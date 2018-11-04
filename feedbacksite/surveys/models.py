from django.db import models
from django.contrib.auth.models import User


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
    recipient = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    feedback_text = models.TextField()
    # created_date = models.DateTimeField(default=timezone.now)

    class Meta:
        # scrambles output order
        ordering = ['feedback_text']

    def __str__(self):
        return "Private feedback for %s" % (self.recipient)
