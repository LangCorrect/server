from collections import defaultdict

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone


def get_contribution_data(user):
    today = timezone.now().date()
    start_date = timezone.datetime(today.year, 1, 1).date()
    end_date = timezone.datetime(today.year, 12, 31).date()
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
