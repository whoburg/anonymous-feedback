from django.views import generic
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group, User
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


@login_required
def form_fill(request, pk, rk):
    survey = get_object_or_404(Survey, pk=pk)
    assignments = survey.assignment_set.filter(user=request.user)
    rkuser = get_object_or_404(User, pk=rk)
    if request.method == 'POST':
        userform = RecipientSelectForm(request.POST)
        # todo replace the ugly assert below.
        # the call to is_valid creates userform.cleaned_data
        assert(userform.is_valid())
        recipient = userform.cleaned_data['user']
        forms = [FeedbackModelForm(request.POST,
                                   question=q,
                                   instance=Feedback(recipient=recipient,
                                                     question=q),
                                   prefix=("question%s" % q.id))
                 for q in survey.question_set.all()]
        if all(form.is_valid() for form in forms):
            # do something with the cleaned data
            for form in forms:
                form.save()
            # mark assignment completed, if there was one
            assignment_list = assignments.filter(recipient=recipient)
            if assignment_list:
                assignment, = assignment_list
                assignment.complete = True
                assignment.save()
            return HttpResponseRedirect('surveys/../submitted/')
    else:
        userform = RecipientSelectForm()
        forms = [FeedbackModelForm(question=q,
                                   prefix=("question%s" % q.id))
                 for q in survey.question_set.all()]
    return render(request, 'surveys/form_fill.html',
                  {'forms': forms, 'userform': userform, 'survey': survey,
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
