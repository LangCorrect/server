import { messages } from './messages.js';
import { pubSub } from './pubsub.js';
import { chatSocketHelper } from './socket-handlers.js';

export const chatForm = {
  init: () => {
    pubSub.subscribe('dialogChanged', chatForm.setupForm);
  },

  setupForm: ({ userId, username }) => {
    const form = document.querySelector('.chat__form');
    form.querySelector("input[name='other_user_id']").value = userId;
    form
      .querySelector('button')
      .addEventListener('click', chatForm.handleSubmit);
  },

  handleSubmit: (evt) => {
    evt.preventDefault();

    const userId = document.querySelector("input[name='other_user_id']").value;
    const senderId = document.querySelector("input[name='sender_id']").value;
    const textarea = document.querySelector("textarea[name='text']");
    const text = textarea.value;
    const random_id = -Math.floor(Math.random() * 100_000_000_000);

    if (textarea.value.trim() === '') {
      // TODO: Display error
      return;
    }

    chatSocketHelper.sendMessage({ userId, text, randomId: random_id });

    const outgoingMessage = messages.createMessageWithTimestamp({
      id: random_id,
      text,
      recipient: userId,
      sender: senderId,
      out: true,
      // sender_username: null,
    });

    textarea.value = '';

    pubSub.publish('outgoingMessage', outgoingMessage);
  },
};
