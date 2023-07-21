from django.contrib import admin

from langcorrect.corrections.models import CorrectedRow, CorrectionType


@admin.register(CorrectionType)
class CorrectionTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]


@admin.register(CorrectedRow)
class CorrectedRowAdmin(admin.ModelAdmin):
    readonly_fields = ["post", "user", "post_row", "correction", "note", "correction_types"]
    list_display = ["author", "corrector", "original_sentence", "correction", "note", "get_correction_types"]
    search_fields = ["post__user__username"]

    def author(self, obj):
        if obj.post:
            return obj.post.user
        else:
            return None

    def corrector(self, obj):
        return obj.user

    def original_sentence(self, obj):
        return obj.post_row.sentence

    def get_correction_types(self, obj):
        return [t.name for t in obj.correction_types.all()]
