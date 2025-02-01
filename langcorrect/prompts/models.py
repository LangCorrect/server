# ruff: noqa: DJ001,S311
import random
import string
import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse
from model_utils.models import SoftDeletableModel
from model_utils.models import TimeStampedModel
from taggit.managers import TaggableManager

from langcorrect.languages.models import Language
from langcorrect.languages.models import LevelChoices


class Prompt(SoftDeletableModel, TimeStampedModel):
    class Meta:
        ordering = ["-created"]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    difficulty_level = models.CharField(
        choices=tuple(choice for choice in LevelChoices.choices if choice[0] != "N"),
        max_length=30,
        null=True,
        blank=True,
    )
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255, null=True)
    tags = TaggableManager(blank=True)
    challenge = models.ForeignKey(
        "challenges.Challenge",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    uuid = models.UUIDField(null=True, blank=True, default=uuid.uuid4, editable=False)

    def create_hash(self):
        def get_random_str():
            return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

        slug = get_random_str()
        while Prompt.objects.filter(slug=slug).exists():
            slug = get_random_str()
        return slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.create_hash()

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("prompts:detail", kwargs={"slug": self.slug})

    @property
    def response_count(self):
        return self.post_set.all().count()
