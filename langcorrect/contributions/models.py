from django.conf import settings
from django.db import models
from model_utils.models import SoftDeletableModel, TimeStampedModel


class Contribution(SoftDeletableModel, TimeStampedModel):
    class Meta:
        ordering = ["-total_points"]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_points = models.IntegerField(default=0)
    post_count = models.IntegerField(default=0)
    correction_count = models.IntegerField(default=0)
