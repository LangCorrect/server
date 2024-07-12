from django.contrib import admin

from langcorrect.corrections.models import Comment
from langcorrect.corrections.models import CorrectionType
from langcorrect.corrections.models import PostCorrection
from langcorrect.corrections.models import PostUserCorrection


@admin.register(CorrectionType)
class CorrectionTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]


@admin.register(PostUserCorrection)
class PostUserCorrectionAdmin(admin.ModelAdmin):
    readonly_fields = [
        "user",
        "post",
        "overall_feedback",
    ]

    list_display = ["user", "get_title", "get_language", "created", "overall_feedback"]

    def get_title(self, obj):
        return obj.post.title

    def get_language(self, obj):
        return obj.post.language


@admin.register(PostCorrection)
class PostCorrectionAdmin(admin.ModelAdmin):
    readonly_fields = [
        "user_correction",
        "post_row",
        "feedback_type",
    ]

    list_display = [
        "original_sentence",
        "feedback_type",
        "correction",
        "created",
        "modified",
    ]

    def original_sentence(self, obj):
        return obj.post_row.sentence


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    readonly_fields = [
        "user",
        "user_correction",
        "correction",
        "parent",
    ]
    list_display = [
        "user",
        "user_correction",
        "text",
        "correction",
        "created",
        "modified",
    ]
