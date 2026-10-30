// examples/preact/components/counter.js
// The smallest complete Preact component built the NoF way: local state
// via @preact/signals' useSignal/useComputed rather than plain
// useState/useMemo — same no-dependency-array ergonomics as VanJS's
// van.state()/van.derive(), scoped to one component instead of
// js/store.js. Kept self-contained (native <button>, no base/button.js)
// on purpose — this file's job is teaching signals, not the
// base/component pattern; see login-button.js for that.
// See references/ui_libraries.md#preact-signals.

import { html } from "../html.js";
import { useSignal, useComputed } from "https://cdn.jsdelivr.net/npm/@preact/signals@2.11.3/+esm";

export const Counter = () => {
  const count = useSignal(0);
  // Unlike VanJS, Preact doesn't accept a function as a child for a
  // reactive binding — the computed signal itself is what gets embedded
  // directly, so it's defined to already hold the label string.
  const isEvenLabel = useComputed(() => (count.value % 2 === 0 ? "yes" : "no"));

  return html`
    <div>
      <p>Count: ${count}</p>
      <p>Even: ${isEvenLabel}</p>
      <button onClick=${() => count.value++}>+1</button>
      <button onClick=${() => count.value--}>-1</button>
    </div>
  `;
};
