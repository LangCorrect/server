from django.urls import path

from langcorrect.chats.consumers.chat_consumer import ChatConsumer
from langcorrect.chats.views import (
    ChatHome,
    DialogsList,
    MarkAllMessagesAsRead,
    MessagesList,
    SelfInfoView,
    UsersListView,
)

app_name = "chats"

websocket_urlpatterns = [
    path("chat_ws", ChatConsumer.as_asgi()),
]

urlpatterns = [
    path("", ChatHome.as_view(), name="index"),
    path("messages/", MessagesList.as_view(), name="all_messages_list"),
    path("messages/<dialog_with>/", MessagesList.as_view(), name="messages_list"),
    path("messages/<dialog_with>/mark-all-read", MarkAllMessagesAsRead.as_view()),
    path("dialogs/", DialogsList.as_view(), name="dialogs_list"),
    path("self/", SelfInfoView.as_view(), name="self_info"),
    path("users/", UsersListView.as_view(), name="user_list"),
]
