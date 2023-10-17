from factory import Sequence
from factory.django import DjangoModelFactory

from langcorrect.languages.models import Language


class LanguageFactory(DjangoModelFactory):
    en_name = Sequence(lambda n: f"language{n}")
    code = Sequence(lambda n: f"code{n}")

    class Meta:
        model = Language
        django_get_or_create = ("en_name", "code")
