import re

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from taggit.serializers import TaggitSerializer
from taggit.serializers import TagListSerializerField

from langcorrect.languages.serializers import LanguageSerializer
from langcorrect.posts.models import Post
from langcorrect.posts.models import PostReply
from langcorrect.users.api.serializers import BasicUserSerializer
from langcorrect.users.models import User


class PostSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    language = LanguageSerializer()
    user = BasicUserSerializer()

    class Meta:
        model = Post
        fields = [
            "created",
            "modified",
            "title",
            "text",
            "native_text",
            "gender_of_narration",
            "slug",
            "language_level",
            "is_corrected",
            "language",
            "permission",
            "user",
            "tags",
        ]


class PostReplySerializer(serializers.ModelSerializer):
    author = serializers.CharField(read_only=True, source="user.username")
    recipient = serializers.SerializerMethodField()
    post = serializers.SerializerMethodField()

    class Meta:
        model = PostReply
        fields = ["id", "text", "created", "modified", "author", "recipient", "post"]

    def _clean_string(self, s):
        s = s.strip()
        # Replace multiple spaces/tabs with a single space
        s = re.sub(r"[ \t]+", " ", s)
        # Replace more than two consecutive newlines with two newlines
        return re.sub(r"\n{3,}", "\n\n", s)

    def validate_text(self, obj):
        min_length = 10
        err_msg = f"Message needs to be at least {min_length} characters long"

        # Replace all whitespace with a single space
        text_length = re.sub(r"\s+", " ", obj)
        if len(text_length) < min_length:
            raise serializers.ValidationError(err_msg)
        return self._clean_string(obj)

    def get_recipient(self, obj):
        return obj.recipient.username

    def get_post(self, obj):
        return obj.post.slug

    def create(self, validated_data):
        recipient_username = self.context["request"].data.get("recipient")
        post_slug = self.context["request"].data.get("post")

        recipient = get_object_or_404(User, username=recipient_username)
        post = get_object_or_404(Post, slug=post_slug)

        validated_data["recipient"] = recipient
        validated_data["post"] = post
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("recipient", None)
        return super().update(instance, validated_data)
