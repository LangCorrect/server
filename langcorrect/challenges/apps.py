from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ChallengesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "langcorrect.challenges"
    verbose_name = _("Challenges")
