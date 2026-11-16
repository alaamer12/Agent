// examples/preact/components/product-card.js
// A component composed from a base/ primitive (Button), taking a
// product prop and an onAdd callback rather than reaching into global
// store actions directly — keeps ProductCard reusable in any context.
// Another base -> component example, alongside login-button.js and
// hero-image.js in this same folder.

import { html } from "../html.js";
import { Button } from "../base/button.js";

/**
 * @param {{product: {id: number, name: string, price: number}, onAdd: (product: object) => void}} props
 */
export const ProductCard = ({ product, onAdd }) => html`
  <div class="product-card">
    <h3>${product.name}</h3>
    <span>$${product.price.toFixed(2)}</span>
    <${Button} label="Add to Cart" onClick=${() => onAdd(product)} />
  </div>
`;

// Usage in a page:
//
//   import { ProductCard } from "../examples/preact/components/product-card.js";
//   import { addToCart } from "../js/store.js";
//
//   products.map(p => html`<${ProductCard} key=${p.id} product=${p} onAdd=${addToCart} />`)
