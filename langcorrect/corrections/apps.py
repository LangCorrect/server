from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CorrectionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "langcorrect.corrections"
    verbose_name = _("Corrections")
