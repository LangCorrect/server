import random

from django.contrib.auth import get_user_model
from factory import LazyAttribute
from factory.django import DjangoModelFactory
from faker import Faker

from langcorrect.languages.models import LanguageLevel, LevelChoices
from langcorrect.posts.models import Post
from langcorrect.posts.tests.utils import generate_text
from langcorrect.prompts.models import Prompt

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


class PromptFactory(DjangoModelFactory):
    user = LazyAttribute(lambda _: User.objects.order_by("?").first())
    content = LazyAttribute(lambda x: generate_text(LANGUAGE_TO_FAKER_LOCALE.get(x.language.code), amount=1))
    language = LazyAttribute(
        lambda x: random.choice(LanguageLevel.objects.filter(user=x.user, level=LevelChoices.NATIVE)).language
    )
    slug = LazyAttribute(lambda _: fake.uuid4())

    class Meta:
        model = Prompt
        django_get_or_create = ["slug"]

    @classmethod
    def create_batch(cls, size, **kwargs):
        max_posts = kwargs.pop("max_posts", None)

        instances = super().create_batch(size, **kwargs)

        for instance in instances:
            cls._associate_posts_to_instances(instance, max_posts)

        return instances

    @staticmethod
    def _associate_posts_to_instances(instance, max_posts):
        if max_posts:
            available_posts = Post.objects.filter(language=instance.language).exclude(prompt__isnull=False)

            amount = random.randint(0, min(available_posts.count(), max_posts))
            posts = available_posts.order_by("?")[:amount]

            for post in posts:
                post.prompt = instance

            Post.objects.bulk_update(posts, ["prompt"])
