import { pubSub } from './pubsub.js';

export const chat = {
  init: () => {
    pubSub.subscribe('dialogChanged', chat.updateChatUI);
  },
  hideEmptyChatContainer: () => {
    const container = document.querySelector('.empty__chat__container');
    container.classList.add('d-none');
  },
  showChatContainer: () => {
    const container = document.querySelector('.chat__container');
    container.classList.remove('d-none');
  },
  updateChatUI: ({ userId, username }) => {
    chat.hideEmptyChatContainer();
    chat.showChatContainer();

    const usernameHeader = document.querySelector('.chat__header__username');
    usernameHeader.textContent = username;
  },
};
