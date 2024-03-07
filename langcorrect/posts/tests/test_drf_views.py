from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from langcorrect.languages.models import LevelChoices
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
        self.staff = UserFactory.create(
            studying_languages=["ja", "ko"],
            native_languages=["en", "de"],
            is_staff=True,
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

        url = reverse("api:post-list-list")
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
        url = reverse("api:post-list-list")
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
        url = reverse("api:post-list-list")
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
        url = reverse("api:post-list-list")
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

    def test_anon_user_can_view_public_posts(self):
        """Test that an anon user can view public posts."""

        post = Post.objects.create(
            title="Test Post 1",
            permission=PostVisibility.PUBLIC,
            user=self.daniel,
            language=self.daniel.studying_languages.first(),
        )

        url = reverse("api:post-detail-detail", kwargs={"slug": post.slug})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Test Post 1"

    def test_anon_user_cannot_view_member_posts(self):
        """Test that an anon user cannot view member posts."""

        post = Post.objects.create(
            title="Test Post 1",
            permission=PostVisibility.MEMBER,
            user=self.daniel,
            language=self.daniel.studying_languages.first(),
        )

        url = reverse("api:post-detail-detail", kwargs={"slug": post.slug})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_auth_user_can_view_public_post(self):
        """Test that an auth user can view public posts."""

        post = Post.objects.create(
            title="Test Post 1",
            permission=PostVisibility.PUBLIC,
            user=self.daniel,
            language=self.daniel.studying_languages.first(),
        )

        self.client.force_authenticate(user=self.masato)
        url = reverse("api:post-detail-detail", kwargs={"slug": post.slug})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Test Post 1"

    def test_auth_user_can_view_member_post(self):
        """Test that an auth user can view member posts."""

        post = Post.objects.create(
            title="Test Post 1",
            permission=PostVisibility.MEMBER,
            user=self.daniel,
            language=self.daniel.studying_languages.first(),
        )

        self.client.force_authenticate(user=self.masato)
        url = reverse("api:post-detail-detail", kwargs={"slug": post.slug})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Test Post 1"

    def test_non_owner_cannot_delete_post(self):
        """Test that a user who does not own the post cannot delete it."""

        post = Post.objects.create(
            title="Test Post 1",
            permission=PostVisibility.MEMBER,
            user=self.daniel,
            language=self.daniel.studying_languages.first(),
        )

        self.client.force_authenticate(user=self.masato)
        url = reverse("api:post-detail-detail", kwargs={"slug": post.slug})
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_owner_can_delete_post(self):
        """Test that the owner of the post can delete it."""

        post = Post.objects.create(
            title="Test Post 1",
            permission=PostVisibility.MEMBER,
            user=self.daniel,
            language=self.daniel.studying_languages.first(),
        )

        self.client.force_authenticate(user=self.daniel)
        url = reverse("api:post-detail-detail", kwargs={"slug": post.slug})
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_staff_can_delete_post(self):
        """Test that a staff member can delete the post."""

        post = Post.objects.create(
            title="Test Post 1",
            permission=PostVisibility.MEMBER,
            user=self.daniel,
            language=self.daniel.studying_languages.first(),
        )

        self.client.force_authenticate(user=self.staff)
        url = reverse("api:post-detail-detail", kwargs={"slug": post.slug})
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_non_owner_cannot_update_post(self):
        """Test that a user who does not own the post cannot update it."""

        post = Post.objects.create(
            title="Test Post 1",
            permission=PostVisibility.MEMBER,
            user=self.daniel,
            language=self.daniel.studying_languages.first(),
        )

        self.client.force_authenticate(user=self.masato)
        url = reverse("api:post-detail-detail", kwargs={"slug": post.slug})
        response = self.client.patch(url, {"title": "New Title"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_owner_can_edit_post(self):
        """Test that the owner of the post can edit it."""

        post = Post.objects.create(
            title="Test Post 1",
            permission=PostVisibility.MEMBER,
            user=self.daniel,
            language=self.daniel.studying_languages.first(),
        )

        self.client.force_authenticate(user=self.daniel)
        url = reverse("api:post-detail-detail", kwargs={"slug": post.slug})
        response = self.client.patch(url, {"title": "New Title"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "New Title"

    def test_staff_can_edit_post(self):
        """Test that a staff member can edit the post."""

        post = Post.objects.create(
            title="Test Post 1",
            permission=PostVisibility.MEMBER,
            user=self.daniel,
            language=self.daniel.studying_languages.first(),
        )

        self.client.force_authenticate(user=self.staff)
        url = reverse("api:post-detail-detail", kwargs={"slug": post.slug})
        response = self.client.patch(url, {"title": "New Title"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "New Title"

    def test_non_owner_cannot_put_post(self):
        """Test that a user who does not own the post cannot replace it."""

        post = Post.objects.create(
            title="Test Post 1",
            permission=PostVisibility.MEMBER,
            user=self.daniel,
            language=self.daniel.studying_languages.first(),
        )

        self.client.force_authenticate(user=self.masato)
        url = reverse("api:post-detail-detail", kwargs={"slug": post.slug})
        response = self.client.put(url, {"title": "New Title", "text": "New Text"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_slug_not_editable(self):
        """Test that the post slug cannot be edited."""

        post = Post.objects.create(
            title="Test Post 1",
            permission=PostVisibility.MEMBER,
            user=self.daniel,
            language=self.daniel.studying_languages.first(),
        )

        self.client.force_authenticate(user=self.daniel)
        url = reverse("api:post-detail-detail", kwargs={"slug": post.slug})
        response = self.client.patch(url, {"slug": "new-slug"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["slug"] != "new-slug"

    def test_is_corrected_not_editable(self):
        """Test that the 'is_corrected' field cannot be edited."""

        post = Post.objects.create(
            title="Test Post 1",
            permission=PostVisibility.MEMBER,
            user=self.daniel,
            language=self.daniel.studying_languages.first(),
            is_corrected=False,
        )

        self.client.force_authenticate(user=self.daniel)
        url = reverse("api:post-detail-detail", kwargs={"slug": post.slug})
        response = self.client.patch(url, {"is_corrected": True})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_corrected"] is False

    def test_language_level_not_editable(self):
        """Test that the 'language_level' field cannot be edited."""

        post = Post.objects.create(
            title="Test Post 1",
            permission=PostVisibility.MEMBER,
            user=self.daniel,
            language=self.daniel.studying_languages.first(),
            language_level=LevelChoices.A1,
        )

        self.client.force_authenticate(user=self.daniel)
        url = reverse("api:post-detail-detail", kwargs={"slug": post.slug})
        response = self.client.patch(url, {"language_level": LevelChoices.C1})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["language_level"] == LevelChoices.A1
