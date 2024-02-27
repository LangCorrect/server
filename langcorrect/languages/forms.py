from django import forms
from django.core.exceptions import ValidationError

from langcorrect.languages.models import LanguageLevel
from langcorrect.languages.models import LevelChoices


class LanguageLevelForm(forms.ModelForm):
    class Meta:
        model = LanguageLevel
        fields = ["language", "level"]

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            level_choices = tuple(
                choice
                for choice in LevelChoices.choices
                if choice[0] != LevelChoices.NATIVE
            )
            self.fields["level"].choices = level_choices
            self.fields["language"].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        level = cleaned_data.get("level")
        language = cleaned_data.get("language")

        existing_native_languages = self.user.native_languages
        existing_studying_languages = self.user.studying_languages
        existing_languages = existing_native_languages | existing_studying_languages

        max_native_languages = 3
        max_studying_languages = 10 if self.user.is_premium_user else 2

        native_lang_error_msg = (
            f"You cannot have more than {max_native_languages} native languages."  # ruff: E501
        )
        studying_lang_error_msg = (
            f"You cannot have more than {max_studying_languages} studying languages."  # ruff: E501
        )
        dupe_lang_err_msg = "You cannot have duplicate languages."

        if self.instance and self.instance.pk:
            pass
        else:
            if language in existing_languages:
                raise ValidationError(dupe_lang_err_msg)

            if level == LevelChoices.NATIVE:
                if existing_native_languages.count() >= max_native_languages:
                    raise ValidationError(native_lang_error_msg)

            if level != LevelChoices.NATIVE:
                if existing_studying_languages.count() >= max_studying_languages:
                    raise ValidationError(studying_lang_error_msg)
