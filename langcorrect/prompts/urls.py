from django.urls import path

from langcorrect.prompts.views import prompt_detail_view, prompt_list_view

app_name = "prompts"
urlpatterns = [
    path("", view=prompt_list_view, name="list"),
    path("<str:slug>/", view=prompt_detail_view, name="detail"),
]
