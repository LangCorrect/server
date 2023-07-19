from django.contrib import admin

from langcorrect.challenges.models import Challenge


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ["title", "is_active", "description", "start_date", "end_date"]
