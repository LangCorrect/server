from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from langcorrect.posts.api.serializers import PostSerializer
from langcorrect.posts.models import Post
from langcorrect.posts.models import PostVisibility
from langcorrect.prompts.models import Prompt
from langcorrect.prompts.serializers import PromptSerializer

from .serializers import UserSerializer

User = get_user_model()


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "username"

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False)
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class UserPostsListAPIView(ListAPIView):
    serializer_class = PostSerializer
    queryset = Post.available_objects.all()
    permission_classes = []

    def get_queryset(self):
        author = self.kwargs.get("username")
        current_user = self.request.user
        queryset = (
            self.queryset.filter(user__username=author)
            .select_related("user", "language")
            .prefetch_related("tags")
        )
        if current_user.is_anonymous:
            queryset = queryset.filter(permission=PostVisibility.PUBLIC)

        return queryset


class UserPromptsListAPIView(ListAPIView):
    serializer_class = PromptSerializer
    queryset = Prompt.available_objects.all()
    permission_classes = []

    def get_queryset(self):
        author = self.kwargs.get("username")
        return (
            self.queryset.filter(user__username=author)
            .select_related("user")
            .prefetch_related("tags")
        )
