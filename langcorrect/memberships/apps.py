from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MembershipsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "langcorrect.memberships"
    verbose_name = _("Memberships")
