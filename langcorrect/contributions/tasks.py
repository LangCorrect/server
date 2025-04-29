from django.contrib.auth import get_user_model
from django.db import transaction

from config import celery_app
from langcorrect.contributions.helpers import get_contribution_counts
from langcorrect.contributions.helpers import update_contribution_rankings
from langcorrect.contributions.helpers import update_user_writing_streak
from langcorrect.contributions.models import Contribution
from langcorrect.users.helpers import get_active_user_ids
from langcorrect.users.helpers import get_active_users

User = get_user_model()


@celery_app.task()
def calculate_contribution_points(batch_size=20, days=60):
    active_user_ids = get_active_user_ids(days=days)

    (
        user_post_counts,
        user_prompt_counts,
        user_correction_counts,
    ) = get_contribution_counts(user_ids=active_user_ids)

    contributions = Contribution.available_objects.filter(
        user_id__in=active_user_ids,
    ).select_related("user")

    if not contributions.exists():
        return

    _update_contribution_points(
        contributions=contributions,
        user_post_counts=user_post_counts,
        user_prompt_counts=user_prompt_counts,
        user_correction_counts=user_correction_counts,
        batch_size=batch_size,
    )
    update_contribution_rankings(batch_size=batch_size)


@celery_app.task()
def calculate_writing_streaks():
    for user in get_active_users(days=90).select_related("contribution"):
        with transaction.atomic():
            update_user_writing_streak(user)


def _update_contribution_points(
    contributions,
    user_post_counts,
    user_prompt_counts,
    user_correction_counts,
    batch_size,
):
    contribution_updates = []

    for contribution in contributions.iterator(chunk_size=batch_size):
        user = contribution.user
        posts = user_post_counts.get(user.id, 0)
        prompts = user_prompt_counts.get(user.id, 0)
        corrections = user_correction_counts.get(user.id, 0)

        total_points = posts + prompts + corrections

        contribution.total_points = total_points
        contribution.post_count = posts
        contribution.prompt_count = prompts
        contribution.correction_count = corrections

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
