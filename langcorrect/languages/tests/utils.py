import random

from django.db import IntegrityError
from faker import Faker

from langcorrect.languages.models import Language, LanguageLevel, LevelChoices

fake = Faker()


def get_available_language(user):
    existing_language_ids = LanguageLevel.objects.filter(user=user).values_list("language", flat=True)
    available_languages = Language.objects.exclude(id__in=existing_language_ids)
    return available_languages


def create_language_level(user, level, is_native=False):
    try:
        available_languages = get_available_language(user)
        if available_languages:
            language = random.choice(available_languages)
            defaults = {"level": level} if not is_native else {"level": LevelChoices.NATIVE}
            LanguageLevel.objects.get_or_create(user=user, language=language, defaults=defaults)
    except IntegrityError:
        pass


def create_studying_languages(user, level="A1"):
    create_language_level(user, level)


def create_native_languages(user):
    create_language_level(user, LevelChoices.NATIVE, is_native=True)
