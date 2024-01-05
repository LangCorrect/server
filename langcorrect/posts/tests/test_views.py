from unittest.mock import patch
from urllib.parse import urlencode

from django.test import TestCase
from django.urls import reverse

from langcorrect.contributions.models import Contribution
from langcorrect.languages.models import Language
from langcorrect.posts.models import Post, PostRow, PostVisibility
from langcorrect.posts.tests.factories import LANGUAGE_TO_FAKER_LOCALE, PostFactory
from langcorrect.posts.tests.utils import generate_text, generate_title
from langcorrect.users.tests.factories import UserFactory


class TestPostCreateView(TestCase):
    fixtures = ["fixtures/tests/languages.json"]

    @classmethod
    def setUpTestData(cls):
        cls.user1 = UserFactory(native_languages=["ja"], studying_languages=["en"])

    def submit_form(self, form_data):
        return self.client.post(reverse("posts:create"), form_data)

    def build_form_payload(self, title=None, text=None, language_id=None):
        all_studying_languages = self.user1.studying_languages
        target_language = all_studying_languages.first()

        faker_locale = LANGUAGE_TO_FAKER_LOCALE.get(target_language.code)

        data = {
            "title": title if title else generate_title(faker_locale),
            "text": text if text else generate_text(faker_locale),
            "language": language_id if language_id else target_language.id,
            "gender_of_narration": "M",
            "permission": "public",
        }
        return data

    @patch("langcorrect.posts.views.check_can_create_post")
    def test_can_access_page_good_ratio(self, mock_check_can_create_post):
        mock_check_can_create_post.return_value = True

        self.client.force_login(self.user1)

        response = self.client.get(reverse("posts:create"))
        self.assertEqual(response.status_code, 200)

    @patch("langcorrect.posts.views.check_can_create_post")
    def test_cannot_access_page_bad_ratio(self, mock_check_can_create_post):
        mock_check_can_create_post.return_value = False

        self.client.force_login(self.user1)

        response = self.client.get(reverse("posts:create"))
        self.assertEqual(response.status_code, 403)

    def test_cannot_access_page_anonymous_user(self):
        response = self.client.get(reverse("posts:create"))
        url = "/accounts/login/?next=/journals/~create/"
        self.assertEqual(response.url, url)
        self.assertEqual(response.status_code, 302)

    def test_create_post(self):
        self.client.force_login(self.user1)

        data = self.build_form_payload(title="A Title")
        response = self.submit_form(data)

        url = "/journals/a-title/"
        self.assertEqual(url, response.url)
        self.assertEqual(response.status_code, 302)

    def test_streak_updates(self):
        self.client.force_login(self.user1)

        data = self.build_form_payload()
        self.submit_form(data)

        self.user1.refresh_from_db()
        contribution = Contribution.objects.get(user=self.user1)
        assert contribution.writing_streak == 1

    def test_correct_number_of_post_rows_generated(self):
        self.client.force_login(self.user1)
        english = Language.objects.get(code="en")

        data = self.build_form_payload(
            title="This is a title",
            text="This is a sentence. This is another sentence. This is patrick.",
            language_id=english.id,
        )
        self.submit_form(data)

        post = self.user1.post_set.first()

        expected_count = 4
        actual_count = post.postrow_set.count()
        self.assertEqual(expected_count, actual_count)


