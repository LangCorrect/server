from collections import defaultdict
from datetime import datetime
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone

from langcorrect.contributions.models import Contribution
from langcorrect.corrections.models import PostCorrection
from langcorrect.posts.models import Post

User = get_user_model()


def get_contribution_counts(user_ids=None):
    user_qs = User.objects.all()

    if user_ids is not None:
        user_qs = user_qs.filter(id__in=user_ids)

    # I tried hitting the db once and recreate the separate dicts, but
    # the query took significantly longer than just hitting the db 3 times.

    user_post_counts = dict(
        user_qs.annotate(posts=Count("post")).values_list("id", "posts"),
    )

    user_prompt_counts = dict(
        user_qs.annotate(prompts=Count("prompt")).values_list("id", "prompts"),
    )

    user_correction_counts = dict(
        user_qs.annotate(
            corrections=Count("postusercorrection__corrections"),
        ).values_list("id", "corrections"),
    )
    return user_post_counts, user_prompt_counts, user_correction_counts


def update_contribution_rankings(batch_size=20):
    contributions = Contribution.available_objects.all().order_by("-total_points")
    ranking_updates = []
    current_rank = 1

    for contribution in contributions.iterator(chunk_size=batch_size):
        contribution.rank = current_rank
        ranking_updates.append(contribution)
        current_rank += 1

        if len(ranking_updates) >= batch_size:
            with transaction.atomic():
                Contribution.objects.bulk_update(ranking_updates, ["rank"])
            ranking_updates = []

    if ranking_updates:
        with transaction.atomic():
            Contribution.objects.bulk_update(ranking_updates, ["rank"])


def get_contribution_data(user):
    now = timezone.now()
    start_date = datetime(now.year, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(now.year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

    contribution_data = defaultdict(int)

    models = [
        user.post_set,
        user.prompt_set,
        PostCorrection.available_objects.filter(user_correction__user=user),
    ]

    for model in models:
        aggregated_data = (
            model.filter(created__range=(start_date, end_date))
            .annotate(date_only=TruncDate("created"))
            .values("date_only")
            .annotate(total=Count("id"))
        )

        for entry in aggregated_data:
            contribution_data[entry["date_only"].isoformat()] += entry["total"]

    return [{"date": key, "value": value} for key, value in contribution_data.items()]


def update_user_writing_streak(user):
    posts = Post.available_objects.filter(user=user).order_by("-created")

    streak = 0
    today = timezone.now().date()
    last_published_date = None

    for post in posts.iterator():
        post_date = post.created.date()

        if last_published_date is None:
            last_published_date = post_date

        if last_published_date == today:
            streak = 1

        if post_date == last_published_date:
            continue

        if last_published_date - post_date == timedelta(days=1):
            streak += 1
        else:
            break

        last_published_date = post_date

    contribution = Contribution.objects.get(user=user)
    contribution.writing_streak = streak
    contribution.save()
