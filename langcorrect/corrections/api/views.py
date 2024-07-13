from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

from langcorrect.constants import NotificationTypes
from langcorrect.corrections.api.serializers import CommentSerializer
from langcorrect.corrections.models import Comment
from langcorrect.helpers import create_notification

User = get_user_model()


class CommentCreateUpdateAPIView(generics.GenericAPIView):
    queryset = Comment.available_objects.all()
    serializer_class = CommentSerializer

    def get_recipients(self, comment):
        post_user_correction = comment.user_correction
        comment_author = comment.user

        recipients = (
            User.objects.filter(
                comment__user_correction=post_user_correction,
            )
            .exclude(id=comment_author.id)
            .distinct()
        )

        recipients_set = set(recipients)

        post_author = post_user_correction.post.user
        if post_author.id != comment_author.id:
            recipients_set.add(post_author)

        user_correction_author = post_user_correction.user
        if user_correction_author.id != comment_author.id:
            recipients_set.add(user_correction_author)

        return list(recipients_set)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            recipients = self.get_recipients(serializer.instance)

            create_notification(
                serializer.instance.user,
                recipients,
                serializer.instance.user_correction.post,
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
