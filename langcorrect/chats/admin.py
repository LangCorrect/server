from django.contrib import admin  # noqa: F401

from langcorrect.chats.models import Dialogs, Message

# Register your models here.

admin.site.register(Message)
admin.site.register(Dialogs)
