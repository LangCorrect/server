import itertools as it
from datetime import datetime
from datetime import timedelta
from operator import itemgetter
from typing import Literal

from django.db.models import Count
from django.db.models.query import QuerySet
from django.utils import timezone

from langcorrect.corrections.models import PostCorrection
from langcorrect.corrections.models import PostUserCorrection
from langcorrect.posts.models import Post
from langcorrect.posts.models import PostRow
from langcorrect.users.models import User

start_dates = {
    "daily": lambda: timezone.now() - timedelta(days=1),
    "weekly": lambda: timezone.now() - timedelta(weeks=1),
    "monthly": lambda: timezone.now() - timedelta(days=30),
    "all_time": lambda: None,
}


def create_or_update_correction(
    user_correction: PostUserCorrection,
    post_row: PostRow,
    feedback_type: Literal["perfect", "corrected"],
    correction: str = "",
    note: str = "",
) -> PostCorrection:
    post_correction, _ = PostCorrection.all_objects.update_or_create(
        user_correction=user_correction,
        post_row=post_row,
        defaults={
            "is_removed": False,
            "feedback_type": feedback_type,
            "correction": ""
            if feedback_type == PostCorrection.FeedbackType.PERFECT
            else correction,
            "note": ""
            if feedback_type == PostCorrection.FeedbackType.PERFECT
            else note,
        },
    )

    return post_correction


def delete_correction(user_correction: PostUserCorrection, post_row: PostRow) -> None:
    PostCorrection.available_objects.filter(
        user_correction=user_correction,
        post_row=post_row,
    ).delete()


def get_overall_feedback(post: Post, user: User) -> str | None:
    try:
        return PostUserCorrection.available_objects.get(
            post=post,
            user=user,
        ).overall_feedback
    except PostUserCorrection.DoesNotExist:
        return None


def delete_overall_feedback(post: Post, user: User) -> None:
    try:
        obj = PostUserCorrection.available_objects.get(
            post=post,
            user=user,
        )
        obj.overall_feedback = ""
        obj.save()
    except PostUserCorrection.DoesNotExist as e:
        msg = "Cannot delete non-existent overall feedback."
        raise ValueError(msg) from e


def get_or_create_post_user_correction(post: Post, user: User) -> PostUserCorrection:
    """
    This will create a new PostUserCorrection object if it doesn't exist.
    If it does exist, it will return the existing object, even if it was soft deleted.
    """
    try:
        obj = PostUserCorrection.all_objects.get(
            post=post,
            user=user,
        )
        if obj.is_removed:
            obj.is_removed = False
            obj.save()
        return obj  # noqa: TRY300
    except PostUserCorrection.DoesNotExist:
        return PostUserCorrection.available_objects.create(
            post=post,
            user=user,
        )


def create_post_user_correction(
    post: Post,
    user: User,
    overall_feedback: str,
) -> PostUserCorrection:
    post_user_correction = PostUserCorrection.available_objects.get_or_create(
        post=post,
        user=user,
    )
    post_user_correction.overall_feedback = overall_feedback
    post_user_correction.save()
    return post_user_correction


def get_post_rows(post: Post) -> QuerySet[PostRow]:
    return PostRow.available_objects.filter(
        post=post,
        is_actual=True,
    )


def get_corrected_sentence(post_row: PostRow, user: User) -> PostCorrection | None:
    try:
        return PostCorrection.available_objects.get(
            post_row=post_row,
            user_correction__user=user,
        )
    except PostCorrection.DoesNotExist:
        return None


def get_post_user_corrections(post: Post) -> QuerySet[PostUserCorrection]:
    return PostUserCorrection.available_objects.filter(post=post).select_related("user")


def get_top_correctors(period: Literal["daily", "weekly", "monthly", "all_time"]):
    if period not in start_dates:
        msg = "Invalid time period."
        raise ValueError(msg)

    start_date = start_dates.get(period)()
    corrections = PostCorrection.available_objects.all()

    if start_date:
        corrections = corrections.filter(created__gte=start_date)

    return (
        corrections.values(
            "user_correction__user__username",
            "user_correction__user__nick_name",
        )
        .annotate(
            correction_count=Count("id"),
        )
        .order_by("-correction_count")[:10]
    )


#  ==================== OLD CODE ====================
# TODO: Check what can be removed / deprecated


def _sort_key(correction_dict):
    return correction_dict["ordering"]


def order_user_corrections_by_post_row(user_corrections):
    for user in user_corrections:
        user_corrections[user]["corrections"].sort(key=_sort_key)
    return user_corrections


def populate_user_corrections(
    perfect_rows,
    corrected_rows,
    feedback_rows,
    postreply_rows,
):
    user_corrections = {}

    for row in perfect_rows:
        data = row.serialize
        user = row.user

        if user not in user_corrections:
            user_corrections[user] = {
                "corrections": [],
                "overall_feedback": "",
                "replies": [],
            }
        user_corrections[user]["corrections"].append(data)

    for row in corrected_rows:
        data = row.serialize
        user = row.user

        if user not in user_corrections:
            user_corrections[user] = {
                "corrections": [],
                "overall_feedback": "",
                "replies": [],
            }
        user_corrections[user]["corrections"].append(data)

    for feedback in feedback_rows:
        user = feedback.user

        if user not in user_corrections:
            user_corrections[user] = {
                "corrections": [],
                "overall_feedback": "",
                "replies": [],
            }
        user_corrections[user]["overall_feedback"] = feedback.comment

    for reply in postreply_rows:
        recipient = reply.recipient

        if recipient not in user_corrections:
            user_corrections[recipient] = {
                "corrections": [],
                "overall_feedback": "",
                "replies": [],
            }
        user_corrections[recipient]["replies"].append(reply)

    return order_user_corrections_by_post_row(user_corrections)


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
