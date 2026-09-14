// examples/components/hero-image.js
// Another base -> component pairing: base/image.js (Image) becomes
// HeroImage here by adding app-specific meaning — a headline overlay
// and container — without duplicating the underlying <img> wrapper.

import van from "https://cdn.jsdelivr.net/npm/vanjs-core@1.6.0/src/van.min.js";
import { Image } from "../base/image.js";

const { div, h1 } = van.tags;

/**
 * @param {{src: string, alt: string, headline: string}} props
 */
export const HeroImage = ({ src, alt, headline }) => {
  return div({ class: "hero-image" },
    Image(src, alt, { class: "image hero-image__img" }),
    h1({ class: "hero-image__headline" }, headline)
  );
};
