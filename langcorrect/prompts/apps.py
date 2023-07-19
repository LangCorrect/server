from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PromptsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "langcorrect.prompts"
    verbose_name = _("Prompts")
