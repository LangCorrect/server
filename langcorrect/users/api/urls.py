from django.urls import path

from langcorrect.users.api.views import UserPostsListAPIView
from langcorrect.users.api.views import UserPromptsListAPIView

urlpatterns = [
    path(
        "<str:username>/posts",
        view=UserPostsListAPIView.as_view(),
        name="user-posts-list",
    ),
    path(
        "<str:username>/prompts",
        view=UserPromptsListAPIView.as_view(),
        name="user-prompts-list",
    ),
]
