from django.conf import settings
from django.db import models
from django.utils import timezone
from model_utils.models import SoftDeletableModel, TimeStampedModel


class Contribution(SoftDeletableModel, TimeStampedModel):
    class Meta:
        ordering = ["-total_points"]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_points = models.IntegerField(default=0)
    post_count = models.IntegerField(default=0)
    correction_count = models.IntegerField(default=0)
    prompt_count = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)

    @property
    def get_average_per_day(self):
        today = timezone.now().date()
        date_joined = self.user.date_joined.date()
        days_since_joined = (today - date_joined).days

        try:
            average = self.total_points / days_since_joined
        except ZeroDivisionError:
            average = 0

        return f"{round(average, 2):.2f}"
