// examples/preact/stores/store.js
// A small but complete global store via @preact/signals: state, an
// action that reassigns (never mutates) the array, and derived computed
// values. Direct mirror of examples/vanjs/stores/store.js — the
// reassign-don't-mutate rule is identical, only the primitives change
// (signal/.value instead of van.state/.val, computed instead of
// van.derive).
//
// Read a signal directly in a template (`${cartTotal}`, not
// `${cartTotal.value}`) for Preact's optimized text-node binding that
// skips a full component re-render — see
// references/ui_libraries.md#preact-signals. Outside templates (event
// handlers, computed callbacks), always use .value.
//
// Want this store shared with a non-Preact part of the page? See
// --state nanostores in references/ui_libraries.md.

import { signal, computed } from "https://cdn.jsdelivr.net/npm/@preact/signals@2.11.3/+esm";

export const cart = signal([]);

export const addToCart = (product) => {
  // New array — this is what makes the signal notify subscribers.
  cart.value = [...cart.value, { ...product, cartId: Date.now() }];
};

export const removeFromCart = (cartId) => {
  cart.value = cart.value.filter((item) => item.cartId !== cartId);
};

export const cartTotal = computed(() =>
  cart.value.reduce((sum, item) => sum + item.price, 0)
);

export const cartCount = computed(() => cart.value.length);
