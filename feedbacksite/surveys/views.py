from django.views import generic
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.forms import formset_factory, modelformset_factory

from .models import Survey, Question, Feedback
from .forms import FeedbackForm, FeedbackModelForm


class IndexView(generic.ListView):
    template_name = 'surveys/index.html'
    context_object_name = 'latest_survey_list'
    def get_queryset(self):
        """Return all questions"""
        return Survey.objects.order_by('pub_date')[:]


class FeedbackCreate(generic.edit.CreateView):
    model = Feedback
    fields = '__all__'
    template_name = 'surveys/fill.html'


def form_fill(request, pk):
    survey = get_object_or_404(Survey, pk=pk)
#    if request.method == 'POST':
#        form = FeedbackForm(request.POST)
#        if form.is_valid():
#            # process the data in form.cleaned_data as required
#            # ...
#            # redirect to a new URL:
#            return HttpResponseRedirect('surveys/../submitted/')
#    else:
#        form = FeedbackForm()
    if request.method == 'POST':
        forms = [FeedbackModelForm(request.POST,
                                   question=q,
                                   instance=Feedback(recipient=request.user,
                                                     question=q),
                                   prefix=("question%s" % q.id))
                 for q in survey.question_set.all()]
        if all(form.is_valid() for form in forms):
            # do something with the cleaned data
            for form in forms:
                form.save()
            return HttpResponseRedirect('surveys/../submitted/')
    else:
        forms = [FeedbackModelForm(question=q,
                                   prefix=("question%s" % q.id))
                 for q in survey.question_set.all()]
    return render(request, 'surveys/form_fill.html',
            {'forms': forms, 'survey': survey})


def submit_feedback(request, pk):
    survey = get_object_or_404(Survey, pk=pk)
    if request.method == "POST":
        form = FeedbackModelForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.question_id = 2
            feedback.recipient_id = 1
            feedback.save()
            return redirect('../submitted')
    else:
        form = FeedbackModelForm()
    return render(request, 'surveys/submit.html',
                  {'survey': survey, 'form': form})


class SubmittedView(generic.DetailView):
    model = Survey
    template_name = 'surveys/submitted.html'
