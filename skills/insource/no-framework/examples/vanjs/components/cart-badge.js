// examples/vanjs/components/cart-badge.js
// Shows how a VanJS component reads shared state: pass the derived
// state straight in as a child and VanJS binds that node to it — no
// subscription to manage, no re-render. Compare
// examples/preact/components/cart-badge.js (signals, same idea) and
// examples/nanojsx/components/cart-badge.js (explicit subscribe/update).

import van from "https://cdn.jsdelivr.net/npm/vanjs-core@1.6.0/src/van.min.js";
import { cartCount } from "../stores/store.js";

const { span } = van.tags;

export const CartBadge = () => span({ class: "cart-badge" }, "Cart (", cartCount, ")");
