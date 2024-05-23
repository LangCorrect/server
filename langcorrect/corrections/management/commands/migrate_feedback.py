from django.core.management.base import BaseCommand

from langcorrect.corrections.models import CorrectedRow
from langcorrect.corrections.models import PerfectRow
from langcorrect.corrections.models import PostRowFeedback
from langcorrect.posts.models import Post


class Command(BaseCommand):
    help = "Migrate data from CorrectedRow and PerfectRow to PostRowFeedback"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Starting feedback data migration..."))

        posts = Post.all_objects.all().order_by("created")
        end = posts.count()

        for start, post in enumerate(posts, start=1):
            perfect_rows = PerfectRow.available_objects.filter(post=post).order_by(
                "created",
            )
            for perfect_row in perfect_rows:
                PostRowFeedback.objects.create(
                    user=perfect_row.user,
                    post=perfect_row.post,
                    post_row=perfect_row.post_row,
                    feedback_type=PostRowFeedback.FeedbackType.PERFECT,
                    correction="",
                    note="",
                    created=perfect_row.created,
                    modified=perfect_row.modified,
                    is_removed=perfect_row.is_removed,
                )

            corrected_rows = CorrectedRow.available_objects.filter(post=post).order_by(
                "created",
            )
            for corrected_row in corrected_rows:
                feedback = PostRowFeedback.objects.create(
                    user=corrected_row.user,
                    post=corrected_row.post,
                    post_row=corrected_row.post_row,
                    feedback_type=PostRowFeedback.FeedbackType.CORRECTED,
                    correction=corrected_row.correction,
                    note=corrected_row.note or "",
                    created=corrected_row.created,
                    modified=corrected_row.modified,
                    is_removed=corrected_row.is_removed,
                )
                feedback.save()
                feedback.correction_types.set(corrected_row.correction_types.all())

            self.stdout.write(self.style.NOTICE(f"Processed post {start} of {end}"))

        self.stdout.write(self.style.SUCCESS("Data migration completed..."))
