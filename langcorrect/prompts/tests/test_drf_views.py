from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from langcorrect.challenges.models import Challenge
from langcorrect.prompts.models import Prompt
from langcorrect.users.tests.factories import UserFactory


class PromptListCreateAPIViewTestCase(APITestCase):
    fixtures = ["fixtures/tests/languages.json"]

    def setUp(self):
        self.daniel = UserFactory.create(
            studying_languages=["ja", "ko"],
            native_languages=["en", "de"],
        )
        self.staff = UserFactory.create(
            studying_languages=["ja", "ko"],
            native_languages=["en", "de"],
            is_staff=True,
        )
        self.url = reverse("prompt-list-create")

    def test_create_prompt_valid_language(self):
        """
        Test that a prompt can be created in a user related language.
        """
        data = {
            "content": "This is a prompt",
            "lang_code": "en",
        }
        self.client.force_authenticate(self.daniel)
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Prompt.objects.count() == 1

    def test_create_prompt_invalid_language(self):
        """
        Test that a prompt cannot be created in a user unrelated language.
        """
        data = {
            "content": "This is a prompt",
            "lang_code": "es",
        }
        self.client.force_authenticate(self.daniel)
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Prompt.objects.count() == 0

    def test_create_prompt_anon_user(self):
        """
        Test that an anonymous user cannot create a prompt.
        """
        data = {
            "content": "This is a prompt",
            "lang_code": "en",
        }
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Prompt.objects.count() == 0

    def test_list_prompts(self):
        """
        Test that a list of prompts can be retrieved.
        """
        self.client.force_authenticate(self.daniel)
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_list_prompts_anon_user(self):
        """
        Test that an anonymous user cannot retrieve a list of prompts.
        """
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_prompts_search(self):
        """
        Test that a list of prompts can be filtered by search.
        """
        self.client.force_authenticate(self.daniel)
        response = self.client.get(self.url, {"search": "prompt"})
        assert response.status_code == status.HTTP_200_OK

    def test_list_prompts_langs(self):
        """
        Test that a list of prompts can be filtered by language.
        """
        self.client.force_authenticate(self.daniel)
        data = {
            "content": "This is a prompt",
            "lang_code": "en",
        }
        self.client.post(self.url, data)

        data = {
            "content": "This is a prompt 2",
            "lang_code": "de",
        }
        self.client.post(self.url, data)

        response = self.client.get(self.url, {"langs": "en"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

        response = self.client.get(self.url, {"langs": "en,de"})
        expected_results = 2
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == expected_results

    def test_normal_user_cannot_attach_challenge(self):
        """
        Test that a normal user cannot attach a challenge to a prompt.
        """
        self.client.force_authenticate(self.daniel)
        challenge = Challenge.objects.create(
            title="Test Challenge",
            description="Test Challenge Description",
            slug="test-challenge",
        )
        data = {
            "content": "This is a prompt",
            "lang_code": "en",
            "challenge": challenge.pk,
        }
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_staff_user_can_attach_challenge(self):
        """
        Test that a staff user can attach a challenge to a prompt.
        """
        self.client.force_authenticate(self.staff)
        challenge = Challenge.objects.create(
            title="Test Challenge",
            description="Test Challenge Description",
            slug="test-challenge",
        )
        data = {
            "content": "This is a prompt",
            "lang_code": "en",
            "challenge": challenge.pk,
        }
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_201_CREATED


class PromptRetrieveUpdateDestroyAPIViewTestCase(APITestCase):
    fixtures = ["fixtures/tests/languages.json"]

    def setUp(self):
        self.daniel = UserFactory.create(
            studying_languages=["ja", "ko"],
            native_languages=["en", "de"],
        )
        self.mike = UserFactory.create(
            studying_languages=["ja"],
            native_languages=["de"],
        )
        self.staff = UserFactory.create(
            studying_languages=["ja", "ko"],
            native_languages=["en", "de"],
            is_staff=True,
        )
        self.prompt_daniel = Prompt.objects.create(
            content="This is a prompt",
            language=self.daniel.studying_languages.get(code="ja"),
            user=self.daniel,
        )
        self.prompt_daniel_url = reverse(
            "prompt-retrieve-update-destroy",
            kwargs={"slug": self.prompt_daniel.slug},
        )

    def test_anon_user_cannot_view_prompt(self):
        """
        Test that an anonymous user cannot view a prompt.
        """
        response = self.client.get(self.prompt_daniel_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_auth_user_can_view_prompt(self):
        """
        Test that an authenticated user can view a prompt.
        """
        self.client.force_authenticate(self.mike)
        response = self.client.get(self.prompt_daniel_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["content"] == "This is a prompt"

    def test_anon_cannot_update_prompt(self):
        """
        Test that an anonymous user cannot update a prompt.
        """
        data = {
            "content": "This is an updated prompt",
            "lang_code": "de",
        }
        response = self.client.patch(self.prompt_daniel_url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_non_owner_cannot_update_prompt(self):
        """
        Test that a non-owner user cannot update a prompt.
        """
        data = {
            "content": "This is an updated prompt",
            "lang_code": "de",
        }
        self.client.force_authenticate(self.mike)
        response = self.client.patch(self.prompt_daniel_url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_owner_can_update_prompt(self):
        """
        Test that an owner user can update a prompt.
        """
        data = {
            "content": "This is an updated prompt",
            "lang_code": "de",
        }
        self.client.force_authenticate(self.daniel)
        response = self.client.patch(self.prompt_daniel_url, data)
        assert response.status_code == status.HTTP_200_OK
        self.prompt_daniel.refresh_from_db()
        assert self.prompt_daniel.content == "This is an updated prompt"
        assert self.prompt_daniel.language.code == "de"

    def test_staff_can_update_prompt(self):
        """
        Test that a staff user can update a prompt.
        """
        data = {
            "content": "This is an updated prompt 2",
            "lang_code": "es",
        }
        self.client.force_authenticate(self.staff)
        response = self.client.patch(self.prompt_daniel_url, data)
        assert response.status_code == status.HTTP_200_OK
        self.prompt_daniel.refresh_from_db()
        assert self.prompt_daniel.content == "This is an updated prompt 2"
        assert self.prompt_daniel.language.code == "es"

    def test_anon_cannot_delete_prompt(self):
        """
        Test that an anonymous user cannot delete a prompt.
        """
        response = self.client.delete(self.prompt_daniel_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_non_owner_cannot_delete_prompt(self):
        """
        Test that a non-owner user cannot delete a prompt.
        """
        self.client.force_authenticate(self.mike)
        response = self.client.delete(self.prompt_daniel_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_owner_can_delete_prompt(self):
        """
        Test that an owner user can delete a prompt.
        """
        self.client.force_authenticate(self.daniel)
        response = self.client.delete(self.prompt_daniel_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Prompt.objects.count() == 0

    def test_staff_can_delete_prompt(self):
        """
        Test that a staff user can delete a prompt.
        """
        self.client.force_authenticate(self.staff)
        response = self.client.delete(self.prompt_daniel_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Prompt.objects.count() == 0
