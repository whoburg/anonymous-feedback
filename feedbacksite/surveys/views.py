from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from .models import Survey, Question


class IndexView(generic.ListView):
    template_name = 'surveys/index.html'
    context_object_name = 'latest_survey_list'
    def get_queryset(self):
        """Return all questions"""
        return Survey.objects.order_by('pub_date')[:]


class DetailView(generic.DetailView):
    model = Survey
    template_name = 'surveys/detail.html'


class SubmittedView(generic.DetailView):
    model = Survey
    template_name = 'surveys/submitted.html'


def submit(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    try:
        selected_question = survey.question_set.get(pk=request.POST['question'])
    except (KeyError, Question.DoesNotExist):
        # Redisplay the survey voting form.
        return render(request, 'surveys/detail.html', {
            'survey': survey,
            'error_message': "You didn't select a question.",
        })
    else:
        selected_question.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('surveys:submitted', args=(survey.id,)))
