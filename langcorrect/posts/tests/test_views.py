from django.test import RequestFactory, TestCase
from django.urls import reverse

from langcorrect.contributions.models import Contribution
from langcorrect.languages.models import Language, LanguageLevel, LevelChoices
from langcorrect.posts.views import PostCreateView
from langcorrect.users.tests.factories import UserFactory


class TestPostCreateView(TestCase):
    def setUp(self):
        self.user = UserFactory()

        self.language = Language.objects.create(code="en", en_name="English")
        self.studying_language = LanguageLevel.objects.create(
            user=self.user, language=self.language, level=LevelChoices.A1
        )
        self.factory = RequestFactory()

    def test_create_post_and_streak(self):
        post_data = {
            "title": "Test Post",
            "text": "This is a test post and I need to make it fifty characters in length.",
            "language": self.language.id,
            "gender_of_narration": "M",
            "permission": "public",
        }

        request = self.factory.post(reverse("posts:create"), data=post_data)
        request.user = self.user

        response = PostCreateView.as_view()(request)
        assert response.status_code == 302

        self.user.refresh_from_db()
        contribution = Contribution.objects.get(user=self.user)
        assert contribution.writing_streak == 1
