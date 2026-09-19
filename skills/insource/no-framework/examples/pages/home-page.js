// examples/pages/home-page.js
// A page composed from components — pages assemble, they don't define.
// See references/project_structure.md for why component definitions
// don't belong in pages/.

import van from "https://cdn.jsdelivr.net/npm/vanjs-core@1.6.0/src/van.min.js";
import { HeroImage } from "../components/hero-image.js";
import { ProductCard } from "../components/product-card.js";
import { LoginButton } from "../components/login-button.js";
import { addToCart } from "../stores/store.js";

const { div, section } = van.tags;

const featuredProducts = [
  { id: 1, name: "Widget", price: 9.99 },
  { id: 2, name: "Gadget", price: 19.99 },
];

export const HomePage = () => {
  return div({ class: "page home-page" },
    HeroImage({
      src: "/images/hero.jpg",
      alt: "Storefront banner",
      headline: "Welcome to the shop",
    }),
    section({ class: "featured" },
      featuredProducts.map(p => ProductCard(p, addToCart))
    ),
    LoginButton(async () => {
      // app-specific auth call goes here
    })
  );
};

// Rendered via the standard helper, not ad hoc DOM manipulation:
//
//   import { renderToApp } from "../utils/utils.js";
//   import { HomePage } from "../pages/home-page.js";
//   renderToApp(HomePage);
