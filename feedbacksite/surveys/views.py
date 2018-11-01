from django.http import HttpResponse
from django.shortcuts import render

from .models import Survey


def index(request):
    latest_survey_list = Survey.objects.order_by('pub_date')[:5]
    context = {'latest_survey_list': latest_survey_list}
    return render(request, 'surveys/index.html', context)

def detail(request, survey_id):
    return HttpResponse("You're looking at survey %s." % survey_id)
