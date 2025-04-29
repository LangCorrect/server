import logging
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from langcorrect.subscriptions.utils import StripeManager
from langcorrect.users.models import GenderChoices

logger = logging.getLogger(__name__)

User = get_user_model()


def get_active_user_ids(days=30):
    active_days = timezone.now() - timedelta(days=days)
    return list(
        User.objects.filter(
            last_login__gte=active_days,
        ).values_list("id", flat=True),
    )


def delete_user_notifications(user):
    if user is not None:
        if user.notifications.exists():
            user.notifications.all().delete()


def delete_user_follows(user):
    if user is not None:
        if user.follower.exists():
            user.follower.all().delete()

        if user.follow_to.exists():
            user.follow_to.all().delete()


def anonymize_user(user):
    if user is None:
        return

    # info
    user.gender = GenderChoices.UNKNOWN
    user.username = f"deleted_user_{user.pk}"
    user.first_name = ""
    user.last_name = ""
    user.nick_name = ""
    user.bio = ""
    user.staff_notes = ""
    user.email = f"deleted_user_{user.pk}@langcorrect.com"

    # roles
    user.is_superuser = False
    user.is_staff = False
    user.is_moderator = False
    user.is_volunteer = False
    user.is_premium = False
    user.is_lifetime_vip = False
    user.is_max_studying = False

    user.is_active = False
    user.is_verified = False

    user.save()


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
