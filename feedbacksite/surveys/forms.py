from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Feedback

import gnupg
gpg = gnupg.GPG(gnupghome='~/.gnupg/')


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
