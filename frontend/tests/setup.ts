import '@testing-library/jest-dom';

// JSDOM mock for window.scrollTo
if (typeof window !== 'undefined') {
  window.scrollTo = () => {};
}
