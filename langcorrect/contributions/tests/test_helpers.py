# ruff: noqa: PT009
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from langcorrect.contributions.helpers import update_user_writing_streak
from langcorrect.contributions.models import Contribution
from langcorrect.languages.models import Language
from langcorrect.posts.models import Post
from langcorrect.users.tests.factories import UserFactory


class TestWritingStreaks(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.contribution, _ = Contribution.objects.get_or_create(user=self.user)
        self.en_lang = Language.objects.create(code="en", en_name="English")

    def create_post(self, days_ago):
        Post.objects.create(
            user=self.user,
            created=timezone.now() - timedelta(days=days_ago),
            language=self.en_lang,
        )

    def test_one_day_streak(self):
        """
        Test that the writing streak is set to 1 if a post was made today.
        """
        self.create_post(0)
        update_user_writing_streak(self.user)
        self.contribution.refresh_from_db()
        self.assertEqual(self.contribution.writing_streak, 1)

    def test_two_day_streak(self):
        """
        Test that the writing streak is set to 2 if posts were made today and
        yesterday.
        """
        self.create_post(days_ago=0)
        self.create_post(days_ago=1)
        update_user_writing_streak(self.user)
        self.contribution.refresh_from_db()
        self.assertEqual(self.contribution.writing_streak, 2)

    def test_two_day_streak_multiple_posts(self):
        """
        Test that the writing streak counts the number of days and not the
        number of posts. For example, the streak should be 2 even if multiple
        posts were published on those days.
        """
        self.create_post(days_ago=0)
        self.create_post(days_ago=0)
        self.create_post(days_ago=0)
        self.create_post(days_ago=1)
        self.create_post(days_ago=1)
        self.create_post(days_ago=1)
        update_user_writing_streak(self.user)
        self.contribution.refresh_from_db()
        self.assertEqual(self.contribution.writing_streak, 2)

    def test_zero_day_streak(self):
        """
        Test that the writing streak is set to 0 if the last post was made more
        than one day ago.
        """
        self.create_post(days_ago=5)
        update_user_writing_streak(self.user)
        self.contribution.refresh_from_db()
        self.assertEqual(self.contribution.writing_streak, 0)

    def test_streak_broken(self):
        """
        Test that the writing streak is set to 1 if a post is made today but
        the previous post was made two days ago, thereby breaking the streak.
        """
        self.create_post(days_ago=0)
        self.create_post(days_ago=2)
        update_user_writing_streak(self.user)
        self.contribution.refresh_from_db()
        self.assertEqual(self.contribution.writing_streak, 1)

    def test_no_posts(self):
        """
        Test that the writing streak is 0 if the user has made no posts.
        """
        update_user_writing_streak(self.user)
        self.contribution.refresh_from_db()
        self.assertEqual(self.contribution.writing_streak, 0)

    def test_long_streak(self):
        """
        Test that a long streak of 30 days is correctly identified.
        """
        thirty_days = 30

        for i in range(thirty_days):
            self.create_post(days_ago=i)
        update_user_writing_streak(self.user)
        self.contribution.refresh_from_db()
        self.assertEqual(self.contribution.writing_streak, thirty_days)
