from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PostsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "langcorrect.posts"
    verbose_name = _("Posts")
