import re

from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django import forms as django_forms
from django.contrib.auth import forms as admin_forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from langcorrect.languages.models import Language
from langcorrect.languages.models import LanguageLevel
from langcorrect.languages.models import LevelChoices
from langcorrect.users.models import GenderChoices

User = get_user_model()


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User


class UserAdminCreationForm(admin_forms.UserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    class Meta(admin_forms.UserCreationForm.Meta):
        model = User
        error_messages = {
            "username": {"unique": _("This username has already been taken.")},
        }


class UserSignupForm(SignupForm):
    """
    Form that will be rendered on a user sign up section/screen.
    Default fields will be added automatically.
    Check UserSocialSignupForm for accounts created from social.
    """

    studying_level_options = list(LevelChoices.choices)[:-1]
    native_language = django_forms.ModelChoiceField(queryset=Language.objects.all())
    studying_language = django_forms.ModelChoiceField(queryset=Language.objects.all())
    studying_language_level = django_forms.ChoiceField(choices=studying_level_options)
    gender_of_narration = django_forms.ChoiceField(choices=GenderChoices.choices)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial["gender_of_narration"] = GenderChoices.UNKNOWN

    def clean_username(self):
        username = super().clean_username()
        err_msg = "Username can only contain letters, numbers, and underscores."

        if not re.match("^[a-zA-Z0-9_]+$", username):
            raise django_forms.ValidationError(err_msg)

        return username

    def clean(self):
        cleaned_data = super().clean()
        native_language = cleaned_data.get("native_language")
        studying_language = cleaned_data.get("studying_language")

        if native_language == studying_language:
            self.add_error(
                "studying_language",
                django_forms.ValidationError(
                    "Studying and native language cannot be the same",
                    code="dupe_languages",
                ),
            )
        return cleaned_data

    def save(self, request):
        user = super().save(request)
        native_language = self.cleaned_data.get("native_language")
        studying_language = self.cleaned_data.get("studying_language")
        studying_language_level = self.cleaned_data.get("studying_language_level")

        if user is None:
            return None

        # native
        LanguageLevel.objects.create(
            user=user,
            language=native_language,
            level=LevelChoices.NATIVE,
        )

        # studying
        LanguageLevel.objects.create(
            user=user,
            language=studying_language,
            level=studying_language_level,
        )

        user.gender = self.cleaned_data.get("gender_of_narration")
        user.save()

        return user


class UserSocialSignupForm(SocialSignupForm):
    """
    Renders the form when user has signed up using social accounts.
    Default fields will be added automatically.
    See UserSignupForm otherwise.
    """
