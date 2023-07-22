from django.contrib import admin

from langcorrect.follows.models import Follower


@admin.register(Follower)
class FollowerAdmin(admin.ModelAdmin):
    list_display = ["user", "follow_to", "created", "modified"]
    search_fields = ["user__username"]
