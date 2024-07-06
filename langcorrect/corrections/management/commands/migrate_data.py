from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from langcorrect.corrections.models import Comment
from langcorrect.corrections.models import CorrectedRow
from langcorrect.corrections.models import OverallFeedback
from langcorrect.corrections.models import PerfectRow
from langcorrect.corrections.models import PostCorrection
from langcorrect.corrections.models import PostUserCorrection
from langcorrect.posts.models import Post
from langcorrect.posts.models import PostReply

User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            self.stdout.write("Starting data migration...")
            with transaction.atomic():
                # NOTE: Don't mess with the order of these calls
                self.populate_post_user_corrections()
                self.populate_post_corrections()
                self.populate_comments()
            self.stdout.write(
                self.style.SUCCESS("Data migration completed successfully."),
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error during migration: {e}"))

    def populate_post_user_corrections(self):
        all_posts = Post.all_objects.all().order_by("created")

        for post in all_posts:
            correctors = post.get_correctors

            for corrector in correctors:
                overall_feedback = OverallFeedback.objects.filter(
                    user=corrector,
                    post=post,
                ).first()

                PostUserCorrection.objects.create(
                    user=corrector,
                    post=post,
                    overall_feedback=overall_feedback.comment
                    if overall_feedback
                    else None,
                )

    def populate_post_corrections(self):
        post_user_corrections = PostUserCorrection.objects.all().order_by("created")

        for post_user_correction in post_user_corrections:
            post = post_user_correction.post
            corrector = post_user_correction.user

            perfect_rows = PerfectRow.available_objects.filter(
                user=corrector,
                post=post,
            )
            for perfect_row in perfect_rows:
                PostCorrection.objects.create(
                    created=perfect_row.created,
                    modified=perfect_row.modified,
                    user_correction=post_user_correction,
                    post_row=perfect_row.post_row,
                    correction="",
                    note="",
                    feedback_type=PostCorrection.FeedbackType.PERFECT,
                )

            corrected_rows = CorrectedRow.available_objects.filter(
                user=corrector,
                post=post,
            )
            for corrected_row in corrected_rows:
                post_correction = PostCorrection.objects.create(
                    created=corrected_row.created,
                    modified=corrected_row.modified,
                    user_correction=post_user_correction,
                    post_row=corrected_row.post_row,
                    correction=corrected_row.correction,
                    note=corrected_row.note or "",
                    feedback_type=PostCorrection.FeedbackType.CORRECTED,
                )

                post_correction.correction_types.set(
                    corrected_row.correction_types.all(),
                )

    def populate_comments(self):
        count_created = 0

        post_user_corrections = PostUserCorrection.objects.all()
        for post_user_correction in post_user_corrections:
            post = post_user_correction.post
            corrector = post_user_correction.user

            post_replies = PostReply.objects.filter(post=post).order_by("created")

            for post_reply in post_replies:
                # Determine if the post_reply is associated with the corrector or recipient
                if post_reply.user == corrector or post_reply.recipient == corrector:
                    comment, created = Comment.objects.get_or_create(
                        user=post_reply.user,
                        user_correction=post_user_correction,
                        text=post_reply.text,
                        defaults={
                            "created": post_reply.created,
                            "modified": post_reply.modified,
                            "is_removed": post_reply.is_removed,
                        },
                    )
                    if created:
                        count_created += 1

                    # Handle quoted corrections
                    if post_reply.perfect_row:
                        try:
                            correction = PostCorrection.objects.get(
                                user_correction=post_user_correction,
                                post_row=post_reply.perfect_row.post_row,
                                feedback_type=PostCorrection.FeedbackType.PERFECT,
                            )
                            comment.correction = correction
                            comment.save()
                        except PostCorrection.DoesNotExist:
                            self.stderr.write(
                                self.style.ERROR(
                                    f"No matching perfect row correction for PostReply {post_reply.id}",
                                ),
                            )

                    if post_reply.corrected_row:
                        try:
                            correction = PostCorrection.objects.get(
                                user_correction=post_user_correction,
                                post_row=post_reply.corrected_row.post_row,
                                feedback_type=PostCorrection.FeedbackType.CORRECTED,
                            )
                            comment.correction = correction
                            comment.save()
                        except PostCorrection.DoesNotExist:
                            self.stderr.write(
                                self.style.ERROR(
                                    f"No matching corrected row correction for PostReply {post_reply.id}",
                                ),
                            )

                    # Handle quoted replies
                    if post_reply.reply:
                        try:
                            quoted_comment = Comment.objects.get(
                                user=post_reply.reply.user,
                                user_correction=post_user_correction,
                                text=post_reply.reply.text,
                            )
                            comment.parent = quoted_comment
                            comment.save()
                        except Comment.DoesNotExist:
                            self.stderr.write(
                                self.style.ERROR(
                                    f"No matching reply comment for PostReply {post_reply.id}",
                                ),
                            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {count_created} Comment objects from PostReply.",
            ),
        )
