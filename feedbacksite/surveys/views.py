from django.views import generic

from .models import Survey, Question, Feedback


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


class SubmittedView(generic.DetailView):
    model = Survey
    template_name = 'surveys/submitted.html'
