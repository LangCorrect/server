from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import SoftDeletableModel, TimeStampedModel


class CorrectionType(SoftDeletableModel, TimeStampedModel):
    class Meta:
        verbose_name = _("Correction Type")
        verbose_name_plural = _("Correction Types")

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name


class CorrectedRow(SoftDeletableModel, TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, null=True, blank=True)
    post_row = models.ForeignKey("posts.PostRow", on_delete=models.CASCADE)
    correction = models.TextField()
    note = models.TextField(default=None, null=True, blank=True)
    correction_types = models.ManyToManyField(CorrectionType)


class PerfectRow(SoftDeletableModel, TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, null=True, blank=True)
    post_row = models.ForeignKey("posts.PostRow", on_delete=models.CASCADE)


class OverallFeedback(SoftDeletableModel, TimeStampedModel):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE)
    comment = models.TextField()
    is_draft = models.BooleanField(default=False)
