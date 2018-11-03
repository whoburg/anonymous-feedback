from django.views import generic
from django.shortcuts import render, get_object_or_404, redirect

from .models import Survey, Question, Feedback
from .forms import FeedbackForm


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
    return render(request, 'surveys/form_fill.html',
                  {'current_name': "George"})


def submit_feedback(request, pk):
    survey = get_object_or_404(Survey, pk=pk)
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.question_id = 2
            feedback.recipient_id = 1
            feedback.save()
            return redirect('../submitted')
    else:
        form = FeedbackForm()
    return render(request, 'surveys/submit.html',
                  {'survey': survey, 'form': form})


class SubmittedView(generic.DetailView):
    model = Survey
    template_name = 'surveys/submitted.html'
