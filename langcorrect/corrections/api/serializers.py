import re

from rest_framework import serializers

from langcorrect.corrections.models import Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            "text",
            "user_correction",
        ]
        read_only_fields = [
            "id",
            "created",
            "modified",
            "user",
        ]

    def _clean_string(self, s):
        s = s.strip()
        # Replace multiple spaces/tabs with a single space
        s = re.sub(r"[ \t]+", " ", s)
        # Replace more than two consecutive newlines with two newlines
        return re.sub(r"\n{3,}", "\n\n", s)

    def validate_text(self, obj):
        min_length = 1
        err_msg = f"Message needs to be at least {min_length} characters long"

        # Replace all whitespace with a single space
        text_length = re.sub(r"\s+", " ", obj)
        if len(text_length) < min_length:
            raise serializers.ValidationError(err_msg)
        return self._clean_string(obj)
