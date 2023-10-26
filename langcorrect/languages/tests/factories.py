from factory import Faker, Sequence, SubFactory
from factory.django import DjangoModelFactory

from langcorrect.languages.models import Language, LanguageLevel, LevelChoices
from langcorrect.users.tests.factories import UserFactory


class LanguageFactory(DjangoModelFactory):
    en_name = Sequence(lambda n: f"language{n}")
    code = Sequence(lambda n: f"code{n}")

    class Meta:
        model = Language
        django_get_or_create = ("en_name", "code")


class LanguageLevelFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    language = SubFactory(LanguageFactory)
    level = Faker("random_element", elements=LevelChoices.values)

    class Meta:
        model = LanguageLevel
