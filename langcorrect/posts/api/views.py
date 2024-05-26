from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

from langcorrect.corrections.constants import NotificationTypes
from langcorrect.corrections.helpers import create_notification
from langcorrect.posts.api.serializers import PostReplySerializer
from langcorrect.posts.models import PostReply

User = get_user_model()


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

            create_notification(
                reply_author,
                list(recipients),
                post,
                NotificationTypes.NEW_REPLY,
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
