import { chatService } from '../services/chatService.js';
import { pubSub } from './pubsub.js';

export const messages = {
  list: [],
  processQueue: [],
  otherUserId: null,
  init: async () => {
    pubSub.subscribe('dialogChanged', await messages.handleDialogChange);
  },
  fetchMessages: async ({ userId, username }) => {
    try {
      messages.list = await chatService.getMessagesByUserId(userId);
      messages.otherUserId = userId;
    } catch (_) {
      throw new Error('Problems fetching messages...');
    }
  },

  handleDialogChange: async ({ userId, username }) => {
    if (!(userId && username)) throw new Error('Username and Id is required.');
    messages.otherUserId = userId;

    await chatService.markAllMessagesAsRead(userId);
    messages.list = await chatService.getMessagesByUserId(userId);
    messages.renderMessages();
  },

  renderMessages: () => {
    const sortedMessages = messages.list
      .sort((a, b) => a.sent - b.sent)
      .filter((msg) => {
        if (
          +msg.sender === +messages.otherUserId ||
          +msg.recipient === +messages.otherUserId
        )
          return msg;
      });

    const messageList = document.querySelector('.chat__messages');
    messageList.textContent = '';

    for (const message of sortedMessages) {
      messages.createMessage(message);
    }

    messages.scrollToBottom();
  },

  createMessage: ({
    id,
    text,
    sent,
    edited,
    read,
    sender,
    recipient,
    out,
    sender_username,
  }) => {
    const template = document.getElementById('messageTemplate');
    const message = template.content.cloneNode(true).querySelector('.message');

    message.querySelector('.bubble').textContent = text;
    message.classList.add(out ? 'outgoing' : 'incoming');

    document.querySelector('.chat__messages').appendChild(message);
  },

  scrollToBottom: () => {
    const container = document.querySelector('.chat__messages');
    container.scroll({ top: container.scrollHeight, behavior: 'smooth' });
  },
};
