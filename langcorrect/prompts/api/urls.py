from django.urls import path

from langcorrect.prompts.api.views import PromptListCreateAPIView
from langcorrect.prompts.api.views import PromptRetrieveUpdateDestroyAPIView

urlpatterns = [
    path("", view=PromptListCreateAPIView.as_view(), name="prompt-list-create"),
    path(
        "<str:slug>/",
        view=PromptRetrieveUpdateDestroyAPIView.as_view(),
        name="prompt-detail",
    ),
]
