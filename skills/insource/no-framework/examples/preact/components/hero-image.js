// examples/preact/components/hero-image.js
// Another base -> component pairing: base/image.js (Image) becomes
// HeroImage here by adding app-specific meaning — a headline overlay
// and container — without duplicating the underlying <img> wrapper.

import { html } from "../html.js";
import { Image } from "../base/image.js";

/**
 * @param {{src: string, alt: string, headline: string}} props
 */
export const HeroImage = ({ src, alt, headline }) => html`
  <div class="hero-image">
    <${Image} src=${src} alt=${alt} class="image hero-image__img" />
    <h1 class="hero-image__headline">${headline}</h1>
  </div>
`;
