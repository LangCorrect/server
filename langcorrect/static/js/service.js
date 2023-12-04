'use strict';

async function postRequest(url, data) {
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify(data),
    });

    // Response data can be either JSON or HTML

    let responseData;
    const contentType = response.headers.get('content-type');

    if (contentType && contentType.includes('application/json')) {
      responseData = await response.json();
      if (!response.ok) {
        const errorMessage =
          responseData.detail || responseData.text || 'Unknown error occurred';
        throw new Error(errorMessage);
      }
    } else if (contentType && contentType.includes('text/html')) {
      responseData = await response.text();
    } else {
      throw new Error('Unsupported response type');
    }

    return responseData;
  } catch (err) {
    throw err;
  }
}

function getCsrfToken() {
  const csrfToken = document
    .querySelector('meta[name="csrf-token"]')
    .getAttribute('content');
  return csrfToken;
}

class ReplyService {
  constructor(data) {
    this.data = data;
  }

  async create() {
    return postRequest('/journals/~post_reply/', this.data);
  }
}
