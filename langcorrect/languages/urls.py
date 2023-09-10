from django.urls import path

from langcorrect.languages.views import (
    language_level_create_view,
    language_level_delete_view,
    language_level_list_view,
    language_level_update_view,
)

app_name = "languages"

urlpatterns = [
    path("", view=language_level_list_view, name="list"),
    path("~create/", view=language_level_create_view, name="create"),
    path("<int:pk>/", view=language_level_update_view, name="update"),
    path("<int:pk>/delete/", view=language_level_delete_view, name="delete"),
]
