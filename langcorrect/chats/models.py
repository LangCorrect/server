from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from model_utils.models import SoftDeletableModel, TimeStampedModel


class Dialogs(TimeStampedModel):
    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("User1"), related_name="+", db_index=True
    )
    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("User2"), related_name="+", db_index=True
    )

    class Meta:
        unique_together = (("user1", "user2"), ("user2", "user1"))
        verbose_name = _("Dialog")
        verbose_name_plural = _("Dialogs")

    def __str__(self):
        return _("Dialog between ") + f"{self.user1_id}, {self.user2_id}"

    @staticmethod
    def dialog_exists(u1: AbstractBaseUser, u2: AbstractBaseUser):
        return Dialogs.objects.filter(Q(user1=u1, user2=u2) | Q(user1=u2, user2=u1)).first()

    @staticmethod
    def create_if_not_exists(u1: AbstractBaseUser, u2: AbstractBaseUser):
        res = Dialogs.dialog_exists(u1, u2)
        if not res:
            Dialogs.objects.create(user1=u1, user2=u2)

    @staticmethod
    def get_dialogs_for_user(user: AbstractBaseUser):
        return Dialogs.objects.filter(Q(user1=user) | Q(user2=user)).values_list("user1__pk", "user2__pk")


class Message(TimeStampedModel, SoftDeletableModel):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Author"),
        related_name="from_user",
        db_index=True,
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Recipient"),
        related_name="to_user",
        db_index=True,
    )
    text = models.TextField(verbose_name=_("Text"), blank=True)

    read = models.BooleanField(verbose_name=_("Read"), default=False)
    all_objects = models.Manager()

    @staticmethod
    def get_unread_count_for_dialog_with_user(sender, recipient):
        return Message.objects.filter(sender_id=sender, recipient_id=recipient, read=False).count()

    @staticmethod
    def get_last_message_for_dialog(sender, recipient):
        return (
            Message.objects.filter(
                Q(sender_id=sender, recipient_id=recipient) | Q(sender_id=recipient, recipient_id=sender)
            )
            .select_related("sender", "recipient")
            .first()
        )

    def __str__(self):
        return str(self.pk)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Dialogs.create_if_not_exists(self.sender, self.recipient)

    class Meta:
        ordering = ("-created",)
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")
