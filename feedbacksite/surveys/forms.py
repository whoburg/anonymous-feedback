from django import forms

from .models import Feedback


class FeedbackModelForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['feedback_text']

    def __init__(self, *args, question, **kwargs):
        self.question = question
        super(FeedbackModelForm, self).__init__(*args, **kwargs)
        self.fields['feedback_text'].label = question.question_text

    def clean_feedback_text(self):
        data = self.cleaned_data['feedback_text']
        return "SIMULATED%sENCRYPTION" % data
