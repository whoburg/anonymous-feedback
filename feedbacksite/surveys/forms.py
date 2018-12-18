from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from .models import Feedback, PublicKey


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


class GPGUserCreationForm(UserCreationForm):
    public_key = forms.CharField(
        widget=forms.Textarea,
        help_text='See instructions below. '
                  'Include the full BEGIN and END flags.',
        label="GPG Public Key")

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'public_key')

    def __init__(self, *args, **kwargs):
        super(GPGUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].help_text = (
            'At least 8 characters, and not easily guessed, such as '
            '"password" or "FCR1".')
        self.fields['password2'].help_text = (
            "Re-enter password, for verification.")

    def clean_public_key(self):
        data = self.cleaned_data['public_key']
        publickey = PublicKey()
        try:
            publickey.import_to_gpg(ascii_key=data)
        except ValueError as err:
            raise ValidationError(_('%s' % err))
        if publickey.fingerprint in (key.fingerprint
                                     for key in PublicKey.objects.all()):
            raise ValidationError(_('This public key already has an account'))
        return publickey

    def save(self, commit=True):
        user = super(GPGUserCreationForm, self).save()
        pk = self.cleaned_data['public_key']
        pk.user = user
        udata = pk.get_user_data()
        user.first_name = udata["first_name"]
        user.last_name = udata["last_name"]
        user.email = udata["email"]
        if commit:
            pk.save()
            user.save()
        return user
