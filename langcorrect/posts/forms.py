from django import forms
from django.utils.translation import gettext_lazy as _

from langcorrect.posts.models import Post
from langcorrect.posts.validators import validate_image_size
from langcorrect.posts.validators import validate_jpeg_extension
from langcorrect.posts.validators import validate_text_length


class CustomPostForm(forms.ModelForm):
    image = forms.ImageField(
        required=False,
        validators=[validate_jpeg_extension, validate_image_size],
    )
    text = forms.CharField(validators=[validate_text_length])

    class Meta:
        model = Post
        fields = [
            "title",
            "text",
            "native_text",
            "language",
            "gender_of_narration",
            "permission",
            "tags",
        ]

    def __init__(self, user, *args, is_convert_prompt=False, **kwargs):
        self.user = user
        self.is_convert_prompt = is_convert_prompt
        super().__init__(*args, **kwargs)

        self.fields["native_text"].required = False
        self.fields["language"].queryset = self.user.studying_languages

        if self.instance.is_corrected:
            self.fields["text"].disabled = True
        if not self.user.is_premium_user:
            self.fields["image"].disabled = True
        if self.is_convert_prompt:
            self.fields["language"].queryset = self.user.all_languages

    def clean_tags(self):
        tags = self.cleaned_data.get("tags", None)
        if tags:
            tags = [t.lower().replace("#", "") for t in tags]

        for tag in tags:
            max_char_count = 20
            if len(tag) > max_char_count:
                msg = _("Tags cannot be longer than %s characters") % max_char_count
                raise forms.ValidationError(msg)

        return tags
