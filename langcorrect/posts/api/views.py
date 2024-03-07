from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils.translation import gettext_noop
from notifications.signals import notify
from rest_framework import generics
from rest_framework import mixins
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from config.api.permissions import CanViewPost, IsOwnerOrStaff
from langcorrect.posts.api.serializers import PostReplySerializer
from langcorrect.posts.api.serializers import PostSerializer
from langcorrect.posts.models import Post
from langcorrect.posts.models import PostReply
from langcorrect.posts.models import PostVisibility

User = get_user_model()


class PostListViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = PostSerializer
    queryset = Post.available_objects.all()

    def get_permissions(self):
        if self.request.method == "POST":
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = (
            Post.available_objects.select_related("user", "language")
            .prefetch_related("tags")
            .all()
        )
        current_user = self.request.user

        if current_user.is_anonymous:
            queryset = queryset.filter(
                permission=PostVisibility.PUBLIC,
                is_corrected=True,
            )
        else:
            queryset = queryset.filter(language__in=current_user.native_languages)

        search = self.request.query_params.get("search")
        langs = self.request.query_params.get("langs")

        if search:
            queryset = queryset.filter(title__icontains=search)

        if langs:
            codes = langs.split(",")
            queryset = queryset.filter(language__code__in=codes)

        return queryset


class PostDetailViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = PostSerializer
    queryset = Post.available_objects.all()
    lookup_field = "slug"

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            permission_classes = [IsOwnerOrStaff]
        else:
            permission_classes = [CanViewPost]

        return [permission() for permission in permission_classes]


class PostReplyCreateUpdateAPIView(generics.GenericAPIView):
    # TODO: Implement other HTTP methods
    queryset = PostReply.available_objects.all()
    serializer_class = PostReplySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            post = serializer.instance.post
            reply_author = serializer.instance.user

            recipients = self.get_recipients(serializer)

            notify.send(
                sender=reply_author,
                recipient=list(recipients),
                verb=gettext_noop("replied on"),
                action_object=post,
                notification_type="new_reply",
            )

            return render(
                request,
                "posts/partials/post_reply_card.html",
                {
                    "user": serializer.instance.user,
                    "created": serializer.instance.created,
                    "instance": serializer.instance,
                },
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_recipients(self, serializer):
        recipients = {
            reply.user
            for reply in PostReply.available_objects.filter(
                post=serializer.instance.post,
            )
        }
        recipients.add(serializer.instance.post.user)
        corrector = get_object_or_404(User, username=self.request.data.get("recipient"))
        recipients.add(corrector)
        recipients.discard(serializer.instance.user)
        return recipients
