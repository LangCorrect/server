import random
from collections.abc import Sequence
from typing import Any

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from factory import Faker, LazyAttribute, post_generation
from factory.django import DjangoModelFactory
from faker import Faker as OriginalFaker

from langcorrect.languages.models import Language, LanguageLevel, LevelChoices
from langcorrect.languages.tests.utils import create_native_languages, create_studying_languages

fake = OriginalFaker()


class UserFactory(DjangoModelFactory):
    username = Faker("user_name")
    email = Faker("email")
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    bio = LazyAttribute(lambda _: fake.random_element(elements=["", fake.text()]))

    @post_generation
    def password(self, create: bool, extracted: Sequence[Any], **kwargs):
        password = (
            extracted
            if extracted
            else Faker(
                "password",
                length=42,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ).evaluate(None, None, extra={"locale": None})
        )
        self.set_password(password)
        self.save()

    @post_generation
    def native_languages(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for language_code in extracted:
                language = Language.objects.get(code=language_code)
                LanguageLevel.objects.get_or_create(user=self, language=language, level=LevelChoices.NATIVE)
        else:
            for _ in range(random.randint(1, 3)):
                create_native_languages(self)

    @post_generation
    def studying_languages(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for language_code in extracted:
                language = Language.objects.get(code=language_code)
                LanguageLevel.objects.get_or_create(user=self, language=language)
        else:
            for _ in range(random.randint(1, 2)):
                create_studying_languages(self)

    @post_generation
    def verify_email_address(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            EmailAddress.objects.create(user=self, email=self.email, verified=True, primary=True)

    class Meta:
        model = get_user_model()
        django_get_or_create = ["username"]
