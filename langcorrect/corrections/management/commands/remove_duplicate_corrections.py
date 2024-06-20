from collections import defaultdict
from itertools import chain

from django.core.management.base import BaseCommand
from django.db import transaction

from langcorrect.corrections.models import CorrectedRow
from langcorrect.corrections.models import PerfectRow


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **kwargs):
        count_deleted = 0

        corrected_rows = CorrectedRow.available_objects.order_by(
            "post_row_id",
            "user_id",
            "-created",
        )
        perfect_rows = PerfectRow.available_objects.order_by(
            "post_row_id",
            "user_id",
            "-created",
        )

        grouped_rows = defaultdict(list)

        for row in chain(corrected_rows, perfect_rows):
            key = (row.post_row_id, row.user_id)
            grouped_rows[key].append(row)

        for rows in grouped_rows.values():
            for row in rows[1:]:
                count_deleted += 1
                row.delete()

        self.stdout.write(
            self.style.SUCCESS(f"Deleted {count_deleted} duplicate rows."),
        )
