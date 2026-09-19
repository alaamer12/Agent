// examples/stores/store.js
// A small but complete global store: state, an action that reassigns
// (never mutates) state, and a derived computed value.

import van from "https://cdn.jsdelivr.net/npm/vanjs-core@1.6.0/src/van.min.js";

export const cart = van.state([]);

export const addToCart = (product) => {
  // New array — this is what makes VanJS notice the change.
  cart.val = [...cart.val, { ...product, cartId: Date.now() }];
};

export const removeFromCart = (cartId) => {
  cart.val = cart.val.filter(item => item.cartId !== cartId);
};

export const cartTotal = van.derive(() =>
  cart.val.reduce((sum, item) => sum + item.price, 0)
);

export const cartCount = van.derive(() => cart.val.length);
