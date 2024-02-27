from django.urls import path

from langcorrect.corrections.views import export_corrections
from langcorrect.corrections.views import make_corrections
from langcorrect.posts.api.views import PostReplyCreateUpdateAPIView
from langcorrect.posts.views import post_create_view
from langcorrect.posts.views import post_delete_view
from langcorrect.posts.views import post_detail_view
from langcorrect.posts.views import post_list_view
from langcorrect.posts.views import post_update_view

app_name = "posts"
urlpatterns = [
    path("", view=post_list_view, name="list"),
    path("~create/", view=post_create_view, name="create"),
    path(
        "~create/<slug:prompt_slug>/",
        view=post_create_view,
        name="create-prompt-based-post",
    ),
    path(
        "~post_reply/",
        PostReplyCreateUpdateAPIView.as_view(),
        name="create-update-reply",
    ),
    path("<str:slug>/", view=post_detail_view, name="detail"),
    path("<str:slug>/update/", view=post_update_view, name="update"),
    path("<str:slug>/delete/", view=post_delete_view, name="delete"),
    path("<str:slug>/make_corrections", make_corrections, name="make-corrections"),
    path(
        "<str:slug>/export_corrections",
        export_corrections,
        name="export-corrections",
    ),
]
