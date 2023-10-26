import json

from django.test import RequestFactory, TestCase
from django.urls import reverse

from langcorrect.languages.models import LevelChoices
from langcorrect.languages.tests.factories import LanguageLevelFactory
from langcorrect.posts.models import Post, PostRow
from langcorrect.posts.tests.factories import PostFactory


class TestPostCorrection(TestCase):
    factory = RequestFactory()

    def perform_correction_request(self, post, corrector, updated_sentence, action):
        post_row = PostRow.objects.filter(post=post).first()

        corrections_data = [
            {
                "sentence_id": post_row.id,
                "corrected_text": updated_sentence,
                "feedback": "",
                "action": action,
            }
        ]

        self.client.force_login(corrector)

        return self.client.post(
            path=reverse("posts:make-corrections", args=(post.slug,)),
            data={"corrections_data": json.dumps(corrections_data)},
        )

    def test_deleting_all_corrections_should_unset_iscorrected(self):
        language_level = LanguageLevelFactory.create(level=LevelChoices.NATIVE)
        language = language_level.language
        post = PostFactory.create(language=language)
        corrector = language_level.user

        self.perform_correction_request(post, corrector, "corrected text", "corrected")
        self.assertEqual(Post.objects.get(slug=post.slug).is_corrected, 1)

        self.perform_correction_request(post, corrector, "", "delete")
        self.assertEqual(Post.objects.get(slug=post.slug).is_corrected, 0)
