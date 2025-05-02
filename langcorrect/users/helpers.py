import logging
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from langcorrect.subscriptions.utils import StripeManager

logger = logging.getLogger(__name__)

User = get_user_model()


def get_active_user_ids(days=30):
    active_days = timezone.now() - timedelta(days=days)
    return list(
        User.objects.filter(
            last_login__gte=active_days,
        ).values_list("id", flat=True),
    )


def get_active_users(days=30):
    active_days = timezone.now() - timedelta(days=days)
    return User.objects.filter(last_login__gte=active_days)


def cancel_subscription(user):
    if user is None:
        msg = "User cannot be None"
        raise ValueError(msg)

    # Users who do not proceed to the checkout page will not
    # have a StripeCustomer object
    stripe_customer = getattr(user, "stripecustomer", None)
    if stripe_customer is None:
        return True

    if not stripe_customer.has_active_subscription:
        return True

    sub_id = stripe_customer.current_subscription_id
    if sub_id is None:
        msg = f"{user.username} has an active subscription flag, but no sub ID."
        logger.warning(msg)
        return False

    try:
        StripeManager.cancel_subscription(sub_id)
    except Exception:
        logger.exception("Error cancelling subscription for user %s.", user.username)
        return False

    logger.info(
        "Cancelled subscription for user %s with ID %s.",
        user.username,
        sub_id,
    )
    return True


def is_system_user(user):
    return getattr(user, "is_system", False)
