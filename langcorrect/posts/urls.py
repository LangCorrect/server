from django.urls import path

from langcorrect.posts.views import post_list_view

# from langcorrect.users.views import user_detail_view, user_redirect_view, user_update_view


app_name = "posts"
urlpatterns = [
    path("", view=post_list_view, name="list"),
    # path("~redirect/", view=user_redirect_view, name="redirect"),
    # path("~update/", view=user_update_view, name="update"),
    # path("<str:username>/", view=user_detail_view, name="detail"),
]
