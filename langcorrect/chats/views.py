from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AbstractBaseUser
from django.core.paginator import Page, Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import DetailView, ListView, TemplateView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from langcorrect.chats.models import Dialogs, Message
from langcorrect.chats.serializers import serialize_dialog_model, serialize_message_model

User = get_user_model()


class MarkAllMessagesAsRead(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        dialog_with = self.kwargs.get("dialog_with")
        Message.objects.filter(recipient_id=self.request.user.id, sender=dialog_with).update(read=True)
        return Response({}, status=status.HTTP_200_OK)


class ChatHome(LoginRequiredMixin, TemplateView):
    template_name = "chats/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["disable_page_container"] = True
        return context


class UsersListView(LoginRequiredMixin, ListView):
    http_method_names = [
        "get",
    ]

    def get_queryset(self):
        return User.objects.filter(id__in=self.request.user.get_following_users_ids)

    def render_to_response(self, context, **response_kwargs):
        users = context["object_list"]

        data = [{"username": user.get_username(), "pk": str(user.pk)} for user in users]
        return JsonResponse(data, safe=False, **response_kwargs)


class MessagesList(LoginRequiredMixin, ListView):
    http_method_names = [
        "get",
    ]
    paginate_by = getattr(settings, "MESSAGES_PAGINATION", 500)

    def get_queryset(self):
        if self.kwargs.get("dialog_with"):
            qs = Message.objects.filter(
                Q(recipient=self.request.user, sender=self.kwargs["dialog_with"])
                | Q(sender=self.request.user, recipient=self.kwargs["dialog_with"])
            ).select_related("sender", "recipient")
        else:
            qs = Message.objects.filter(Q(recipient=self.request.user) | Q(sender=self.request.user)).prefetch_related(
                "sender",
                "recipient",
            )

        return qs.order_by("-created")

    def render_to_response(self, context, **response_kwargs):
        user_pk = self.request.user.pk
        data = [serialize_message_model(i, user_pk) for i in context["object_list"]]
        page: Page = context.pop("page_obj")
        paginator: Paginator = context.pop("paginator")
        return_data = {"page": page.number, "pages": paginator.num_pages, "data": data}
        return JsonResponse(return_data, **response_kwargs)


class DialogsList(LoginRequiredMixin, ListView):
    http_method_names = [
        "get",
    ]
    paginate_by = getattr(settings, "DIALOGS_PAGINATION", 20)

    def get_queryset(self):
        qs = Dialogs.objects.filter(
            Q(user1_id=self.request.user.pk) | Q(user2_id=self.request.user.pk)
        ).select_related("user1", "user2")
        return qs.order_by("-created")

    def render_to_response(self, context, **response_kwargs):
        # TODO: add online status
        user_pk = self.request.user.pk
        data = [serialize_dialog_model(i, user_pk) for i in context["object_list"]]
        page: Page = context.pop("page_obj")
        paginator: Paginator = context.pop("paginator")
        return_data = {"page": page.number, "pages": paginator.num_pages, "data": data}
        return JsonResponse(return_data, **response_kwargs)


class SelfInfoView(LoginRequiredMixin, DetailView):
    def get_object(self, queryset=None):
        return self.request.user

    def render_to_response(self, context, **response_kwargs):
        user: AbstractBaseUser = context["object"]
        data = {"username": user.get_username(), "pk": str(user.pk)}
        return JsonResponse(data, **response_kwargs)
