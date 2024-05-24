import itertools as it
from collections import defaultdict
from datetime import datetime
from datetime import timedelta
from operator import itemgetter

from django.db.models import Count
from django.utils import timezone

from langcorrect.corrections.models import CorrectedRow
from langcorrect.corrections.models import OverallFeedback
from langcorrect.corrections.models import PerfectRow
from langcorrect.users.models import User


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

    correctors = list(
        PerfectRow.available_objects.filter(**filters)
        .values("user__username")
        .annotate(num_corrections=Count("user")),
    ) + list(
        CorrectedRow.available_objects.filter(**filters)
        .values("user__username")
        .annotate(num_corrections=Count("user")),
    )

    popular_correctors = aggregate_users(correctors)[:limit]
    for popular_corrector in popular_correctors:
        display_name = User.objects.get(
            username=popular_corrector["username"],
        ).display_name
        popular_corrector["display_name"] = display_name

    return popular_correctors
