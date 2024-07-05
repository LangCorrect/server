/* Project specific Javascript goes here. */

const tooltipTriggerList = document.querySelectorAll(
  '[data-bs-toggle="tooltip"]',
);
const tooltipList = [...tooltipTriggerList].map(
  (tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl),
);

function showErrorToast(message) {
  Toastify({
    text: message,
    duration: 3000,
    gravity: 'top',
    position: 'right',
    stopOnFocus: true,
    className: 'bg-warning',
  }).showToast();
}
