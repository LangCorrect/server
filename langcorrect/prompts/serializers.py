from rest_framework import serializers
from taggit.serializers import TagListSerializerField

from langcorrect.languages.serializers import LanguageSerializer
from langcorrect.posts.validators import validate_tags
from langcorrect.prompts.models import Prompt
from langcorrect.users.api.serializers import BasicUserSerializer


class BasePromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prompt
        fields = [
            "id",
            "created",
            "modified",
            "content",
            "difficulty_level",
            "language",
            "slug",
            "tags",
            "response_count",
            "user",
        ]
        read_only_fields = [
            "slug",
            "created",
            "modified",
            "user",
        ]

    tags = TagListSerializerField(validators=[validate_tags])
    language = LanguageSerializer(read_only=True)
    user = BasicUserSerializer(read_only=True)
    response_count = serializers.SerializerMethodField()

    def get_response_count(self, obj):
        return obj.response_count


class PromptSerializer(BasePromptSerializer):
    pass
