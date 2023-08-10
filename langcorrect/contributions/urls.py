from django.urls import path

from langcorrect.contributions.views import get_contributions

urlpatterns = [
    path("<str:username>/", get_contributions),
]
