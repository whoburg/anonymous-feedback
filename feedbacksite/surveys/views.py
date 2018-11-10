from django.views import generic
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.forms import formset_factory, modelformset_factory
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Survey, Question, Feedback
from .forms import FeedbackModelForm, RecipientSelectForm, SignupForm


class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'surveys/index.html'
    context_object_name = 'latest_survey_list'
    def get_queryset(self):
        """Return all questions"""
        return Survey.objects.order_by('pub_date')


def form_fill(request, pk):
    survey = get_object_or_404(Survey, pk=pk)
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
            return HttpResponseRedirect('surveys/../submitted/')
    else:
        userform = RecipientSelectForm()
        forms = [FeedbackModelForm(question=q,
                                   prefix=("question%s" % q.id))
                 for q in survey.question_set.all()]
    return render(request, 'surveys/form_fill.html',
            {'forms': forms, 'userform': userform, 'survey': survey})


class SubmittedView(generic.DetailView):
    model = Survey
    template_name = 'surveys/submitted.html'


class ResultsView(LoginRequiredMixin, generic.ListView):
    template_name = 'surveys/results.html'
    def get_queryset(self):
        """Return feedback for this user"""
        survey = get_object_or_404(Survey, pk=self.kwargs['pk'])
        questions = survey.question_set.all()
        return Feedback.objects.filter(recipient=self.request.user,
                                       question__in=questions)


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.publickey.key = form.cleaned_data.get('public_key')
            user.publickey.import_to_gpg()
            user.save()
            return redirect('../../accounts/login/?newuser=%s' %
                            user.get_username())
    else:
        form = SignupForm()
    return render(request, 'surveys/signup.html', {'form': form})
