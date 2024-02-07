import { chatService } from '../services/chatService.js';
import { debounce } from './debounce.js';
import { pubSub } from './pubsub.js';

export const users = {
  list: [],
  modal: null,

  init: async () => {
    users.modal = new bootstrap.Modal('#usersModal');
    const modalBtn = document.getElementById('userModalBtn');
    modalBtn.addEventListener('click', users.openModal);

    const form = document.querySelector('.chat__users__form');
    form.addEventListener('keyup', debounce(users.handleSearch, 600));

    const container = document.querySelector('.chat__users');
    container.addEventListener('click', users.handleClick);

    try {
      users.list = await chatService.getUsers();
      users.renderUsers(users.list);
    } catch (err) {
      console.log('🚀 ~ init: ~ err:', err);
    }
  },

  renderUsers: (userArr) => {
    const container = document.querySelector('.chat__users');

    container.textContent = '';

    const userCount = document.querySelector('.chat__users__count');
    userCount.textContent = userArr.length;

    for (const user of userArr) {
      const ele = users.createUserItem(user);
      container.appendChild(ele);
    }
  },

  createUserItem: ({ pk, username }) => {
    const btn = document.createElement('button');
    btn.classList = 'list-group-item list-group-item-action';
    btn.dataset.userId = pk;
    btn.dataset.username = username;
    btn.textContent = username;
    return btn;
  },

  handleSearch: (evt) => {
    const { value } = evt.target;
    const filteredUsers = users.list.filter((user) =>
      user.username.includes(value.toLowerCase()),
    );
    users.renderUsers(filteredUsers);
  },

  handleClick: (evt) => {
    const { userId, username } = evt.target.dataset;
    pubSub.publish('dialogChanged', { userId, username });
    users.modal.hide();
  },

  openModal: (evt) => {
    users.modal.show();
  },
};
