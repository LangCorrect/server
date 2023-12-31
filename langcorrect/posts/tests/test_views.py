from urllib.parse import urlencode

from django.test import RequestFactory, TestCase
from django.urls import reverse

from langcorrect.contributions.models import Contribution
from langcorrect.languages.models import Language, LanguageLevel, LevelChoices
from langcorrect.languages.tests.factories import LanguageFactory
from langcorrect.posts.models import Post, PostVisibility
from langcorrect.posts.tests.factories import PostFactory
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

    # def test_correct_number_of_post_rows(self):
    #     post_data = {
    #         "title": "Test Post",
    #         "text": "This is a test post. I need to make it fifty characters in length.",
    #         "language": self.language.id,
    #         "gender_of_narration": "M",
    #         "permission": "public",
    #     }
    #     request = self.factory.post(reverse("posts:create"), data=post_data)
    #     request.user = self.user
    #     PostCreateView.as_view()(request)
    #     post = Post.objects.first()

    #     # Title + Text = 3
    #     expected_postrow_count = 3
    #     actual_post_row_count = PostRow.objects.filter(post=post).count()
    #     self.assertEqual(expected_postrow_count, actual_post_row_count)


class TestPostListView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.languages = LanguageFactory.create_batch(2)
        PostFactory.create_batch(25, language=cls.languages[0])
        PostFactory.create_batch(25, language=cls.languages[1])
        cls.user = UserFactory()
        LanguageLevel.objects.create(user=cls.user, language=cls.languages[0], level=LevelChoices.NATIVE)

    def setUp(self):
        self.factory = RequestFactory()

    def test_anon_queryset(self):
        """
        Test if qs for anon users returns only posts that are both public and corrected
        """
        response = self.client.get(reverse("posts:list"))
        posts = response.context["object_list"]
        expected_posts = Post.available_objects.filter(permission=PostVisibility.PUBLIC, is_corrected=1)
        self.assertQuerySetEqual(posts, expected_posts)

    def test_auth_queryset(self):
        """
        Test if qs for auth users returns only posts that are written in their native language
        """
        self.client.force_login(self.user)
        response = self.client.get(reverse("posts:list"))
        posts = response.context["object_list"]
        expected_posts = Post.objects.filter(language=self.languages[0])
        self.assertQuerySetEqual(posts, expected_posts)

    def test_anon_user_redirected(self):
        """
        Test if anon users are redirecting in learn and following modes
        """
        params1 = {"mode": "learn"}
        url1 = f"{reverse('posts:list')}?{urlencode(params1)}"
        response1 = self.client.get(url1)
        expected_url1 = f"{reverse('account_login')}?next={url1}"
        self.assertRedirects(response1, expected_url1)

        params2 = {"mode": "following"}
        url2 = f"{reverse('posts:list')}?{urlencode(params2)}"
        response2 = self.client.get(url2)
        expected_url2 = f"{reverse('account_login')}?next={url2}"
        self.assertRedirects(response2, expected_url2)

    def test_auth_user_not_redirected(self):
        """
        Test if auth users are not redirected in learn and following modes
        """
        self.client.force_login(self.user)
        params1 = {"mode": "following"}
        url1 = f"{reverse('posts:list')}?{urlencode(params1)}"
        response1 = self.client.get(url1)
        self.assertEqual(response1.status_code, 200)

        params2 = {"mode": "learn"}
        url2 = f"{reverse('posts:list')}?{urlencode(params2)}"
        response2 = self.client.get(url2)
        self.assertEqual(response2.status_code, 200)

    def test_filter_queryset_by_lang_code(self):
        self.client.force_login(self.user)
        params = {"lang_code": self.languages[0].code}
        url = f"{reverse('posts:list')}?{urlencode(params)}"
        response = self.client.get(url)
        posts = response.context["object_list"]
        expected_posts = Post.available_objects.filter(language=self.languages[0]).order_by("is_corrected", "-created")
        self.assertQuerySetEqual(posts, expected_posts)
