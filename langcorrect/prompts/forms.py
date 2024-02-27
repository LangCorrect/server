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
        max_length = 20
        if tags:
            tags = [t.lower().replace("#", "") for t in tags]

        for tag in tags:
            if len(tag) > max_length:
                msg = _("Tags cannot be longer than %s characters") % max_length
                raise forms.ValidationError(msg)

        return tags
