import { request } from './request.js';

export const chatService = {
  getDialogs: async () => {
    const resp = await request('/chats/dialogs');
    return resp.data;
  },
  getMessagesByUserId: async (userId) => {
    const resp = await request(`/chats/messages/${userId}`);
    return resp.data;
  },
  getUsers: async () => {
    const resp = await request('/chats/users');
    return resp.data;
  },
  markAllMessagesAsRead: async (userId) => {
    const resp = await request(
      `/chats/messages/${userId}/mark-all-read`,
      {},
      'post',
    );
    return resp.data;
  },
};
