'use strict';

window.addEventListener('DOMContentLoaded', () => {
  const navButtons = document.querySelectorAll('.nav-link');

  navButtons.forEach((button) =>
    button.addEventListener('click', () => {
      navButtons.forEach((b) => {
        if (b !== button) {
          b.classList.remove('border-bottom', 'border-primary');
        }
      });
      button.classList.add('border-bottom', 'border-primary');
    }),
  );
});
