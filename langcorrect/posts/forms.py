from django import forms
from django.utils.translation import gettext_lazy as _

from langcorrect.posts.models import Post


class CustomPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "text", "native_text", "language", "gender_of_narration", "permission", "tags"]

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

        self.fields["native_text"].required = False
        self.fields["language"].queryset = self.user.studying_languages
        if self.instance.is_corrected:
            self.fields["text"].disabled = True

    def clean_text(self):
        text = self.cleaned_data["text"]
        if text and len(text) < 50:
            msg = _(f"You need to write {50 - len(text)} more characters to meet the minimum requirement.")
            raise forms.ValidationError(msg)
        return self.cleaned_data["text"]

    def clean_tags(self):
        tags = self.cleaned_data.get("tags", None)
        if tags:
            tags = [t.lower().replace("#", "") for t in tags]

        for tag in tags:
            if len(tag) > 20:
                msg = _("Tags cannot be longer than 20 characters")
                raise forms.ValidationError(msg)

        return tags
