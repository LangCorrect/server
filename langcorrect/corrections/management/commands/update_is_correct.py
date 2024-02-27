from django.core.management.base import BaseCommand
from django.db.models import Subquery

from langcorrect.corrections.models import CorrectedRow
from langcorrect.corrections.models import PerfectRow
from langcorrect.posts.models import Post


class Command(BaseCommand):
    """
    Correct the value of 'is_correct' if there is no corrector for a post
    This command needs to be run only once and can be deleted afterwards
    """

    def handle(self, *args, **options):
        corrected_post_ids = CorrectedRow.objects.values("post_id").distinct()
        perfect_post_ids = PerfectRow.objects.values("post_id").distinct()
        revised_post_ids = Subquery(corrected_post_ids.union(perfect_post_ids))

        Post.objects.exclude(id__in=revised_post_ids).update(is_corrected=False)
