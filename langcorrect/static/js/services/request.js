'use strict';

export const getCsrfToken = () => {
  return document
    .querySelector('meta[name="csrf-token"]')
    .getAttribute('content');
};

export const request = async (endpoint, data = {}, method = 'get') => {
  console.debug('🚀 API Call:', endpoint, data, method);

  const options = {
    method: method.toUpperCase(),
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
    },
  };

  if (method.toUpperCase() === 'POST') {
    options.body = JSON.stringify(data);
  }

  try {
    const response = await fetch(endpoint, options);
    const contentType = response.headers.get('content-type');
    let responseData;

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
};
