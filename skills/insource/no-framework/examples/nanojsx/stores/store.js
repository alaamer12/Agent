// examples/nanojsx/stores/store.js
// A small but complete global store via Nano Stores: state, an action
// that reassigns (never mutates) the array, and derived computed
// values. Nano JSX has no reactive store of its own, so Nano Stores is
// the shared-state choice here (see references/ui_libraries.md#nano-jsx).
// Direct mirror of examples/vanjs/stores/store.js — the reassign-
// don't-mutate rule is identical, only the primitives change
// (atom + .get()/.set() instead of van.state + .val, computed instead
// of van.derive).
//
// Components read a store by subscribing explicitly (didMount ->
// store.subscribe(() => this.update()), didUnmount -> unsubscribe) —
// there are no hooks to do it for you. See components/cart-badge.js.

import { atom, computed } from "https://cdn.jsdelivr.net/npm/nanostores@1.5.5/+esm";

export const cart = atom([]);

export const addToCart = (product) => {
  // New array — this is what makes subscribers get notified.
  cart.set([...cart.get(), { ...product, cartId: Date.now() }]);
};

export const removeFromCart = (cartId) => {
  cart.set(cart.get().filter((item) => item.cartId !== cartId));
};

export const cartTotal = computed(cart, (items) =>
  items.reduce((sum, item) => sum + item.price, 0)
);

export const cartCount = computed(cart, (items) => items.length);