class TestPostUpdateView(TestCase):
    fixtures = ["fixtures/tests/languages.json"]

    @classmethod
    def setUpTestData(cls):
        sample_text = """
            Source girl reach exactly.
            Away situation like season specific.
            Fund prove bill need through factor participant.
            Too knowledge long black sit must two.
        """
        title = "Testing is hard"

        cls.user1 = UserFactory(native_languages=["ja"], studying_languages=["en"])
        cls.post = PostFactory(
            user=cls.user1,
            title=title,
            text=sample_text,
            is_corrected=False,
            set_language="en",
        )

    def submit_form(self, form_data):
        return self.client.post(reverse("posts:update", kwargs={"slug": self.post.slug}), form_data, follow=True)

    def build_form_payload(self, title=None, text=None, language_id=None):
        all_studying_languages = self.user1.studying_languages
        target_language = all_studying_languages.first()

        faker_locale = LANGUAGE_TO_FAKER_LOCALE.get(target_language.code)

        data = {
            "title": title if title else generate_title(faker_locale),
            "text": text if text else generate_text(faker_locale),
            "language": language_id if language_id else target_language.id,
            "gender_of_narration": "M",
            "permission": "public",
        }
        return data

    def test_no_additional_rows_created(self):
        self.client.force_login(self.user1)
        data = self.build_form_payload(
            title=self.post.title,
            text=self.post.text,
            language_id=self.post.language.id,
        )
        response = self.submit_form(data)

        actual_post_row_count = response.context["object"].postrow_set.count()

        # title + post text
        expected_count = 5
        self.assertEqual(expected_count, actual_post_row_count)

    def test_sentence_appended(self):
        self.client.force_login(self.user1)
        data = self.build_form_payload(
            title=self.post.title,
            text=self.post.text + "This is an additional sentence.",
            language_id=self.post.language.id,
        )
        response = self.submit_form(data)
        actual_post_row_count = response.context["object"].postrow_set.count()

        # title + post text + added sentence
        expected_count = 6
        self.assertEqual(expected_count, actual_post_row_count)

    def test_sentence_prepended(self):
        self.client.force_login(self.user1)
        data = self.build_form_payload(
            title=self.post.title,
            text="This is an additional sentence." + self.post.text,
            language_id=self.post.language.id,
        )
        response = self.submit_form(data)
        actual_post_row_count = response.context["object"].postrow_set.count()

        # title + post text + added sentence
        expected_count = 6
        self.assertEqual(expected_count, actual_post_row_count)

    def test_sentences_mixed(self):
        updated_text = """
            This is Bob.
            Source girl reach exactly.
            This is Mike.
            Away situation like season specific.
            Too knowledge long black sit must two.
        """

        self.client.force_login(self.user1)
        data = self.build_form_payload(
            title=self.post.title,
            text=updated_text,
            language_id=self.post.language.id,
        )
        self.submit_form(data)
        actual_post_row_count = PostRow.available_objects.filter(post=self.post, is_actual=True).count()

        expected_count = 6
        self.assertEqual(expected_count, actual_post_row_count)

        hidden_rows_count = PostRow.available_objects.filter(post=self.post, is_actual=False).count()
        self.assertEqual(1, hidden_rows_count)


class TestPostListView(TestCase):
    fixtures = ["fixtures/tests/languages.json"]

    @classmethod
    def generate_posts_by_code(cls, lang_code, is_corrected, permission, amount):
        PostFactory.create_batch(amount, is_corrected=is_corrected, permission=permission, set_language=lang_code)

    @classmethod
    def setUpTestData(cls):
        cls.en_ja_user = UserFactory(native_languages=["en"], studying_languages=["ja"])
        cls.enko_ja_user = UserFactory(native_languages=["en", "ko"], studying_languages=["ja"])

        UserFactory.create_batch(5)

        cls.generate_posts_by_code("en", True, PostVisibility.PUBLIC, 10)
        cls.generate_posts_by_code("en", True, PostVisibility.MEMBER, 10)
        cls.generate_posts_by_code("ja", False, PostVisibility.MEMBER, 5)
        cls.generate_posts_by_code("ja", True, PostVisibility.PUBLIC, 5)
        cls.generate_posts_by_code("ko", False, PostVisibility.MEMBER, 2)
        cls.generate_posts_by_code("ko", True, PostVisibility.PUBLIC, 3)

    def test_anonymous_queryset(self):
        response = self.client.get(reverse("posts:list"))
        posts = response.context["object_list"]
        expected_posts = Post.available_objects.filter(permission=PostVisibility.PUBLIC, is_corrected=1)
        self.assertQuerySetEqual(posts, expected_posts)

    def test_authenticated_queryset(self):
        """
        Check that logged in user will see posts written in their native languages.
        """
        self.client.force_login(self.en_ja_user)
        response = self.client.get(reverse("posts:list"))
        posts = response.context["object_list"]
        english = Language.objects.get(code="en")
        expected_posts = Post.available_objects.filter(language=english)
        self.assertQuerySetEqual(posts, expected_posts)

    def test_anonymous_redirected_in_learn_mode(self):
        params = {"mode": "learn"}
        url = f"{reverse('posts:list')}?{urlencode(params)}"
        response = self.client.get(url)
        expected_url = f"{reverse('account_login')}?next={url}"
        self.assertRedirects(response, expected_url)

    def test_anonymous_redirected_in_following_mode(self):
        params = {"mode": "following"}
        url = f"{reverse('posts:list')}?{urlencode(params)}"
        response = self.client.get(url)
        expected_url = f"{reverse('account_login')}?next={url}"
        self.assertRedirects(response, expected_url)

    def test_can_access_learn_mode_auth_user(self):
        self.client.force_login(self.en_ja_user)
        params = {"mode": "learn"}
        url = f"{reverse('posts:list')}?{urlencode(params)}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_can_access_following_mode_auth_user(self):
        self.client.force_login(self.en_ja_user)
        params = {"mode": "following"}
        url = f"{reverse('posts:list')}?{urlencode(params)}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_filter_queryset_by_language_code(self):
        self.client.force_login(self.enko_ja_user)
        korean_code = "ko"
        params = {"lang_code": korean_code}
        url = f"{reverse('posts:list')}?{urlencode(params)}"
        response = self.client.get(url)
        posts = response.context["object_list"]
        expected_posts = Post.available_objects.filter(language__code=korean_code).order_by("is_corrected", "-created")
        self.assertQuerySetEqual(posts, expected_posts)
