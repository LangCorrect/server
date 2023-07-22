from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FollowsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "langcorrect.follows"
    verbose_name = _("Follows")
