/**
 * @param {Element} element - The target DOM element.
 * @param {string} text - The text to render.
 * @returns {void}
 */
export function renderText(element, text) {
  if (!element || typeof element.textContent !== 'string') {
    throw new TypeError('renderText: element must be a DOM element with a textContent property.');
  }

  if (typeof text !== 'string') {
    throw new TypeError('renderText: text must be a string.');
  }

  element.textContent = text;
}