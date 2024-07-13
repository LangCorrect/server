from django.contrib.auth import get_user_model
from django.db import transaction

from config import celery_app
from langcorrect.contributions.helpers import update_user_writing_streak
from langcorrect.contributions.models import Contribution
from langcorrect.corrections.models import PostCorrection

User = get_user_model()


@celery_app.task()
def calculate_rankings(batch_size=20):
    """
    A Celery task to calculate user rankings based on total contributions.
    """
    contributions = Contribution.available_objects.select_related("user").all()
    contribution_updates = []

    for contribution in contributions.iterator(chunk_size=batch_size):
        user = contribution.user

        posts_count = user.post_set.count()
        prompts_count = user.prompt_set.count()
        corrections_count = PostCorrection.available_objects.filter(
            user_correction__user=user,
        ).count()

        total_points = posts_count + corrections_count + prompts_count

        contribution.total_points = total_points
        contribution.post_count = posts_count
        contribution.correction_count = corrections_count
        contribution.prompt_count = prompts_count

        contribution_updates.append(contribution)

        if len(contribution_updates) >= batch_size:
            with transaction.atomic():
                Contribution.objects.bulk_update(
                    contribution_updates,
                    ["total_points", "post_count", "correction_count", "prompt_count"],
                )
            contribution_updates = []

    if contribution_updates:
        with transaction.atomic():
            Contribution.objects.bulk_update(
                contribution_updates,
                ["total_points", "post_count", "correction_count", "prompt_count"],
            )

    contributions = Contribution.available_objects.order_by("-total_points")
    ranking_updates = []
    current_rank = 1

    for contribution in contributions.iterator(chunk_size=batch_size):
        ranking_updates.append(
            Contribution(id=contribution.id, rank=current_rank),
        )
        current_rank += 1

        if len(ranking_updates) >= batch_size:
            with transaction.atomic():
                Contribution.objects.bulk_update(ranking_updates, ["rank"])
            ranking_updates = []

    if ranking_updates:
        with transaction.atomic():
            Contribution.objects.bulk_update(ranking_updates, ["rank"])


@celery_app.task()
def calculate_writing_streaks():
    """
    A Celery task to calculate user writing streaks.
    """

    with transaction.atomic():
        for user in User.objects.all():
            update_user_writing_streak(user)
