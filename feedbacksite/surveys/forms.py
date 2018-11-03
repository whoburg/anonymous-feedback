from django import forms

from .models import Feedback


class FeedbackModelForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['feedback_text']


class FeedbackForm(forms.Form):
    your_feedback = forms.CharField(label='Your feedback', max_length=100)
