from django.shortcuts import get_object_or_404, render

from .models import Survey


def index(request):
    latest_survey_list = Survey.objects.order_by('pub_date')[:5]
    context = {'latest_survey_list': latest_survey_list}
    return render(request, 'surveys/index.html', context)

def detail(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    return render(request, 'surveys/detail.html', {'survey': survey})
