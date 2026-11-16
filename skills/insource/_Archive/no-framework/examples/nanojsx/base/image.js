// examples/nanojsx/base/image.js
// Another base element in the same spirit as base/button.js: wraps the
// native <img> tag with a default class and a lazy-loading default,
// nothing app-specific. Compare with components/hero-image.js, which
// wraps THIS to add business meaning (headline overlay, CTA slot).

import { html } from "../html.js";

/**
 * @param {{src: string, alt: string, [key: string]: any}} props
 */
export const Image = ({ src, alt, ...extraProps }) => html`
  <img class="image" src=${src} alt=${alt} loading="lazy" ...${extraProps} />
`;
