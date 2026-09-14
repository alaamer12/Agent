// examples/base/image.js
// Another base element in the same spirit as base/button.js: wraps the
// native <img> tag with a default class and a lazy-loading default,
// nothing app-specific. Compare with components/hero-image.js, which
// wraps THIS to add business meaning (headline overlay, CTA slot).

import van from "https://cdn.jsdelivr.net/npm/vanjs-core@1.6.0/src/van.min.js";

const { img } = van.tags;

/**
 * @param {string} src
 * @param {string} alt
 * @param {object} [extraProps] - spread onto the native img element
 */
export const Image = (src, alt, extraProps = {}) => {
  return img({ class: "image", src, alt, loading: "lazy", ...extraProps });
};
