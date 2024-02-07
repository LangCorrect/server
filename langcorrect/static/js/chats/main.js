import { chat } from './chat.js';
import { dialogs } from './dialogs.js';

document.addEventListener('DOMContentLoaded', async () => {
  chat.init();
  await dialogs.init();
});
