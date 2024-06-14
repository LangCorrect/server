from rest_framework import serializers

from langcorrect.languages.models import Language


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = [
            "en_name",
            "family_code",
            "code",
        ]
        read_only_fields = ["en_name", "family_code", "code"]
