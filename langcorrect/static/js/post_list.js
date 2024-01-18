'use strict';

window.addEventListener('DOMContentLoaded', () => {
  const languageSelect = document.getElementById('language-select');
  languageSelect.addEventListener('change', function (evt) {
    updateUrl(evt.target, 'lang_code');
  });

  const authorNativeLanguageSelect = document.getElementById(
    'author-native-language-select',
  );
  authorNativeLanguageSelect.addEventListener('change', function (evt) {
    updateUrl(evt.target, 'author_native_lang_code');
  });

  function updateUrl(selectElement, queryParamName) {
    const selectedOption =
      selectElement.options[selectElement.options.selectedIndex];
    const url = new URL(window.location.href);
    url.searchParams.set('mode', mode);
    url.searchParams.set(queryParamName, selectedOption.value);
    window.location = url.toString();
  }
});
