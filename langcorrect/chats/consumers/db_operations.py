from collections.abc import Awaitable

from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser

from langcorrect.chats.models import Dialogs, Message

User = get_user_model()


@database_sync_to_async
def get_groups_to_add(u: AbstractBaseUser) -> Awaitable[set[int]]:
    l = Dialogs.get_dialogs_for_user(u)  # noqa: E741
    return set(list(sum(l, ())))


@database_sync_to_async
def get_user_by_pk(pk: str) -> Awaitable[AbstractBaseUser | None]:
    return User.objects.filter(pk=pk).first()


@database_sync_to_async
def get_message_by_id(mid: int) -> Awaitable[tuple[str, str] | None]:
    msg: Message | None = Message.objects.filter(id=mid).first()
    if msg:
        return str(msg.recipient.pk), str(msg.sender.pk)
    else:
        return None


# @database_sync_to_async
# def mark_message_as_read(mid: int, sender_pk: str, recipient_pk: str):
#     return Message.objects.filter(id__lte=mid,sender_id=sender_pk, recipient_id=recipient_pk).update(read=True)


@database_sync_to_async
def mark_message_as_read(mid: int) -> Awaitable[None]:
    return Message.objects.filter(id=mid).update(read=True)


@database_sync_to_async
def get_unread_count(sender, recipient) -> Awaitable[int]:
    return int(Message.get_unread_count_for_dialog_with_user(sender, recipient))


@database_sync_to_async
def save_text_message(text: str, from_: AbstractBaseUser, to: AbstractBaseUser) -> Awaitable[Message]:
    return Message.objects.create(text=text, sender=from_, recipient=to)
