from django.views import generic
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.forms import formset_factory

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
    FeedbackFormSet = formset_factory(FeedbackForm, extra=4)
    if request.method == 'POST':
        formset = FeedbackFormSet(request.POST)
        if formset.is_valid():
            # do something with the cleaned data
            return HttpResponseRedirect('surveys/../submitted/')
    else:
        formset = FeedbackFormSet()
    return render(request, 'surveys/form_fill.html',
            {'formset': formset, 'survey': survey})


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
