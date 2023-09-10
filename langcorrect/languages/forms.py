from django import forms
from django.core.exceptions import ValidationError

from langcorrect.languages.models import LanguageLevel, LevelChoices


class LanguageLevelForm(forms.ModelForm):
    class Meta:
        model = LanguageLevel
        fields = ["language", "level"]

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            level_choices = tuple(choice for choice in LevelChoices.choices if choice[0] != LevelChoices.NATIVE)
            self.fields["level"].choices = level_choices
            self.fields["language"].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        level = cleaned_data.get("level")
        language = cleaned_data.get("language")

        existing_native_languages = self.user.native_languages
        existing_studying_languages = self.user.studying_languages
        existing_languages = existing_native_languages | existing_studying_languages

        if self.instance and self.instance.pk:
            pass
        else:
            if language in existing_languages:
                raise ValidationError("You cannot have duplicate languages.")

            MAX_NATIVE_LANGUAGES = 3
            MAX_STUDYING_LANGUAGES = 10 if self.user.is_premium_user else 2

            if level == LevelChoices.NATIVE:
                if existing_native_languages.count() >= MAX_NATIVE_LANGUAGES:
                    raise ValidationError(f"You cannot have more than {MAX_NATIVE_LANGUAGES} native languages.")

            if level != LevelChoices.NATIVE:
                if existing_studying_languages.count() >= MAX_STUDYING_LANGUAGES:
                    raise ValidationError(f"You cannot have more than {MAX_STUDYING_LANGUAGES} studying languages.")
