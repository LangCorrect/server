from django.contrib.auth import get_user_model
from django.db import transaction

from config import celery_app
from langcorrect.contributions.helpers import update_user_writing_streak
from langcorrect.contributions.models import Contribution

User = get_user_model()


@celery_app.task()
def calculate_rankings():
    """
    A Celery task to calculate user rankings based on total contributions.
    """
    contributions = (
        Contribution.available_objects.select_related("user")
        .prefetch_related(
            "user__post_set",
            "user__prompt_set",
        )
        .all()
    )

    with transaction.atomic():
        contribution_updates = []

        for contribution in contributions:
            posts_count = contribution.user.post_set.count()
            prompts_count = contribution.user.prompt_set.count()
            corrections_count = contribution.user.corrections_made_count
            total_points = posts_count + corrections_count + prompts_count

            contribution_updates.append(
                Contribution(
                    id=contribution.id,
                    total_points=total_points,
                    post_count=posts_count,
                    correction_count=corrections_count,
                    prompt_count=prompts_count,
                ),
            )

        Contribution.objects.bulk_update(
            contribution_updates,
            ["total_points", "post_count", "correction_count", "prompt_count"],
        )

        ranking_updates = []
        current_rank = 1

        for contribution in Contribution.available_objects.order_by("-total_points"):
            ranking_updates.append(
                Contribution(id=contribution.id, rank=current_rank),
            )
            current_rank += 1

        Contribution.objects.bulk_update(ranking_updates, ["rank"])


@celery_app.task()
def calculate_writing_streaks():
    """
    A Celery task to calculate user writing streaks.
    """

    with transaction.atomic():
        for user in User.objects.all():
            update_user_writing_streak(user)
