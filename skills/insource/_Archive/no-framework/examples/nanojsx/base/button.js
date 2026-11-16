// examples/nanojsx/base/button.js
// A "base" element: the smallest possible styled wrapper around a native
// tag. No business meaning, no app-specific behavior — just markup +
// class + the props a <button> naturally takes. Business components
// (examples/nanojsx/components/) are built out of these, not the other
// way around. See references/components.md#base-vs-components.
//
// Nano JSX components take a single props object (not positional args the
// way VanJS's base/button.js does) — the idiomatic JSX/React convention,
// also used here even without real JSX (htm mirrors it exactly).

import { html } from "../html.js";

/**
 * @param {{label: string, onClick: () => void, [key: string]: any}} props
 */
export const Button = ({ label, onClick, ...extraProps }) => html`
  <button class="btn" onClick=${onClick} ...${extraProps}>${label}</button>
`;
