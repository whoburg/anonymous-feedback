from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import Feedback
from . import gpg


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
        # get public key from self.instance.recipient
        r = "78576A7C19B4891D"
        encrypted_data = gpg.encrypt(data, r)
        if encrypted_data.ok:
            return str(encrypted_data)
        raise ValidationError(_('Encryption failed using keyid %s'),
                              code='invalid')


class RecipientSelectForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all(),
                                  label="Please select a recipient:",
                                  empty_label="")


class SignupForm(UserCreationForm):
    public_key = forms.CharField(
        widget=forms.Textarea,
        help_text='Required. Include the full BEGIN and END flags.')

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'public_key')
