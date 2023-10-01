from collections import defaultdict
from datetime import datetime, timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone

from langcorrect.contributions.models import Contribution
from langcorrect.posts.models import Post


def get_contribution_data(user):
    now = timezone.now()
    start_date = timezone.make_aware(datetime(now.year, 1, 1))
    end_date = timezone.make_aware(datetime(now.year, 12, 31, 23, 59, 59))

    contribution_data = defaultdict(int)

    models = [user.post_set, user.correctedrow_set, user.perfectrow_set, user.prompt_set]

    for model in models:
        aggregated_data = (
            model.filter(created__range=(start_date, end_date))
            .annotate(date_only=TruncDate("created"))
            .values("date_only")
            .annotate(total=Count("id"))
        )

        for entry in aggregated_data:
            contribution_data[entry["date_only"].isoformat()] += entry["total"]

    serialized_data = [{"date": key, "value": value} for key, value in contribution_data.items()]

    return serialized_data


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
