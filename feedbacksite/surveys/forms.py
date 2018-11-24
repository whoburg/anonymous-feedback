from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

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
        publickey = self.instance.recipient.publickey
        encrypted_data = publickey.encrypt(data, always_trust=True)
        if encrypted_data.ok:
            return str(encrypted_data)
        raise ValidationError(_('Encryption failed:'
                                '%s' % encrypted_data.stderr),
                              code='invalid')


class UserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        fullname = obj.get_full_name()
        return fullname if fullname else obj


class RecipientSelectForm(forms.Form):
    user = UserChoiceField(
        queryset=User.objects.filter(groups__name='Feedback Recipients'),
        label="Please select a recipient:",
        empty_label="")


class SignupForm(UserCreationForm):
    public_key = forms.CharField(
        widget=forms.Textarea,
        help_text='Required. Include the full BEGIN and END flags.')

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'public_key')
