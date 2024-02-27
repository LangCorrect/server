from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext_noop
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView
from notifications.signals import notify

from langcorrect.follows.models import Follower

User = get_user_model()


class FollowerListView(LoginRequiredMixin, ListView):
    model = Follower
    paginate_by = 100
    template_name = "follows/followers.html"

    def get_queryset(self):
        username = self.kwargs.get("username")
        qs = super().get_queryset()
        return qs.filter(follow_to__username=username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["username"] = self.kwargs.get("username")
        return context


follower_list_view = FollowerListView.as_view()


class FollowingListView(LoginRequiredMixin, ListView):
    model = Follower
    paginate_by = 100
    template_name = "follows/following_list.html"

    def get_queryset(self):
        username = self.kwargs.get("username")
        qs = super().get_queryset()
        return qs.filter(user__username=username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["username"] = self.kwargs.get("username")
        return context


following_list_view = FollowingListView.as_view()


@login_required
@require_http_methods(["POST"])
def follow_user(request, username):
    current_user = request.user
    profile_user = get_object_or_404(User, username=username)

    if current_user.id == profile_user.id:
        raise PermissionDenied(_("You cannot follow yourself"))

    is_already_following = Follower.objects.filter(
        user=current_user,
        follow_to=profile_user,
    ).exists()

    if is_already_following:
        Follower.objects.filter(
            user=current_user,
            follow_to=profile_user,
        ).first().delete(soft=False)
    else:
        Follower.objects.create(user=current_user, follow_to=profile_user)
        notify.send(
            sender=current_user,
            recipient=profile_user,
            verb=gettext_noop("followed you"),
            action_object=current_user,
            notification_type="new_follower",
        )

    return redirect(reverse_lazy("users:detail", kwargs={"username": username}))
