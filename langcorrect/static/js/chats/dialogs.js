'use strict';

import { pubSub } from './pubsub.js';
import { chatService } from '../services/chatService.js';

export const dialogs = {
  list: [],
  activeDialog: null,
  init: async () => {
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

    return dialogItem;
  },
};
