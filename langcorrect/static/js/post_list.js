'use strict';

window.addEventListener('DOMContentLoaded', () => {
  const languageSelect = document.getElementById('language-select');
  languageSelect.addEventListener('change', function (evt) {
    const selectedOption = evt.target.options[evt.target.selectedIndex];
    const link = selectedOption.dataset.link;
    window.location = link;
  });

  const authorNativeLanguageSelect = document.getElementById(
    'author-native-language-select',
  );
  authorNativeLanguageSelect.addEventListener('change', function (evt) {
    const selectedOption = evt.target.options[evt.target.selectedIndex];
    const link = selectedOption.dataset.link;
    window.location = link;
  });
});
