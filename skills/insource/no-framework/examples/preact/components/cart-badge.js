// examples/preact/components/cart-badge.js
// Shows how a Preact component reads shared signals state: embed the
// signal directly in the template (`${cartCount}`, not `.value`) and
// Preact binds that text node straight to it — no hook, no subscription
// to manage, no component re-render when the count changes. Compare
// examples/nanojsx/components/cart-badge.js, which has to subscribe and
// unsubscribe by hand.

import { html } from "../html.js";
import { cartCount } from "../stores/store.js";

export const CartBadge = () => html`<span class="cart-badge">Cart (${cartCount})</span>`;
