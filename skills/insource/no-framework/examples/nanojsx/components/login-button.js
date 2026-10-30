// examples/nanojsx/components/login-button.js
// A "business" component: it knows about the app's concepts (auth,
// loading state) and is built out of a base/ primitive rather than a
// native tag directly. This is the base -> component relationship
// described in references/components.md#base-vs-components:
//   base/button.js (Button)  ->  components/login-button.js (LoginButton)
//
// Local state is a class field + explicit this.update() — the Nano JSX
// way (see counter.js). Stateless components elsewhere in this folder
// stay plain functions; only components that own mutable state need a
// class.
//
// `|| undefined` on disabled is deliberate: Nano JSX renders
// disabled={false} as the literal attribute disabled="false", which
// browsers treat as disabled. undefined omits the attribute entirely.

import { html } from "../html.js";
import { Component } from "https://cdn.jsdelivr.net/npm/nano-jsx@0.2.1/+esm";
import { Button } from "../base/button.js";

export class LoginButton extends Component {
  isLoading = false;

  handleClick = async () => {
    this.isLoading = true;
    this.update();
    try {
      await this.props.onLogin();
    } finally {
      this.isLoading = false;
      this.update();
    }
  };

  render() {
    return html`
      <${Button}
        label=${this.isLoading ? "Logging in..." : "Log in"}
        onClick=${this.handleClick}
        disabled=${this.isLoading || undefined}
        class="btn btn-primary login-button"
      />
    `;
  }
}
