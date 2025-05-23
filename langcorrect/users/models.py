# ruff: noqa: DJ001
import uuid

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from config.settings.base import AVATAR_BASE_URL
from langcorrect.contributions.models import Contribution
from langcorrect.corrections.models import PostCorrection
from langcorrect.languages.models import Language
from langcorrect.languages.models import LevelChoices

CANNOT_DELETE_SYSTEM_USER_ERR_MSG = "System user cannot be deleted."


class ActiveUserManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class AllUserManager(UserManager):
    pass


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

    gender = models.CharField(
        choices=GenderChoices.choices,
        default=GenderChoices.UNKNOWN,
        max_length=1,
    )
    nick_name = models.CharField(_("Nick name"), max_length=26, null=True, blank=True)
    bio = models.TextField(_("Bio"), max_length=2000, blank=True, default="")
    staff_notes = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_volunteer = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    is_moderator = models.BooleanField(default=False)
    is_lifetime_vip = models.BooleanField(default=False)
    is_max_studying = models.BooleanField(default=False)
    is_system = models.BooleanField(default=False)
    uuid = models.UUIDField(null=True, blank=True, default=uuid.uuid4, editable=False)

    objects = ActiveUserManager()
    all_objects = AllUserManager()

    def delete(self, *args, **kwargs):
        if self.is_system:
            raise PermissionDenied(CANNOT_DELETE_SYSTEM_USER_ERR_MSG)
        return super().delete(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})

    def _build_avatar_url(self, size=None):
        base_url = f"{AVATAR_BASE_URL}{self.display_name}"

        if size:
            base_url += f"&size={size}"
        if self.is_premium_user:
            base_url += "&background=FF9066&color=ffffff"
        return base_url

    @property
    def avatar(self):
        return self._build_avatar_url(size=40)

    @property
    def following_users(self):
        return User.objects.filter(follower__user=self)

    @property
    def get_following_users_ids(self):
        return list(self.follower.values_list("follow_to", flat=True))

    @property
    def followers_users(self):
        return User.objects.filter(follower__follow_to=self)

    @property
    def native_languages(self):
        lang_codes = self.languagelevel_set.filter(
            level=LevelChoices.NATIVE,
        ).values_list("language__code", flat=True)
        return Language.objects.filter(code__in=lang_codes)

    @property
    def studying_languages(self):
        lang_codes = (
            self.languagelevel_set.filter(user=self)
            .exclude(level=LevelChoices.NATIVE)
            .values_list("language__code", flat=True)
        )
        return Language.objects.filter(code__in=lang_codes)

    @property
    def all_languages(self):
        return self.native_languages | self.studying_languages

    @property
    def corrections_made_count(self):
        return PostCorrection.available_objects.filter(
            user_correction__user=self,
        ).count()

    @property
    def corrections_received_count(self):
        return PostCorrection.available_objects.filter(
            post_row__post__user=self,
        ).count()

    @property
    def correction_ratio(self):
        total_written_sentences = self.postrow_set.count()

        try:
            return round(
                self.corrections_made_count / total_written_sentences,
                2,
            )
        except ZeroDivisionError:
            return "∞"

    @property
    def is_premium_user(self):
        if hasattr(self, "stripecustomer"):
            stripe_customer = self.stripecustomer
            return stripe_customer.has_active_subscription or (
                stripe_customer.premium_until
                and stripe_customer.premium_until > timezone.now()
            )
        return False

    @property
    def writing_streak(self):
        return self.contribution.writing_streak

    @property
    def display_name(self):
        return self.nick_name if self.nick_name else self.username


@receiver(post_save, sender=User)
def create_contribution_user(sender, instance, created, **kwargs):
    if created:
        Contribution.objects.create(user=instance)
