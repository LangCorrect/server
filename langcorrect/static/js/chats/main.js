import { chatForm } from './chat-form.js';
import { chat } from './chat.js';
import { MessageTypes } from './constants.js';
import { dialogs } from './dialogs.js';
import { messages } from './messages.js';
import { chatSocketEventHandler, chatSocketHelper } from './socket-handlers.js';
import { users } from './users.js';

document.addEventListener('DOMContentLoaded', async () => {
  // TODO: Build the chat socket url manually
  const chatSocketUrl = 'ws://localhost:8000/chat_ws';
  const chatSocket = new WebSocket(chatSocketUrl);
  chatSocketHelper.socket = chatSocket;

  chat.init();
  chatForm.init();
  await dialogs.init();
  await users.init();
  await messages.init();

  chatSocket.onmessage = async function (evt) {
    console.log('🚀 ~ chatSocket.onmessage ~ evt:', evt);

    const data = JSON.parse(evt.data);

    switch (data.msg_type) {
      case MessageTypes.TextMessage:
        chatSocketEventHandler.handleTextMessage(data);
        break;
      default:
        break;
    }
  };
});
