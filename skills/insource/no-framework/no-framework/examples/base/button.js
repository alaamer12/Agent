// examples/base/button.js
// A "base" element: the smallest possible styled wrapper around a native
// tag. No business meaning, no app-specific behavior — just markup +
// class + the props a <button> naturally takes. Business components
// (examples/components/) are built out of these, not the other way
// around. See references/components.md#base-vs-components.

import van from "https://cdn.jsdelivr.net/npm/vanjs-core@1.6.0/src/van.min.js";

const { button } = van.tags;

/**
 * @param {string} label
 * @param {() => void} onClick
 * @param {object} [extraProps] - spread onto the native button element
 */
export const Button = (label, onClick, extraProps = {}) => {
  return button({ class: "btn", onclick: onClick, ...extraProps }, label);
};
