from django.urls import path

from langcorrect.follows.views import follower_list_view, following_list_view
from langcorrect.users.views import user_detail_view, user_redirect_view, user_update_view

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<str:username>/", view=user_detail_view, name="detail"),
    path("<str:username>/followers/", view=follower_list_view, name="followers"),
    path("<str:username>/following/", view=following_list_view, name="following"),
]
