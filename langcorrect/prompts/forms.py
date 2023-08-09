from django import forms
from django.utils.translation import gettext_lazy as _

from langcorrect.prompts.models import Prompt


class CustomPromptForm(forms.ModelForm):
    class Meta:
        model = Prompt
        fields = ["content", "language", "difficulty_level", "tags"]

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

        self.fields["language"].queryset = self.user.native_languages

    def clean_tags(self):
        tags = self.cleaned_data.get("tags", None)
        if tags:
            tags = [t.lower().replace("#", "") for t in tags]

        for tag in tags:
            if len(tag) > 20:
                msg = _("Tags cannot be longer than 20 characters")
                raise forms.ValidationError(msg)

        return tags
