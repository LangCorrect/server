from rest_framework import serializers
from taggit.serializers import TagListSerializerField

from langcorrect.languages.models import Language
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

    tags = TagListSerializerField(validators=[validate_tags], required=False)
    language = LanguageSerializer(read_only=True)
    user = BasicUserSerializer(read_only=True)
    response_count = serializers.SerializerMethodField()

    def get_response_count(self, obj):
        return obj.response_count


class PromptSerializer(BasePromptSerializer):
    class Meta(BasePromptSerializer.Meta):
        fields = [*BasePromptSerializer.Meta.fields, "lang_code"]

    lang_code = serializers.CharField(write_only=True)

    def validate_lang_code(self, value):
        try:
            language = Language.objects.get(code=value)
        except Language.DoesNotExist as err:
            err_msg = "Invalid language code provided."
            raise serializers.ValidationError(err_msg) from err

        request = self.context.get("request")
        current_user = request.user
        if language not in current_user.all_languages:
            err_msg = "You can only post in languages you know."
            raise serializers.ValidationError(err_msg)

        return language

    def create(self, validated_data):
        language = validated_data.pop("lang_code")
        validated_data["language"] = language
        return super().create(validated_data)
