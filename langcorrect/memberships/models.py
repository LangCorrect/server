from django.conf import settings
from django.db import models
from model_utils.models import SoftDeletableModel, TimeStampedModel


class Membership(SoftDeletableModel, TimeStampedModel):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    customer_code = models.CharField(max_length=150)
    subscription_code = models.CharField(
        max_length=150,
        help_text="This will be either a subscription code or charge code",
    )
    plan_type = models.CharField(max_length=100)
    billing_cycle_ends = models.DateTimeField(null=True, blank=True)
    is_cancelled = models.BooleanField(default=False)
    cancelled_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.plan_type}"
