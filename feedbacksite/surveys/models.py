from django.db import models
from django.conf import settings
from django.utils import timezone

from . import gpg


class Survey(models.Model):
    title = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    due_date = models.DateTimeField('date due', null=True)
    results_published = models.BooleanField(default=False,
                                            verbose_name="Publish results")

    def __str__(self):
        return self.title


class Question(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=200)

    def __str__(self):
        return self.question_text


class Feedback(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    feedback_text = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        # first order by question since we'll group results by question
        ordering = ['question', 'feedback_text'] # scrambles output order
        verbose_name_plural = 'Feedback'

    def __str__(self):
        return "Private feedback for %s" % (self.recipient)


class PublicKey(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    fingerprint = models.CharField(max_length=50)

    def __str__(self):
        return self.long_id()

    def long_id(self):
        return self.fingerprint[-16:]

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

    def get_uid(self):
        """Get the UID of the form 'Full Name <email@host.domain>'"""
        if not self.fingerprint:
            return ''
        keys, = gpg.list_keys(keys=self.fingerprint)
        uid, = keys["uids"]
        return uid

    def get_user_data(self):
        """Return a dict of user data extracted from this key, including:

        first_name (The first word in the UID full name)
        last_name (The rest of the UID full name)
        email
        """
        chunks = self.get_uid().split(" ")
        email = chunks.pop(-1).strip("<>")
        first_name = chunks.pop(0) if chunks else ''
        last_name = " ".join(chunks)
        return {'first_name': first_name,
                'last_name': last_name,
                'email': email}


class Assignment(models.Model):
    """Allow tracking of progress as team fills survey"""
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  on_delete=models.CASCADE,
                                  related_name="assignment_target")
    complete = models.BooleanField(default=False)
