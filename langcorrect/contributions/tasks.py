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
        # update contributions
        for contribution in contributions:
            posts_count = contribution.user.post_set.count()
            prompts_count = contribution.user.prompt_set.count()
            corrections_count = contribution.user.corrections_made_count
            total_points = posts_count + corrections_count + prompts_count

            contribution.total_points = total_points
            contribution.post_count = posts_count
            contribution.correction_count = corrections_count
            contribution.prompt_count = prompts_count
            contribution.save()

        # calculate rankings
        current_rank = 1
        for contribution in Contribution.available_objects.all():
            contribution.rank = current_rank
            contribution.save()
            current_rank += 1


@celery_app.task()
def calculate_writing_streaks():
    """
    A Celery task to calculate user writing streaks.
    """

    with transaction.atomic():
        for user in User.objects.all():
            update_user_writing_streak(user)
