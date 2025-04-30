from django.conf import settings
from django.db import models
from django.urls import reverse
from model_utils.models import TimeStampedModel


class Follower(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="follower",
    )
    follow_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="follow_to",
    )
    get_notification = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user} is following {self.follow_to}"

    def get_absolute_url(self):
        """
        This URL is used in notifications to redirect users to the follower's profile.
        """
        return reverse("users:detail", kwargs={"username": self.user.username})
