from django.views import generic
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group, User
from django.urls import reverse
from django.utils import timezone

from .models import Survey, Feedback
from .forms import FeedbackModelForm, RecipientSelectForm, GPGUserCreationForm


class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'surveys/index.html'

    def get_queryset(self):
        """Return published Surveys"""
        now = timezone.now()
        return Survey.objects.filter(pub_date__lt=now).order_by('pub_date')


class DetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'surveys/detail.html'
    model = Survey

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        survey = self.get_object()
        assignments = survey.assignment_set.filter(user=self.request.user)
        context['assignments'] = assignments
        valid_recips = Group.objects.get(name="Feedback Recipients")
        context['optionals'] = valid_recips.user_set.exclude(
            pk__in=(a.recipient.pk for a in assignments)).exclude(
            pk=self.request.user.pk)
        context['survey_complete'] = all(a.complete for a in assignments)
        return context


@login_required
def form_fill(request, pk, rk):
    survey = get_object_or_404(Survey, pk=pk)
    assignments = survey.assignment_set.filter(user=request.user)
    rkuser = get_object_or_404(User, pk=rk)
    if request.method == 'POST':
        forms = [FeedbackModelForm(request.POST,
                                   question=q,
                                   instance=Feedback(recipient=rkuser,
                                                     question=q),
                                   prefix=("question%s" % q.id))
                 for q in survey.question_set.all()]
        if all(form.is_valid() for form in forms):
            # do something with the cleaned data
            for form in forms:
                form.save()
            # mark assignment completed, if there was one
            assignment_list = assignments.filter(recipient=rkuser)
            if assignment_list:
                assignment, = assignment_list
                assignment.complete = True
                assignment.save()
            return HttpResponseRedirect(reverse("surveys:submitted",
                                                args=(survey.pk,)))
    else:
        forms = [FeedbackModelForm(question=q,
                                   prefix=("question%s" % q.id))
                 for q in survey.question_set.all()]
    return render(request, 'surveys/form_fill.html',
                  {'forms': forms, 'survey': survey,
                   'assignments': assignments, 'rkuser': rkuser})


class SubmittedView(generic.DetailView):
    model = Survey
    template_name = 'surveys/submitted.html'


class ResultsView(LoginRequiredMixin, generic.ListView):

    template_name = 'surveys/results.html'

    def get_queryset(self):
        """Return feedback for this user"""
        survey = get_object_or_404(Survey, pk=self.kwargs['pk'])
        if not survey.results_published:
            return Feedback.objects.none()
        questions = survey.question_set.all()
        return Feedback.objects.filter(recipient=self.request.user,
                                       question__in=questions)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['survey'] = get_object_or_404(Survey, pk=self.kwargs['pk'])
        return context


def signup(request):

    if request.method == 'POST':
        form = GPGUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # add users to default groups
            recpnts = Group.objects.get_or_create(name="Feedback Recipients")[0]
            authors = Group.objects.get_or_create(name="Feedback Authors")[0]
            user.groups.add(recpnts)
            user.groups.add(authors)
            user.save()
            return redirect('../../accounts/login/?newuser=%s' %
                            user.get_username())
    else:
        form = GPGUserCreationForm()
    return render(request, 'surveys/signup.html', {'form': form})

def faq(request):
    return render(request, 'surveys/faq.html')
