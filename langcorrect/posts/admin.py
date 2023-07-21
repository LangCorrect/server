from django.contrib import admin

from langcorrect.posts.models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "title",
        "language",
        "gender_of_narration",
        "permission",
        "prompt",
        "is_draft",
        "is_corrected",
        "language_level",
        "created",
    ]
    search_fields = ["title", "user__username"]
