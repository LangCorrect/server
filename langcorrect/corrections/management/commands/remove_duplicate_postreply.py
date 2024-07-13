from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction

from langcorrect.posts.models import PostReply


class Command(BaseCommand):
    help = "Delete duplicate PostReply entries"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        count_deleted = 0

        # Fetch and order PostReply instances
        post_replies = PostReply.objects.order_by(
            "post_id",
            "user_id",
            "text",
            "created",
        )

        grouped_replies = defaultdict(list)

        # Group PostReply instances by (post, user, text, created)
        for reply in post_replies:
            key = (reply.post_id, reply.user_id, reply.text, reply.created)
            grouped_replies[key].append(reply)

        # Delete all but the first (oldest) PostReply in each group
        for replies in grouped_replies.values():
            for reply in replies[1:]:
                reply.delete()
                count_deleted += 1

        self.stdout.write(
            self.style.SUCCESS(f"Deleted {count_deleted} duplicate PostReply entries."),
        )
