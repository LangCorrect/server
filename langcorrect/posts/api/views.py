from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_noop
from notifications.signals import notify
from rest_framework import generics, status
from rest_framework.response import Response

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
        error_message = serializer.errors.get("text")
        return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_recipients(self, serializer):
        recipients = {reply.user for reply in PostReply.available_objects.filter(post=serializer.instance.post)}
        recipients.add(serializer.instance.post.user)
        corrector = get_object_or_404(User, username=self.request.data.get("recipient"))
        recipients.add(corrector)
        recipients.discard(serializer.instance.user)
        return recipients
