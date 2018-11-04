from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


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
    key = models.TextField()
    fingerprint = models.CharField(max_length=50)


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        PublicKey.objects.create(user=instance)
    instance.publickey.save()
