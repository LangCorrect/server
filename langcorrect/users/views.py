from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()

        now = timezone.now()
        start_date = timezone.make_aware(datetime(now.year, 1, 1))
        end_date = timezone.make_aware(datetime(now.year, 12, 31, 23, 59, 59))

        post_this_year_count = user.post_set.filter(created__range=(start_date, end_date)).count()
        corrections_this_year_count = user.correctedrow_set.filter(created__range=(start_date, end_date)).count()
        perfects_this_year_count = user.perfectrow_set.filter(created__range=(start_date, end_date)).count()
        prompts_this_year_count = user.prompt_set.filter(created__range=(start_date, end_date)).count()

        context.update(
            {
                "totalContributions": post_this_year_count
                + corrections_this_year_count
                + perfects_this_year_count
                + prompts_this_year_count,
                "posts": user.post_set.all()[:10],
                "is_following": True if self.request.user in user.followers_users else False,
            }
        )
        return context


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["first_name", "last_name", "bio", "gender"]
    success_message = _("Information successfully updated")

    def get_success_url(self):
        assert self.request.user.is_authenticated  # for mypy to know that the user is authenticated
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
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        qs = user.notifications.all()
        return qs


notifications_view = NotificationsViewList.as_view()
