// examples/components/product-card.js
// A component composed from a base/ primitive (Button), taking a
// product prop and an onAdd callback rather than reaching into global
// store actions directly — keeps ProductCard reusable in any context.
// Another base -> component example, alongside login-button.js and
// hero-image.js in this same folder.

import van from "https://cdn.jsdelivr.net/npm/vanjs-core@1.6.0/src/van.min.js";
import { Button } from "../base/button.js";

const { div, h3, span } = van.tags;

/**
 * @param {{id: number, name: string, price: number}} product
 * @param {(product: object) => void} onAdd
 */
export const ProductCard = (product, onAdd) => {
  return div({ class: "product-card" },
    h3(product.name),
    span(`$${product.price.toFixed(2)}`),
    Button("Add to Cart", () => onAdd(product))
  );
};

// Usage in a page:
//
//   import { ProductCard } from "../examples/components/product-card.js";
//   import { addToCart } from "../js/store.js";
//
//   products.val.map(p => ProductCard(p, addToCart))
