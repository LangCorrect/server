from django.contrib.auth import get_user_model
from rest_framework import serializers

from langcorrect.users.models import User as UserType

User = get_user_model()


class UserSerializer(serializers.ModelSerializer[UserType]):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "url"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "username"},
        }


class BasicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "display_name",
            "is_premium_user",
            "writing_streak",
            "avatar",
        ]
