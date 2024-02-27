import json
from datetime import timedelta

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import decorators
from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from langcorrect.users.forms import UserAdminChangeForm
from langcorrect.users.forms import UserAdminCreationForm

User = get_user_model()

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    # Force the `admin` sign in process to go through the `django-allauth` workflow:
    # https://django-allauth.readthedocs.io/en/stable/advanced.html#admin
    admin.site.login = decorators.login_required(admin.site.login)  # type: ignore[method-assign]


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = [
        "username",
        "pk",
        "is_superuser",
        "is_active",
        "gender",
        "speaks",
        "studies",
    ]
    search_fields = ["username", "email"]
    ordering = ["-date_joined"]

    def speaks(self, user):
        return list(user.native_languages.values_list("code", flat=True))

    def studies(self, user):
        return list(user.studying_languages.values_list("code", flat=True))

    def changelist_view(self, request, extra_context=None):
        now = timezone.now()
        past_31_days = now - timedelta(days=31)

        chart_data = list(
            User.objects.filter(date_joined__gte=past_31_days)
            .annotate(date=TruncDay("date_joined"))
            .values("date")
            .annotate(user_count=Count("id"))
            .order_by("date"),
        )

        as_json = json.dumps(chart_data, cls=DjangoJSONEncoder)
        extra_context = extra_context or {"chart_data": as_json}

        return super().changelist_view(request, extra_context=extra_context)
