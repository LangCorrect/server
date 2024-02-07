from django.contrib.auth import get_user_model

from langcorrect.chats.models import Dialogs, Message

User = get_user_model()


def serialize_message_model(m: Message, user_id):
    sender_pk = m.sender.pk
    is_out = sender_pk == user_id
    obj = {
        "id": m.id,
        "text": m.text,
        "sent": int(m.created.timestamp()),
        "edited": int(m.modified.timestamp()),
        "read": m.read,
        "sender": str(sender_pk),
        "recipient": str(m.recipient.pk),
        "out": is_out,
        "sender_username": m.sender.get_username(),
    }
    return obj


def serialize_dialog_model(m: Dialogs, user_id):
    username_field = User.USERNAME_FIELD
    other_user_pk, other_user_username = (
        User.objects.filter(pk=m.user1.pk).values_list("pk", username_field).first()
        if m.user2.pk == user_id
        else User.objects.filter(pk=m.user2.pk).values_list("pk", username_field).first()
    )
    unread_count = Message.get_unread_count_for_dialog_with_user(sender=other_user_pk, recipient=user_id)
    last_message = Message.get_last_message_for_dialog(sender=other_user_pk, recipient=user_id)
    last_message_ser = serialize_message_model(last_message, user_id) if last_message else None
    obj = {
        "id": m.id,
        "created": int(m.created.timestamp()),
        "modified": int(m.modified.timestamp()),
        "other_user_id": str(other_user_pk),
        "unread_count": unread_count,
        "username": other_user_username,
        "last_message": last_message_ser,
    }
    return obj
