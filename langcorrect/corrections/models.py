# ruff: noqa: DJ001
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import SoftDeletableModel
from model_utils.models import TimeStampedModel

from langcorrect.corrections import diff_match_patch


class CorrectionType(SoftDeletableModel, TimeStampedModel):
    class Meta:
        verbose_name = _("Correction Type")
        verbose_name_plural = _("Correction Types")

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name


class PostUserCorrection(TimeStampedModel, SoftDeletableModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE)
    overall_feedback = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-created"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"],
                name="unique_user_post",
            ),
        ]


class PostCorrection(TimeStampedModel, SoftDeletableModel):
    class FeedbackType(models.TextChoices):
        PERFECT = "perfect", _("Perfect")
        CORRECTED = "corrected", _("Corrected")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["post_row", "user_correction"],
                name="unique_post_row_user_correction",
            ),
        ]

    user_correction = models.ForeignKey(
        PostUserCorrection,
        on_delete=models.CASCADE,
        related_name="corrections",
    )
    post_row = models.ForeignKey("posts.PostRow", on_delete=models.CASCADE)
    correction = models.TextField(default="", blank=True)
    note = models.TextField(default="", blank=True)
    correction_types = models.ManyToManyField(CorrectionType, blank=True)
    feedback_type = models.CharField(max_length=10, choices=FeedbackType.choices)

    def clean(self):
        if self.feedback_type == self.FeedbackType.PERFECT:
            if self.correction:
                raise ValidationError(
                    _("A sentence marked as 'Perfect' cannot have a correction."),
                )
            if self.correction_types.exists():
                raise ValidationError(
                    _("A sentence marked as 'Perfect' cannot have correction types."),
                )
        elif self.feedback_type == self.FeedbackType.CORRECTED:
            if not self.correction:
                raise ValidationError(
                    _("A sentence marked as 'Corrected' must have a correction."),
                )

    @property
    def serialize(self):
        return {
            "type": self.feedback_type,
            "correction": self.display_correction,
            "note": self.note,
            "correction_types": self.correction_types,
            "ordering": self.post_row.order,
        }

    @property
    def display_correction(self):
        if self.feedback_type != self.FeedbackType.CORRECTED:
            return self.post_row.sentence
        dmp = diff_match_patch.diff_match_patch()
        diffs = dmp.diff_main(self.post_row.sentence, self.correction)
        dmp.diff_cleanupSemantic(diffs)
        return dmp.diff_prettyHtml(diffs)


class Comment(TimeStampedModel, SoftDeletableModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user_correction = models.ForeignKey(
        PostUserCorrection,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    text = models.TextField()
    correction = models.ForeignKey(PostCorrection, on_delete=models.SET_NULL, null=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies",
    )

    class Meta:
        ordering = ["created"]

    def __str__(self):
        return f"Comment by {self.user} on {self.user_correction}"


class CorrectedRow(SoftDeletableModel, TimeStampedModel):
    # TODO: Remove; Merged into PostCorrection
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    post_row = models.ForeignKey("posts.PostRow", on_delete=models.CASCADE)
    correction = models.TextField()
    note = models.TextField(default=None, null=True, blank=True)
    correction_types = models.ManyToManyField(CorrectionType)

    @property
    def serialize(self):
        return {
            "type": "corrected",
            "correction": self.display_correction,
            "note": self.note,
            "correction_types": self.correction_types,
            "ordering": self.post_row.order,
        }

    @property
    def display_correction(self):
        dmp = diff_match_patch.diff_match_patch()
        diffs = dmp.diff_main(self.post_row.sentence, self.correction)
        dmp.diff_cleanupSemantic(diffs)
        return dmp.diff_prettyHtml(diffs)


class PerfectRow(SoftDeletableModel, TimeStampedModel):
    # TODO: Remove; Merged into PostCorrection
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    post_row = models.ForeignKey("posts.PostRow", on_delete=models.CASCADE)

    @property
    def serialize(self):
        return {
            "type": "perfect",
            "correction": self.post_row.sentence,
            "ordering": self.post_row.order,
        }


class OverallFeedback(SoftDeletableModel, TimeStampedModel):
    # TODO: Remove; Merged into PostUserCorrection
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE)
    comment = models.TextField()
    is_draft = models.BooleanField(default=False)
