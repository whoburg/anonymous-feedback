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


class FeedbackForm(forms.Form):
    your_feedback = forms.CharField(label='Your feedback', max_length=100)
