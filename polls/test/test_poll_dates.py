import datetime

from django.test import TestCase
from django.utils import timezone
from polls.models import Question


class QuestionModelTests(TestCase):
    """Condition that publish with different question."""
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


class TestModels(TestCase):
    """Test models"""
    def test_published(self):
        """Check this is push already"""
        time = timezone.now() - datetime.timedelta(days=1)
        question = Question(pub_date=time)
        self.assertTrue(question.is_published())

    def test_can_vote(self):
        """ฺBefore close time, it should votable"""
        time_open = timezone.now() - datetime.timedelta(days=1)
        time_close = timezone.now() + datetime.timedelta(days=1)
        question = Question(pub_date=time_open, end_date=time_close)
        self.assertTrue(question.can_vote())