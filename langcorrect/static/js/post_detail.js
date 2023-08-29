"use strict";

document.body.addEventListener("htmx:responseError", function (evt) {
  const xhr = evt.detail.xhr;
  const form = evt.target;
  const textarea = form.querySelector("textarea");
  const errorMessage = form.querySelector(".invalid-feedback");
  textarea.classList.add("is-invalid");
  errorMessage.textContent = JSON.parse(xhr.responseText);
});

document.body.addEventListener("htmx:beforeRequest", function (evt) {
  const form = evt.target;
  const textarea = form.querySelector("textarea");
  const errorMessage = form.querySelector(".invalid-feedback");
  textarea.classList.remove("is-invalid");
  errorMessage.textContent = "";
});

document.body.addEventListener("htmx:afterRequest", function (evt) {
  const xhr = evt.detail.xhr;
  if (xhr.status === 200) {
    const form = evt.detail.elt;
    const replyCounterTarget = form.dataset.repliesCountTarget;
    const replyCounter = document.getElementById(`${replyCounterTarget}`);
    replyCounter.innerText = +replyCounter.innerText + 1;
  }
});

document.addEventListener('DOMContentLoaded', (event) => {
  const modal = new bootstrap.Modal(document.getElementById("lightboxModal"));

  document.querySelectorAll(".js-lightbox-img").forEach((thumbnail) => {
    thumbnail.addEventListener("click", function (e) {
      const imgSrc = this.getAttribute("data-img-src");
      if (imgSrc) {
        const imageInModal = document.getElementById("imageInModal");
        imageInModal.src = imgSrc;
        modal.show();
      }
    });
  });
});
