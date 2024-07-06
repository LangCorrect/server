from django.utils.translation import gettext_noop
from notifications.signals import notify

from langcorrect.constants import NotificationTypes
from langcorrect.users.models import User


def create_notification(
    sender: User | list[User],
    recipient: User,
    action_object: any,
    n_type: NotificationTypes,
) -> None:
    match n_type:
        case NotificationTypes.NEW_CORRECTION:
            notify.send(
                sender=sender,
                recipient=recipient,
                verb=gettext_noop("corrected"),
                action_object=action_object,
                notification_type=NotificationTypes.NEW_CORRECTION,
            )
        case NotificationTypes.UPDATE_CORRECTION:
            notify.send(
                sender=sender,
                recipient=recipient,
                verb=gettext_noop("updated their corrections on"),
                action_object=action_object,
                notification_type=NotificationTypes.UPDATE_CORRECTION,
            )
        case NotificationTypes.NEW_COMMENT:
            notify.send(
                sender=sender,
                recipient=recipient,
                verb=gettext_noop("commented on"),
                action_object=action_object,
                notification_type=NotificationTypes.NEW_COMMENT,
            )
        case NotificationTypes.NEW_POST:
            notify.send(
                sender=sender,
                recipient=recipient,
                verb=gettext_noop("posted"),
                action_object=action_object,
                notification_type=NotificationTypes.NEW_POST,
            )
        case NotificationTypes.NEW_REPLY:
            notify.send(
                sender=sender,
                recipient=recipient,
                verb=gettext_noop("replied on"),
                action_object=action_object,
                notification_type=NotificationTypes.NEW_REPLY,
            )
        case NotificationTypes.NEW_FOLLOWER:
            notify.send(
                sender=sender,
                recipient=recipient,
                verb=gettext_noop("followed you"),
                action_object=action_object,
                notification_type=NotificationTypes.NEW_FOLLOWER,
            )
        case _:
            # TODO: add logger for non existant
            pass
