from django.contrib.auth import get_user_model
from factory import LazyAttribute, post_generation
from factory.django import DjangoModelFactory
from faker import Faker

from langcorrect.corrections.models import PerfectRow
from langcorrect.posts.models import Post

User = get_user_model()

fake = Faker()

LANGUAGE_TO_FAKER_LOCALE = {
    "en": "en_US",
    "es": "es_ES",
    "fr": "fr_FR",
    "de": "de_DE",
    "ja": "ja_JP",
    "zh-hant": "zh_CN",
    "zh-hans": "zh_CN",
    "ko": "ko_KR",
}


class PerfectRowFactory(DjangoModelFactory):
    user = LazyAttribute(lambda _: User.objects.order_by("?").first())
    post = LazyAttribute(lambda _: Post.objects.order_by("?").first())
    post_row = LazyAttribute(lambda x: x.post.postrow_set.order_by("?").first())

    class Meta:
        model = PerfectRow

    @post_generation
    def mark_post_as_corrected(self, create, extracted, **kwargs):
        if not create:
            return

        post = self.post
        post.is_corrected = True
        post.save()
