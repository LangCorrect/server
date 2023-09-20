from django.urls import path

from langcorrect.prompts.views import prompt_create_view, prompt_detail_view, prompt_list_view, user_prompts_view

app_name = "prompts"
urlpatterns = [
    path("", view=prompt_list_view, name="list"),
    path("~create/", view=prompt_create_view, name="create"),
    path("<str:slug>/", view=prompt_detail_view, name="detail"),
    path("me", view=user_prompts_view, name="user_prompts"),
]
