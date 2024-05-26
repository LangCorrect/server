import itertools as it
from collections import defaultdict
from datetime import datetime
from datetime import timedelta
from operator import itemgetter

from django.db.models import Count
from django.utils import timezone
from django.utils.translation import gettext_noop
from notifications.signals import notify

from langcorrect.corrections.constants import NotificationTypes
from langcorrect.corrections.models import OverallFeedback
from langcorrect.corrections.models import PostRowFeedback


def _initialize_user_correction_data():
    return {
        "corrections": [],
        "overall_feedback": "",
        "replies": [],
    }


def _add_to_user_corrections(user_corrections, corrections, overall_feedbacks, replies):
    for correction in corrections:
        user_corrections[correction.user]["corrections"].append(correction.serialize)

    for feedback in overall_feedbacks:
        user_corrections[feedback.user]["overall_feedback"] = feedback.comment

    for reply in replies:
        user_corrections[reply.recipient]["replies"].append(reply)

    return user_corrections


def _order_user_corrections_by_post_row(user_corrections):
    for user in user_corrections:
        user_corrections[user]["corrections"].sort(key=lambda x: x["ordering"])
    return user_corrections


def serialize_user_corrections_for_post(post):
    user_corrections = defaultdict(_initialize_user_correction_data)

    corrections = post.postrowfeedback_set.all()
    overall_feedbacks = OverallFeedback.objects.filter(post=post)
    replies = post.postreply_set.all()

    user_corrections = _add_to_user_corrections(
        user_corrections,
        corrections,
        overall_feedbacks,
        replies,
    )

    # More efficient than converting defaultdict to dict
    # https://stackoverflow.com/a/12842716
    user_corrections.default_factory = None
    return _order_user_corrections_by_post_row(user_corrections)


def check_can_make_corrections(current_user, post):
    if post.user == current_user:
        return False

    if post.language not in current_user.native_languages:
        return False

    return True


def get_date_range_filters(period):
    """
    Returns a filter dict for the given period.

    Periods:
    - "today": from the beginning of today until now
    - "this_week": from the beginning of the current week until now
    - "this_month": from the beginning of the current month until now
    - "all_time": no filters will be applied

    Args:
        period (str): "today", "this_week", "this_month", or "all_time"

    Returns:
        dict: a dict of the filters for the given period
    """

    filters = {}
    now = timezone.localtime(timezone.now())
    today = now.date()

    if period == "today":
        filters["created__gte"] = timezone.make_aware(
            datetime.combine(today, datetime.min.time()),
        )
    elif period == "this_week":
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=7)
        filters["created__gte"] = timezone.make_aware(
            datetime.combine(week_start, datetime.min.time()),
        )
        filters["created__lt"] = timezone.make_aware(
            datetime.combine(week_end, datetime.min.time()),
        )
    elif period == "this_month":
        filters["created__year"] = today.year
        filters["created__month"] = today.month
    elif period == "all_time":
        pass

    return filters


def aggregate_users(correctors):
    """
    Aggregates the num_corrections made by each user.

    Args:
        correctors (list): [
            {'user__username': 'jim', 'num_corrections': 2},
            {'user__username': 'admin', 'num_corrections': 9},
            {'user__username': 'jim', 'num_corrections': 2}
        ]

    Returns:
        list: A sorted list in desc order based on num_corrections:
        [
            {'username': 'admin', 'num_corrections': 9},
            {'username': 'jim', 'num_corrections': 4}
        ]
    """

    results = []
    groups = it.groupby(
        sorted(correctors, key=itemgetter("user__username")),
        key=itemgetter("user__username"),
    )

    for username, user_entries in groups:
        total_count = 0
        for entry in user_entries:
            total_count += entry["num_corrections"]
        results.append({"username": username, "num_corrections": total_count})

    return sorted(results, key=itemgetter("num_corrections"), reverse=True)


def get_popular_correctors(period=None, limit=10):
    if period is None:
        return -1

    filters = get_date_range_filters(period)

    popular_correctors = (
        PostRowFeedback.objects.filter(**filters)
        .values(
            "user__username",
            "user__nick_name",
        )
        .annotate(num_corrections=Count("user"))
        .order_by("-num_corrections")[:limit]
    )

    for popular_corrector in popular_correctors:
        username = popular_corrector["user__username"]
        nick_name = popular_corrector["user__nick_name"]
        display_name = nick_name if nick_name else username
        num_corrections = popular_corrector["num_corrections"]

        popular_corrector["username"] = username
        popular_corrector["display_name"] = display_name
        popular_corrector["num_corrections"] = num_corrections

    return popular_correctors


def check_if_correction_exists(user, post, post_row):
    return PostRowFeedback.all_objects.filter(
        user=user,
        post=post,
        post_row=post_row,
    ).exists()


def check_if_overall_feedback_exists(user, post):
    return OverallFeedback.objects.filter(
        user=user,
        post=post,
    ).exists()


def delete_correction(user, post, post_row):
    PostRowFeedback.available_objects.get(
        user=user,
        post=post,
        post_row=post_row,
    ).delete()


def add_or_update_correction(
    user,
    post,
    post_row,
    feedback_type,
    correction="",
    note="",
    correction_types=None,
):
    if check_if_correction_exists(user, post, post_row):
        existing_correction = PostRowFeedback.all_objects.get(
            user=user,
            post=post,
            post_row=post_row,
        )
        existing_correction.feedback_type = feedback_type
        existing_correction.correction = correction
        existing_correction.note = note

        if existing_correction.is_removed:
            existing_correction.is_removed = False

        existing_correction.save()
        return False
    else:
        new_correction = PostRowFeedback.available_objects.create(
            user=user,
            post=post,
            post_row=post_row,
            feedback_type=feedback_type,
            correction=correction,
            note=note,
        )

        if correction_types:
            new_correction.correction_types.set(correction_types)

        return True


def create_notification(
    sender,
    recipient,
    action_object,
    notification_type: NotificationTypes,
):
    match type:
        case NotificationTypes.NEW_CORRECTION:
            notify.send(
                sender=sender,
                recipient=recipient,
                verb=gettext_noop("corrected"),
                action_object=object,
                notification_type=NotificationTypes.NEW_CORRECTION,
            )
        case NotificationTypes.UPDATE_CORRECTION:
            notify.send(
                sender=sender,
                recipient=recipient,
                verb=gettext_noop("updated their corrections on"),
                action_object=object,
                notification_type=NotificationTypes.UPDATE_CORRECTION,
            )
        case NotificationTypes.NEW_COMMENT:
            notify.send(
                sender=sender,
                recipient=recipient,
                verb=gettext_noop("commented on"),
                action_object=object,
                notification_type=NotificationTypes.NEW_COMMENT,
            )
        case NotificationTypes.NEW_POST:
            notify.send(
                sender=sender,
                recipient=recipient,
                verb=gettext_noop("posted"),
                action_object=object,
                notification_type=NotificationTypes.NEW_POST,
            )
        case NotificationTypes.NEW_REPLY:
            notify.send(
                sender=sender,
                recipient=recipient,
                verb=gettext_noop("replied on"),
                action_object=object,
                notification_type=NotificationTypes.NEW_REPLY,
            )
        case NotificationTypes.NEW_FOLLOWER:
            notify.send(
                sender=sender,
                recipient=recipient,
                verb=gettext_noop("followed you"),
                action_object=object,
                notification_type=NotificationTypes.NEW_FOLLOWER,
            )
        case _:
            pass
