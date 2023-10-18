'use strict';

window.addEventListener('DOMContentLoaded', () => {
  const tableRows = document.querySelectorAll('.prompt-row');
  tableRows.forEach((row) =>
    row.addEventListener('click', () => {
      const link = row.dataset.link;
      window.location = link;
      if (link) {
        window.location = link;
      }
    }),
  );
});
