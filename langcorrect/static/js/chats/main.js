import { chat } from './chat.js';
import { dialogs } from './dialogs.js';
import { users } from './users.js';

document.addEventListener('DOMContentLoaded', async () => {
  chat.init();
  await dialogs.init();
  await users.init();
});
