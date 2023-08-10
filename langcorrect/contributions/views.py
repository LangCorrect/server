from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from langcorrect.contributions.helpers import get_contribution_data

User = get_user_model()


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def get_contributions(request, username):
    user = get_object_or_404(User, username=username)
    data = get_contribution_data(user)
    return Response(data=data)
