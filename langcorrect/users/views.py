# ruff: noqa: PLR0911

import logging
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import RedirectView
from django.views.generic import UpdateView

from langcorrect.corrections.models import PostCorrection
from langcorrect.subscriptions.exceptions import MissingSubscriptionIdError
from langcorrect.subscriptions.exceptions import SubscriptionCancellationError
from langcorrect.users.exceptions import MissingSystemUserError
from langcorrect.users.exceptions import UserIsNoneError
from langcorrect.users.helpers import cancel_subscription
from langcorrect.utils.management import DataManagement

logger = logging.getLogger(__name__)


User = get_user_model()

ACCOUNT_DELETION_ERR_MSG = _("An error occurred while deleting your account.")
SYSTEM_ACCOUNT_MISSING_MIGRATION_ERR_MSG = (
    "Cannot migrate data because system user is missing."
)
UNKNOWN_ACCOUNT_DELETION_ERR_MSG = _(
    "An unknown error occurred while deleting your account.",
)


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()

        now = timezone.now()
        start_date = timezone.make_aware(datetime(now.year, 1, 1))  # noqa: DTZ001
        end_date = timezone.make_aware(datetime(now.year, 12, 31, 23, 59, 59))  # noqa: DTZ001

        language_levels_ordered = user.languagelevel_set.order_by("-level")
        post_this_year_count = user.post_set.filter(
            created__range=(start_date, end_date),
        ).count()

        corrections_this_year_count = PostCorrection.available_objects.filter(
            user_correction__user=user,
            created__range=(start_date, end_date),
        ).count()

        prompts_this_year_count = user.prompt_set.filter(
            created__range=(start_date, end_date),
        ).count()

        total_contributions = (
            post_this_year_count + corrections_this_year_count + prompts_this_year_count
        )

        context.update(
            {
                "totalContributions": total_contributions,
                "posts": user.post_set.all()[:10],
                "is_following": self.request.user in user.followers_users,
                "languages": language_levels_ordered,
            },
        )
        return context


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["first_name", "last_name", "bio", "gender"]
    success_message = _("Information successfully updated")

    def get_success_url(self):
        assert (
            self.request.user.is_authenticated
        )  # for mypy to know that the user is authenticated
        return self.request.user.get_absolute_url()

    def get_object(self):
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()


class NotificationsViewList(LoginRequiredMixin, ListView):
    template_name = "notifications/notification_list.html"
    context_object_name = "notifications"
    paginate_by = 25

    def get_queryset(self):
        user = self.request.user
        return user.notifications.all()


notifications_view = NotificationsViewList.as_view()


@login_required
def user_delete_view(request):
    """
    Permanently deleted info:
    - email address (cascade delete)
    - notifications (cascade delete)
    - language levels (cascade delete)
    - contribution (cascade delete)
    - profile info (username, password, first and last name, etc.)

    Anonymized info:
    - posts
    - corrections
    - comments
    - prompts

    """
    current_user = request.user

    if request.method == "POST":
        try:
            cancel_subscription(current_user)

            with transaction.atomic():

                try:
                    system_user = User.objects.get(username="system")
                except User.DoesNotExist:
                    raise MissingSystemUserError(
                        "System user does not exist. Cannot migrate data.",
                    )

                # posts
                DataManagement.migrate_posts(
                    from_user=current_user,
                    to_user=system_user,
                )
                DataManagement.delete_post_images(from_user=current_user)

                # prompts
                DataManagement.migrate_prompts(
                    from_user=current_user,
                    to_user=system_user,
                )

                # corrections
                DataManagement.migrate_corrections(
                    from_user=current_user,
                    to_user=system_user,
                )

                # comments
                DataManagement.migrate_comments(
                    from_user=current_user,
                    to_user=system_user,
                )

                current_user.delete()

                messages.success(
                    request,
                    _("Your account has been deleted successfully."),
                )

                return redirect("/")

        except UserIsNoneError:
            # This should never happen
            messages.error(request, ACCOUNT_DELETION_ERR_MSG)
            return redirect("/")
        except MissingSystemUserError:
            # TODO: add system user in seed.py
            messages.error(request, SYSTEM_ACCOUNT_MISSING_MIGRATION_ERR_MSG)
            return redirect("/")
        except MissingSubscriptionIdError:
            messages.error(request, ACCOUNT_DELETION_ERR_MSG)
            return redirect("/")
        except SubscriptionCancellationError:
            messages.error(request, ACCOUNT_DELETION_ERR_MSG)
            return redirect("/")
        except Exception:  # noqa: BLE001
            messages.error(
                request,
                UNKNOWN_ACCOUNT_DELETION_ERR_MSG,
            )
            return redirect("/")

    return render(request, "users/user_delete.html")
