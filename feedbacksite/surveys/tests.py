from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User

from .models import Survey, Question, Feedback


class TestResultsView(TestCase):

    def setUp(self):
        # ResultsView requires a logged in user
        self.testuser, flag = User.objects.get_or_create(username='testuser')
        self.assertTrue(flag)
        self.client.force_login(self.testuser)

    def test_no_results(self):
        """"If no results, an appropriate message is displayed"""
        url = reverse('surveys:results', args=(1,))
        response = self.client.get(url)
        self.assertContains(response, "No results are available.")

    def test_results_filtered_by_survey(self):
        """Results page should only show results for given survey"""
        s = Survey.objects.create(survey_text="Test Survey",
                                  pub_date=timezone.now())
        q = Question.objects.create(survey=s, question_text="Q1")
        f = Feedback.objects.create(recipient=self.testuser,
                                    question=q,
                                    feedback_text="meh")
        url = reverse('surveys:results', args=(1,))
        response = self.client.get(url)
        self.assertQuerysetEqual(
            response.context['feedback_list'],
            ['<Feedback: Private feedback for testuser>']
        )
        # now increment the URL pk, there should be no results here
        url = reverse('surveys:results', args=(2,))
        response = self.client.get(url)
        self.assertQuerysetEqual(
            response.context['feedback_list'],
            []
        )
        print(response.content)

    def test_logged_out(self):
        """If user logged out, should get redirected"""
        self.client.logout()
        url = reverse('surveys:results', args=(1,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
