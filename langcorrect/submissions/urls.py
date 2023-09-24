from django.urls import path

from langcorrect.submissions.views import post_list_view

app_name = "submissions"
urlpatterns = [
    path("posts/", view=post_list_view, name="list"),
]
