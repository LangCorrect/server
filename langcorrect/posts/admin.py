from django.contrib import admin

from langcorrect.posts.models import Post
from langcorrect.posts.models import PostReply
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


@admin.register(PostReply)
class PostReplyAdmin(admin.ModelAdmin):
    readonly_fields = [
        "user",
        "recipient",
        "post",
        "corrected_row",
        "perfect_row",
        "reply",
        "dislike",
    ]
    list_display = [
        "user",
        "recipient",
        "post",
        "text",
        "get_corrected_row",
        "get_perfect_row",
        "get_parent",
    ]
    search_fields = ["post__title", "user__username"]

    def get_perfect_row(self, obj):
        if obj.perfect_row:
            return obj.perfect_row.post_row.sentence
        return None

    def get_corrected_row(self, obj):
        if obj.corrected_row:
            return obj.corrected_row.correction
        return None

    def get_parent(self, obj):
        if obj.reply:
            return obj.reply.text
        return None
