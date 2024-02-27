from django.urls import path

from langcorrect.prompts.views import convert_prompt_to_journal_entry
from langcorrect.prompts.views import prompt_create_view
from langcorrect.prompts.views import prompt_detail_view
from langcorrect.prompts.views import prompt_list_view

app_name = "prompts"
urlpatterns = [
    path("", view=prompt_list_view, name="list"),
    path("~create/", view=prompt_create_view, name="create"),
    path("<str:slug>/", view=prompt_detail_view, name="detail"),
    path(
        "convert_to_journal/<str:slug>/",
        convert_prompt_to_journal_entry,
        name="convert_to_journal",
    ),
]
