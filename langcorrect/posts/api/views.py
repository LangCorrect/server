from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response

from langcorrect.posts.api.serializers import PostReplySerializer
from langcorrect.posts.models import PostReply


class PostReplyCreateUpdateAPIView(generics.GenericAPIView):
    queryset = PostReply.available_objects.all()
    serializer_class = PostReplySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
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

    # def put(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data)
    #     if serializer.is_valid():
    #         self.perform_update(serializer)
    #         return render(request, 'path_to_your_template.html', {'post_reply': serializer.instance})
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def perform_update(self, serializer):
    #     serializer.save()
