import { MessageTypes } from './constants.js';
import { dialogs } from './dialogs.js';
import { messages } from './messages.js';
import { pubSub } from './pubsub.js';

export const chatSocketHelper = {
  socket: null,
  sendReadReceipt: ({ userId, messageId }) => {
    const payload = JSON.stringify({
      user_pk: userId,
      message_id: messageId,
      msg_type: MessageTypes.MessageRead,
    });
    chatSocketHelper.socket.send(payload);
  },
  sendMessage: ({ userId, randomId, text }) => {
    const payload = JSON.stringify({
      user_pk: userId,
      text,
      random_id: randomId,
      msg_type: MessageTypes.TextMessage,
    });

    chatSocketHelper.socket.send(payload);
  },
};

export const chatSocketEventHandler = {
  handleTextMessage: (data) => {
    const { sender, random_id, text, receiver, sender_username } = data;

    const incomingMessage = messages.createMessageWithTimestamp({
      id: random_id,
      text,
      sender,
      recipient: receiver,
      sender_username,
      out: false,
    });

    pubSub.publish('incomingMessage', incomingMessage);
  },
  handleNewUnreadCount: ({ sender, unread_count }) => {
    pubSub.publish('newUnreadCount', { userId: sender, count: unread_count });
  },
};
