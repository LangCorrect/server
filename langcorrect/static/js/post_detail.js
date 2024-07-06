'use strict';

document.addEventListener('DOMContentLoaded', (event) => {
  function openAccordion(userCorrectionId) {
    const accordionId = `flush-collapseOne-${userCorrectionId}`;
    const ele = document.getElementById(accordionId);

    if (ele) {
      const bsCollapse = new bootstrap.Collapse(ele, {
        toggle: false,
      });
      bsCollapse.show();
    } else {
      console.error('Accordion not found.');
    }
  }

  const modal = new bootstrap.Modal(document.getElementById('lightboxModal'));

  document.querySelectorAll('.js-lightbox-img').forEach((thumbnail) => {
    thumbnail.addEventListener('click', function (e) {
      const imgSrc = this.getAttribute('data-img-src');
      if (imgSrc) {
        const imageInModal = document.getElementById('imageInModal');
        imageInModal.src = imgSrc;
        modal.show();
      }
    });
  });

  class ReplyFormHandler {
    constructor(form) {
      this.form = form;
      this.init();
    }

    init() {
      this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    async handleSubmit(e) {
      e.preventDefault();

      const submitBtn = this.form.querySelector("button[type='submit']");
      submitBtn.disabled = true;

      const payload = this.buildPayload();
      try {
        const data = await new ReplyService(payload).create();
        this.updateUI(data, payload.user_correction);
        this.form.reset();
      } catch (err) {
        showErrorToast(err.message);
      } finally {
        submitBtn.disabled = false;
      }
    }

    buildPayload() {
      return {
        post: this.form.querySelector("input[name='post']").value,
        text: this.form.querySelector("textarea[name='text']").value,
        user_correction: this.form.querySelector(
          "input[name='user_correction']",
        ).value,
      };
    }

    updateUI(data, userCorrectionId) {
      const targetList = document.getElementById(
        `reply-list-${userCorrectionId}`,
      );
      const targetAccordion = document.getElementById(
        `accordion-${userCorrectionId}`,
      );

      const replyCountSpan = document.getElementById(
        `reply-count-${userCorrectionId}`,
      );

      targetList.innerHTML += data;
      if (targetAccordion.classList.contains('d-none')) {
        targetAccordion.classList.remove('d-none');
      }
      openAccordion(userCorrectionId);
      replyCountSpan.textContent = parseInt(replyCountSpan.textContent) + 1;
    }
  }

  document
    .querySelectorAll('.post-reply-form')
    .forEach((form) => new ReplyFormHandler(form));
});
