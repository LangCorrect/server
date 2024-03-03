from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from langcorrect.posts.models import Post
from langcorrect.posts.models import PostVisibility
from langcorrect.users.tests.factories import UserFactory

User = get_user_model()


class TestPostViewSet(APITestCase):
    fixtures = ["fixtures/tests/languages.json"]

    def setUp(self) -> None:
        self.daniel = UserFactory.create(
            studying_languages=["ja", "ko"],
            native_languages=["en", "de"],
        )
        self.masato = UserFactory.create(
            studying_languages=["en", "ko"],
            native_languages=["ja"],
        )
        self.cadence = UserFactory.create(
            studying_languages=["es", "de"],
            native_languages=["fr"],
        )

    def test_get_queryset_anonymous_user(self):
        """Test that an anon user can only see public and corrected posts."""

        Post.objects.create(
            title="Test Post 1",
            permission=PostVisibility.PUBLIC,
            is_corrected=True,
            user=self.daniel,
            language=self.daniel.studying_languages.first(),
        )
        Post.objects.create(
            title="Test Post 2",
            permission=PostVisibility.PUBLIC,
            is_corrected=True,
            user=self.masato,
            language=self.masato.studying_languages.first(),
        )
        Post.objects.create(
            title="Test Post 4",
            permission=PostVisibility.MEMBER,
            is_corrected=True,
            user=self.cadence,
            language=self.cadence.studying_languages.first(),
        )
        Post.objects.create(
            title="Test Post 3",
            permission=PostVisibility.PUBLIC,
            is_corrected=False,
            user=self.masato,
            language=self.masato.studying_languages.first(),
        )

        expected_results_count = 2

        url = reverse("api:post-list")
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == expected_results_count
        assert response.data["results"][0]["title"] == "Test Post 2"

    def test_get_queryset_authenticated_user(self):
        """Test that auth users can only see posts in their native languages."""

        Post.objects.create(
            title="Test Post 1",
            permission=PostVisibility.PUBLIC,
            is_corrected=True,
            user=self.masato,
            language=self.masato.studying_languages.get(code="en"),
        )

        # These posts should not be returned
        Post.objects.create(
            title="Test Post 2",
            permission=PostVisibility.PUBLIC,
            is_corrected=True,
            user=self.daniel,
            language=self.daniel.studying_languages.first(),
        )
        Post.objects.create(
            title="Test Post 3",
            permission=PostVisibility.PUBLIC,
            is_corrected=True,
            user=self.cadence,
            language=self.cadence.studying_languages.get(code="es"),
        )

        expected_results_count = 1

        self.client.force_authenticate(user=self.daniel)
        url = reverse("api:post-list")
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == expected_results_count
        assert response.data["results"][0]["title"] == "Test Post 1"

        # Check that the language of the posts is in the user's native languages
        for post in response.data["results"]:
            assert post["language"]["code"] in self.daniel.native_languages.values_list(
                "code",
                flat=True,
            )

    def test_get_queryset_search(self):
        """Test that the search query parameter works."""

        Post.objects.create(
            title="Test Post 1",
            user=self.masato,
            language=self.masato.studying_languages.get(code="ko"),
        )
        Post.objects.create(
            title="Test Post 2",
            user=self.masato,
            language=self.masato.studying_languages.get(code="en"),
        )
        Post.objects.create(
            title="Test Post 3",
            user=self.cadence,
            language=self.cadence.studying_languages.get(code="de"),
        )

        expected_results_count = 1

        self.client.force_authenticate(user=self.daniel)
        url = reverse("api:post-list")
        response = self.client.get(url, {"search": "3"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == expected_results_count
        assert response.data["results"][0]["title"] == "Test Post 3"

    def test_get_queryset_langs(self):
        """Test that the langs query parameter works."""

        Post.objects.create(
            title="Test Post 1",
            user=self.masato,
            language=self.masato.studying_languages.get(code="ko"),
        )
        Post.objects.create(
            title="Test Post 2",
            user=self.masato,
            language=self.masato.studying_languages.get(code="en"),
        )
        Post.objects.create(
            title="Test Post 3",
            user=self.cadence,
            language=self.cadence.studying_languages.get(code="de"),
        )

        expected_results_count = 1
        self.client.force_authenticate(user=self.daniel)
        url = reverse("api:post-list")
        response = self.client.get(url, {"langs": "en"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == expected_results_count
        assert response.data["results"][0]["title"] == "Test Post 2"

        expected_results_count = 2
        response = self.client.get(url, {"langs": "en,de"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == expected_results_count
        assert response.data["results"][0]["title"] == "Test Post 3"
        assert response.data["results"][1]["title"] == "Test Post 2"
