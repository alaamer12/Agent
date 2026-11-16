// examples/nanojsx/components/cart-badge.js
// Shows how a Nano JSX component reads shared Nano Stores state: with
// no hooks, it subscribes in didMount, calls this.update() on every
// notification, and MUST unsubscribe in didUnmount — otherwise the
// store keeps a reference to a component that's no longer on the page.
// This subscribe -> update -> unsubscribe cycle is what Preact's
// useStore() hook or VanJS's built-in reactivity do for you elsewhere.

import { html } from "../html.js";
import { Component } from "https://cdn.jsdelivr.net/npm/nano-jsx@0.2.1/+esm";
import { cartCount } from "../stores/store.js";

export class CartBadge extends Component {
  didMount() {
    this.unsubscribe = cartCount.subscribe(() => this.update());
  }

  didUnmount() {
    this.unsubscribe?.();
  }

  render() {
    return html`<span class="cart-badge">Cart (${cartCount.get()})</span>`;
  }
}
