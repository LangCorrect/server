from django.contrib import admin

from langcorrect.corrections.models import CorrectedRow
from langcorrect.corrections.models import CorrectionType
from langcorrect.corrections.models import OverallFeedback
from langcorrect.corrections.models import PerfectRow
from langcorrect.corrections.models import PostRowFeedback


@admin.register(CorrectionType)
class CorrectionTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]


@admin.register(PostRowFeedback)
class PostRowFeedbackAdmin(admin.ModelAdmin):
    list_display = ["user", "post", "post_row", "feedback_type", "correction", "note"]
    readonly_fields = ["user", "post", "post_row", "feedback_type"]


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
