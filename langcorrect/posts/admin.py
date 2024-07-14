from django.contrib import admin

from langcorrect.posts.models import Post
from langcorrect.posts.models import PostRow


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
    raw_id_fields = ("user",)


@admin.register(PostRow)
class PostRowAdmin(admin.ModelAdmin):
    list_display = ["user", "post", "sentence", "is_actual", "order"]
