import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import SoftDeletableModel
from model_utils.models import TimeStampedModel


class LevelChoices(models.TextChoices):
    A1 = "A1", _("Beginner")
    A2 = "A2", _("Elementary")
    B1 = "B1", _("Intermediate")
    B2 = "B2", _("Upper-Intermediate")
    C1 = "C1", _("Advanced")
    C2 = "C2", _("Proficient")
    NATIVE = "N", _("Native")


class Language(TimeStampedModel, SoftDeletableModel):
    class Meta:
        ordering = ["code"]

    en_name = models.CharField(max_length=120, unique=True)
    family_code = models.CharField(default="N/A")
    code = models.CharField(max_length=7, unique=True)
    uuid = models.UUIDField(null=True, blank=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return f"{_(self.en_name)}"


class LanguageLevel(TimeStampedModel):
    class Meta:
        unique_together = ("user", "language")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    level = models.CharField(
        max_length=2,
        choices=LevelChoices.choices,
        default=LevelChoices.A1,
    )

    def __str__(self):
        return f"{self.language} ({self.get_level_display()})"
