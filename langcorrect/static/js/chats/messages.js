import { chatService } from '../services/chatService.js';
import { pubSub } from './pubsub.js';

export const messages = {
  list: [],
  processQueue: [],
  otherUserId: null,
  init: async () => {
    pubSub.subscribe('dialogChanged', await messages.handleDialogChange);
    pubSub.subscribe('outgoingMessage', messages.addOutgoingMessage);
    pubSub.subscribe('incomingMessage', messages.addIncomingMessage);
    pubSub.subscribe('messageIdCreated', messages.updateMessageId);
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
    pubSub.publish('messagesRead', { userId, count: 0 });
    messages.list = await chatService.getMessagesByUserId(userId);
    messages.renderMessages();
  },

  addOutgoingMessage: (message) => {
    messages.list.push(message);
    messages.renderMessage(message);
    messages.scrollToBottom();
  },

  addIncomingMessage: (message) => {
    messages.list.push(message);

    console.log(
      '🚀 Recipient:',
      message.recipient,
      'activeUser',
      messages.otherUserId,
    );

    if (message.sender === messages.otherUserId) {
      messages.renderMessage(message);
      messages.scrollToBottom();
    }
  },

  updateMessageId: ({ randomId, dbId }) => {
    messages.list = messages.list.map((message) => {
      if (message.id === randomId) {
        message.id = dbId;
      }
      return message;
    });

    const msgEle = document.querySelector(`div[msg-id='${randomId}']`);
    if (msgEle) {
      msgEle.setAttribute('msg-id', dbId);
    }
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
      messages.renderMessage(message);
    }

    messages.scrollToBottom();
  },

  renderMessage: ({
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

    message.setAttribute('msg-id', id);

    message.querySelector('.bubble').textContent = text;
    message.classList.add(out ? 'outgoing' : 'incoming');

    document.querySelector('.chat__messages').appendChild(message);
  },

  createMessageWithTimestamp: ({
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
    const timestamp = Math.floor(Date.now() / 1000);

    return {
      id,
      text,
      sent,
      read,
      sender,
      recipient,
      out,
      sender_username,
      sent: timestamp,
      edited: timestamp,
    };
  },

  scrollToBottom: () => {
    const container = document.querySelector('.chat__messages');
    container.scroll({ top: container.scrollHeight, behavior: 'smooth' });
  },
};
