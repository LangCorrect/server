from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import SoftDeletableModel, TimeStampedModel


class Product(models.TextChoices):
    PREMIUM_MONTHLY = "monthly", _("Monthly Premium")
    PREMIUM_YEARLY = "yearly", _("Yearly Premium")


class PaymentStatus(models.TextChoices):
    AWAITING_PAYMENT = "A", _("Awaiting Payment")
    PAID = "P", _("Paid")
    FAILED = "F", _("Failed")


class StripeCustomer(SoftDeletableModel, TimeStampedModel):
    user = models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    customer_id = models.CharField(max_length=255)
    has_active_subscription = models.BooleanField(default=False)
    current_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    premium_until = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username


class PaymentHistory(SoftDeletableModel, TimeStampedModel):
    stripe_customer = models.ForeignKey(StripeCustomer, on_delete=models.CASCADE)
    subscription_id = models.CharField(max_length=255)
    session_id = models.CharField(max_length=255)
    product = models.CharField(choices=Product.choices, max_length=7)
    product_id = models.CharField(max_length=255)
    status = models.CharField(choices=PaymentStatus.choices, max_length=1)
    amount_total = models.DecimalField(
        max_digits=5, decimal_places=2, validators=[MinValueValidator(1)]
    )  # stores up to 999.99
    has_used_coupon = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.product} ({self.status}) ({self.amount_total})"
