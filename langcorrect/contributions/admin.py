from django.contrib import admin

from langcorrect.contributions.models import Contribution


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ["user", "total_points", "post_count", "correction_count", "writing_streak"]
    search_fields = ["user__username"]
