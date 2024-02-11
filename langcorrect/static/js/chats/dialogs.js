'use strict';

import { pubSub } from './pubsub.js';
import { chatService } from '../services/chatService.js';

export const dialogs = {
  list: [],
  activeDialog: null,
  init: async () => {
    pubSub.subscribe('messagesRead', dialogs.updateUnreadCount);
    pubSub.subscribe('newUnreadCount', dialogs.updateUnreadCount);
    pubSub.subscribe('outgoingMessage', dialogs.updateLastMessage);
    pubSub.subscribe('incomingMessage', dialogs.updateLastMessage);
    dialogs.list = await chatService.getDialogs();
    dialogs.render();
  },
  render: async () => {
    const container = document.getElementById('dialogsContent');

    dialogs.list.forEach((dialog) => {
      const dialogItem = dialogs.createDialogItem(dialog);
      container.appendChild(dialogItem);
    });

    container.addEventListener('click', dialogs.handleClick);
  },
  handleClick: (evt) => {
    const { userId, username } = evt.target.dataset;

    if (!(userId && username)) return;

    dialogs.activeDialog = userId;
    pubSub.publish('dialogChanged', { userId, username });
  },
  updateLastMessage: ({ text, sender, recipient }) => {
    let userToUpdate;

    dialogs.list = dialogs.list.map((dialog) => {
      if (
        dialog.other_user_id === sender ||
        dialog.other_user_id === recipient
      ) {
        userToUpdate = dialog.other_user_id === sender ? sender : recipient;
        return {
          ...dialog,
          last_message: {
            text: text !== undefined ? text : dialog.last_message.text,
          },
        };
      }
      return dialog;
    });

    const dialogEle = document.querySelector(
      `div[data-user-id='${userToUpdate}']`,
    );
    if (dialogEle) {
      dialogEle.querySelector('.text__preview').textContent = text;
    }
  },
  updateUnreadCount: ({ userId, count }) => {
    dialogs.list = dialogs.list.map((dialog) => {
      if (dialog.other_user_id === userId) {
        return {
          ...dialog,
          unread_count: count || 0,
        };
      }
      return dialog;
    });

    const dialogEle = document.querySelector(`div[data-user-id='${userId}']`);
    if (dialogEle) {
      dialogEle.querySelector('.unread__count').textContent = count;

      if (count < 1) {
        dialogEle.querySelector('.unread__count').classList.add('d-none');
      } else {
        dialogEle.querySelector('.unread__count').classList.remove('d-none');
      }
    }
  },
  createDialogItem: ({
    id,
    created,
    modified,
    username,
    other_user_id,
    unread_count,
    last_message,
  }) => {
    if (!(username && other_user_id)) {
      throw new Error(
        'Both the username and userId is required to render a dialog item.',
      );
    }

    const template = document.getElementById('dialogsCardTemplate');
    const dialogItem = template.content.cloneNode(true);

    const cardElement = dialogItem.querySelector('.dialogs__card');
    cardElement.dataset.userId = other_user_id;
    cardElement.dataset.username = username;

    const usernameElement = dialogItem.querySelector(
      '.dialogs__card__header h5',
    );
    const previewTextElement = dialogItem.querySelector('.text__preview');
    const avatarElement = dialogItem.querySelector(
      '.dialogs__card__header img',
    );

    avatarElement.setAttribute(
      'src',
      `https://ui-avatars.com/api/?rounded=true&length=1&name=${username}`,
    );
    usernameElement.textContent = username;
    previewTextElement.textContent = last_message.text;

    const unreadCountElement = dialogItem.querySelector('.unread__count');
    unreadCountElement.textContent = unread_count;

    if (unread_count < 1) {
      unreadCountElement.classList.add('d-none');
    }

    return dialogItem;
  },
};
