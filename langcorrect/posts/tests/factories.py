from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

from langcorrect.languages.tests.factories import LanguageFactory
from langcorrect.posts.models import Post, PostVisibility
from langcorrect.users.tests.factories import UserFactory


class PostFactory(DjangoModelFactory):
    slug = Faker("uuid4")
    user = SubFactory(UserFactory)
    permission = Faker("random_element", elements=[elem.value for elem in PostVisibility])
    is_corrected = Faker("random_element", elements=[0, 1])
    language = SubFactory(LanguageFactory)

    class Meta:
        model = Post
        django_get_or_create = ["slug"]
