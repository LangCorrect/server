from django.contrib import admin

from langcorrect.prompts.models import Prompt


@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = [
        "content",
        "user",
        "challenge",
        "difficulty_level",
        "language",
        "created",
        "display_tags",
    ]
    list_filter = ["language", "difficulty_level", "challenge"]
    search_fields = ["user__username", "content"]
    autocomplete_fields = ["user"]

    def display_tags(self, obj):
        tags = [tag.name for tag in obj.tags.all()]
        return ", ".join(tags)
