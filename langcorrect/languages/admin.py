from django.contrib import admin

from langcorrect.languages.models import Language
from langcorrect.languages.models import LanguageLevel


class NoDeleteAdminMixin:
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Language)
class LanguageAdmin(NoDeleteAdminMixin, admin.ModelAdmin):
    list_display = ["id", "code", "family_code", "en_name"]
    search_fields = ["code", "en_name"]


@admin.register(LanguageLevel)
class LanguageLevelsAdmin(admin.ModelAdmin):
    list_display = ["user", "language", "level"]
    search_fields = ["user__username"]
