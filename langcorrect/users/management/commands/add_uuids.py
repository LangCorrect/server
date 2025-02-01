import uuid

from django.core.management.base import BaseCommand
from django.db import transaction

from langcorrect.challenges.models import Challenge
from langcorrect.corrections.models import Comment
from langcorrect.corrections.models import PostCorrection
from langcorrect.corrections.models import PostUserCorrection
from langcorrect.languages.models import Language
from langcorrect.posts.models import Post
from langcorrect.posts.models import PostRow
from langcorrect.prompts.models import Prompt
from langcorrect.users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.atomic():
            for model in [
                User,
                Language,
                Post,
                PostRow,
                Prompt,
                Challenge,
                Comment,
                PostCorrection,
                PostUserCorrection,
            ]:
                self.stdout.write(f"Adding UUIDs to {model.__name__}...")
                for instance in model.objects.all():
                    instance.uuid = str(uuid.uuid4())
                    instance.save()
            self.stdout.write("All UUIDs added successfully.")
