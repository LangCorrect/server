import { request } from './request.js';

export const replyService = {
  add: async (data) => {
    const html = await request('/journals/~post_reply/', data, 'post');
    return html;
  },
};
