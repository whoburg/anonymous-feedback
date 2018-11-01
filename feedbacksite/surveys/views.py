from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .models import Survey, Question


def index(request):
    latest_survey_list = Survey.objects.order_by('pub_date')[:5]
    context = {'latest_survey_list': latest_survey_list}
    return render(request, 'surveys/index.html', context)

def detail(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    return render(request, 'surveys/detail.html', {'survey': survey})

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

def submitted(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    return render(request, 'surveys/submitted.html', {'survey': survey})
