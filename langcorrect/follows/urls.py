from django.urls import path

from langcorrect.follows.views import follow_user

app_name = "follows"

urlpatterns = [
    path("<str:username>/follow", follow_user, name="follow_user"),
]
