export const debounce = (fn, delay = 350) => {
  let timerId;

  return function (...args) {
    if (timerId) clearTimeout(timerId);

    timerId = setTimeout(() => {
      fn(...args);
    }, delay);
  };
};
