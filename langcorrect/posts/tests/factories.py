import random

from django.contrib.auth import get_user_model
from factory import LazyAttribute, post_generation
from factory.django import DjangoModelFactory
from faker import Faker

from langcorrect.languages.models import Language, LanguageLevel
from langcorrect.posts.models import Post, PostVisibility
from langcorrect.posts.tests.utils import generate_text, generate_title
from langcorrect.users.models import GenderChoices

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


class PostFactory(DjangoModelFactory):
    user = LazyAttribute(lambda x: random.choice(User.objects.all()))
    title = LazyAttribute(lambda x: generate_title(LANGUAGE_TO_FAKER_LOCALE.get(x.language.code)))
    text = LazyAttribute(lambda x: generate_text(LANGUAGE_TO_FAKER_LOCALE.get(x.language.code)))
    native_text = LazyAttribute(lambda _: fake.text())
    slug = LazyAttribute(lambda _: fake.uuid4())
    language = LazyAttribute(
        lambda obj: random.choice(LanguageLevel.objects.filter(user=obj.user).exclude(level="N")).language
    )

    gender_of_narration = LazyAttribute(lambda _: fake.random_element(elements=GenderChoices.choices)[0])
    permission = LazyAttribute(lambda _: fake.random_element(elements=PostVisibility.choices)[0])
    is_corrected = LazyAttribute(lambda _: fake.boolean())

    @post_generation
    def set_language(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.language = Language.objects.get(code=extracted)
            self.save()

    class Meta:
        model = Post
        django_get_or_create = ["slug"]
