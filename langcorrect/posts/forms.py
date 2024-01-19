from django import forms
from django.utils.translation import gettext_lazy as _

from langcorrect.posts.models import Post
from langcorrect.posts.validators import validate_image_size, validate_jpeg_extension


class CustomPostForm(forms.ModelForm):
    image = forms.ImageField(required=False, validators=[validate_jpeg_extension, validate_image_size])

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
        if not self.user.is_premium_user:
            self.fields["image"].disabled = True
            self.fields["image"].label = _("Image (Premium Feature)")
        else:
            self.fields["image"].label = _("Image (JPEG, JPG, <5MB)")

    def clean_text(self):
        text = self.cleaned_data["text"].strip()

        if text and len(text) < 50:
            msg = _(f"You need to write {50 - len(text)} more characters to meet the minimum requirement.")
            raise forms.ValidationError(msg)
        return text

    def clean_tags(self):
        tags = self.cleaned_data.get("tags", None)
        if tags:
            tags = [t.lower().replace("#", "") for t in tags]

        for tag in tags:
            if len(tag) > 20:
                msg = _("Tags cannot be longer than 20 characters")
                raise forms.ValidationError(msg)

        return tags
