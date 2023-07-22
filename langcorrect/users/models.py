from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from config.settings.base import AVATAR_BASE_URL


class GenderChoices(models.TextChoices):
    MALE = "M", _("Male")
    FEMALE = "F", _("Female")
    OTHER = "O", _("Other")
    UNKNOWN = "U", _("Prefer not to say")


class User(AbstractUser):
    """
    Default custom user model for LangCorrect.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    gender = models.CharField(choices=GenderChoices.choices, default=GenderChoices.UNKNOWN, max_length=1)
    nick_name = models.CharField(_("Nick name"), max_length=26, null=True, blank=True)
    bio = models.TextField(_("Bio"), max_length=2000, blank=True, default="")
    staff_notes = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_volunteer = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    is_moderator = models.BooleanField(default=False)
    is_lifetime_vip = models.BooleanField(default=False)
    is_max_studying = models.BooleanField(default=False)

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})

    def _build_avatar_url(self, size=None):
        base_url = f"{AVATAR_BASE_URL}{self.username}"
        if size:
            base_url += f"&size={size}"
        if self.is_premium:
            base_url += "&background=FF9066&color=ffffff"
        return base_url

    @property
    def avatar(self):
        return self._build_avatar_url(size=40)

    @property
    def following_users(self):
        return User.objects.filter(follow_to__user=self)
