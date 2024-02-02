'use strict';

window.addEventListener('DOMContentLoaded', () => {
  const languageSelect = document.getElementById('language-select');
  languageSelect.addEventListener('change', function (evt) {
    const selectedOption = evt.target.options[evt.target.selectedIndex];
    const link = selectedOption.dataset.link;
    window.location = link;
  });

  function renderServerTime() {
    const date = new Date();
    const hours = String(date.getUTCHours()).padStart(2, '0');
    const minutes = String(date.getUTCMinutes()).padStart(2, '0');
    const seconds = String(date.getUTCSeconds()).padStart(2, '0');

    const serverTimeEle = document.getElementById('serverTime');

    if (serverTimeEle) {
      serverTimeEle.textContent = `${hours}:${minutes}:${seconds}`;
    }
  }

  renderServerTime();
  setInterval(renderServerTime, 1000);
});
