from django.contrib import admin

from langcorrect.corrections.models import Comment
from langcorrect.corrections.models import CorrectedRow
from langcorrect.corrections.models import CorrectionType
from langcorrect.corrections.models import OverallFeedback
from langcorrect.corrections.models import PerfectRow
from langcorrect.corrections.models import PostCorrection
from langcorrect.corrections.models import PostUserCorrection


@admin.register(CorrectionType)
class CorrectionTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]


@admin.register(CorrectedRow)
class CorrectedRowAdmin(admin.ModelAdmin):
    readonly_fields = [
        "post",
        "user",
        "post_row",
        "correction",
        "note",
        "correction_types",
    ]
    list_display = [
        "author",
        "corrector",
        "original_sentence",
        "correction",
        "note",
        "get_correction_types",
    ]
    search_fields = ["post__user__username"]

    def author(self, obj):
        if obj.post:
            return obj.post.user
        return None

    def corrector(self, obj):
        return obj.user

    def original_sentence(self, obj):
        return obj.post_row.sentence

    def get_correction_types(self, obj):
        return [t.name for t in obj.correction_types.all()]


@admin.register(PerfectRow)
class PerfectRowAdmin(admin.ModelAdmin):
    readonly_fields = ["post", "user", "post_row"]
    list_display = ["author", "corrector", "original_sentence"]
    search_fields = ["post__user__username"]

    def author(self, obj):
        if obj.post:
            return obj.post.user
        return None

    def corrector(self, obj):
        return obj.user

    def original_sentence(self, obj):
        return obj.post_row.sentence


@admin.register(OverallFeedback)
class OverallFeedbackAdmin(admin.ModelAdmin):
    readonly_fields = ["post", "user", "comment"]
    list_display = ["receiver", "corrector", "comment", "is_draft"]
    search_fields = ["post__user__username"]

    def receiver(self, obj):
        if obj.post:
            return obj.post.user
        return None

    def corrector(self, obj):
        return obj.user


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
