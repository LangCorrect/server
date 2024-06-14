from django.urls import resolve
from django.urls import reverse
from rest_framework.test import APITestCase

from langcorrect.posts.models import PostVisibility
from langcorrect.posts.tests.factories import PostFactory
from langcorrect.users.tests.factories import UserFactory


class TestPostViewSetUrls(APITestCase):
    fixtures = ["fixtures/tests/languages.json"]

    def setUp(self) -> None:
        self.daniel = UserFactory.create(
            studying_languages=["ja", "ko"],
            native_languages=["en", "de"],
        )
        self.post = PostFactory.create(
            user=self.daniel,
            set_language="ja",
            title="Test Post",
            text="This is a test post",
            permission=PostVisibility.PUBLIC,
        )

    def test_post_list(self) -> None:
        assert reverse("api:post-list-list") == "/api/v1/posts"
        assert resolve("/api/v1/posts").view_name == "api:post-list-list"

    def test_post_detail(self) -> None:
        assert (
            reverse("api:post-detail-detail", kwargs={"slug": self.post.slug})
            == f"/api/v1/posts/{self.post.slug}"
        )
        assert (
            resolve(f"/api/v1/posts/{self.post.slug}").view_name
            == "api:post-detail-detail"
        )
