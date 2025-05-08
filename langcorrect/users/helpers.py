# ruff: noqa: RSE102

import logging
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from langcorrect.subscriptions.exceptions import MissingSubscriptionIdError
from langcorrect.subscriptions.exceptions import SubscriptionCancellationError
from langcorrect.subscriptions.utils import StripeManager
from langcorrect.users.exceptions import UserIsNoneError

logger = logging.getLogger(__name__)

User = get_user_model()

USER_IS_PREMIUM_BUT_NO_SUB_ID_ERR_MSG = (
    "%s has an active subscription flag, but no sub ID."
)
SUBSCRIPTION_CANCELLED_SUCCESS_MSG = "Cancelled subscription for user %s with ID %s."
SUBSCRIPTION_CANCELLATION_ERR_MSG = "Error cancelling subscription for user %s."


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
        raise UserIsNoneError()

    # Users who do not proceed to the checkout page will not
    # have a StripeCustomer object
    stripe_customer = getattr(user, "stripecustomer", None)
    if stripe_customer is None:
        return True

    if not stripe_customer.has_active_subscription:
        return True

    sub_id = stripe_customer.current_subscription_id
    if sub_id is None:
        raise MissingSubscriptionIdError()
    try:
        StripeManager.cancel_subscription(sub_id)
    except Exception as err:  # noqa: BLE001
        raise SubscriptionCancellationError(
            message=f"Error cancelling subscription for user {user.username}",
        ) from err

    # TODO: remove this after testing
    logger.info(
        SUBSCRIPTION_CANCELLED_SUCCESS_MSG,
        user.username,
        sub_id,
    )
    return True


def is_system_user(user):
    return getattr(user, "is_system", False)
