from datetime import datetime

from django.utils import timezone

from langcorrect.subscriptions.models import StripeCustomer
from langcorrect.subscriptions.utils import StripeManager


def timezone_aware_datatime_from_timestamp(value):
    if isinstance(value, datetime):
        if timezone.is_aware(value):
            return value
        return timezone.make_aware(value, timezone.utc)

    if value:
        return datetime.fromtimestamp(value, tz=timezone.utc)
    return "-"


def get_stripe_customer(user):
    try:
        return StripeCustomer.objects.get(user=user)
    except StripeCustomer.DoesNotExist:
        return None


def handle_subscription_cancellation(subscription_id):
    return serialize_subscription_info(
        StripeManager.cancel_subscription(subscription_id),
    )


def get_current_subscription(stripe_customer):
    if stripe_customer:
        subscription_id = (
            stripe_customer.current_subscription_id
            or stripe_customer.last_subscription_id
        )
        return StripeManager.retrieve_subscription(subscription_id)
    return None


def serialize_subscription_info(subscription):
    data = {}
    data["id"] = subscription["id"]
    data["created"] = timezone_aware_datatime_from_timestamp(subscription["created"])
    data["ended_at"] = timezone_aware_datatime_from_timestamp(subscription["ended_at"])
    data["current_period_start"] = timezone_aware_datatime_from_timestamp(
        subscription["current_period_start"],
    )
    data["current_period_end"] = timezone_aware_datatime_from_timestamp(
        subscription["current_period_end"],
    )
    data["subscription_status"] = subscription["status"]
    data["canceled_at"] = timezone_aware_datatime_from_timestamp(
        subscription["canceled_at"],
    )
    data["currency"] = subscription["currency"]
    data["amount"] = StripeManager.caclulate_amount_with_discount(subscription)

    return data
