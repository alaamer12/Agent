// examples/nanojsx/components/counter.js
// The smallest complete Nano JSX component with local state. Nano JSX
// doesn't observe state — there's no van.state()/useSignal equivalent —
// so local state lives on `this` and every change is followed by an
// explicit this.update(). Derived values (isEven) are just computed
// inline in render(), since render() re-runs on every update() anyway;
// there's nothing to memoize around. Kept self-contained (native
// <button>, no base/button.js) on purpose — see login-button.js for the
// base/component pattern. See references/ui_libraries.md#nano-jsx.

import { html } from "../html.js";
import { Component } from "https://cdn.jsdelivr.net/npm/nano-jsx@0.2.1/+esm";

export class Counter extends Component {
  count = 0;

  increment = () => {
    this.count++;
    this.update(); // explicit — Nano JSX won't notice the field change itself
  };

  decrement = () => {
    this.count--;
    this.update();
  };

  render() {
    const isEven = this.count % 2 === 0;
    return html`
      <div>
        <p>Count: ${this.count}</p>
        <p>Even: ${isEven ? "yes" : "no"}</p>
        <button onClick=${this.increment}>+1</button>
        <button onClick=${this.decrement}>-1</button>
      </div>
    `;
  }
}
