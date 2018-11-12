from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from . import gpg


class Survey(models.Model):
    survey_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.survey_text


class Question(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=200)


class Feedback(models.Model):
    # author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    feedback_text = models.TextField()
    # created_date = models.DateTimeField(default=timezone.now)

    class Meta:
        # scrambles output order
        ordering = ['feedback_text']
        verbose_name_plural = 'Feedback'

    def __str__(self):
        return "Private feedback for %s" % (self.recipient)


class PublicKey(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fingerprint = models.CharField(max_length=50)

    def import_to_gpg(self, ascii_key):
        """Try to import this key into the system gpg.
        Sets self.fingerprint based upon the ascii key text in self.key
        Raises ValueError if the import does not succeed"""
        result = gpg.import_keys(ascii_key)
        if result.count == 0:
            raise ValueError("Unable to import public key")
        if result.count > 1:
            raise ValueError("Multiple keys detected during import")
        self.fingerprint, = result.fingerprints
        return self.fingerprint

    def encrypt(self, text, **kwargs):
        """Encrypt text using this PublicKey; return the encrypted result"""
        return gpg.encrypt(text, self.fingerprint, **kwargs)


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        PublicKey.objects.create(user=instance)
    instance.publickey.save()
