// examples/preact/components/login-button.js
// A "business" component: it knows about the app's concepts (auth,
// loading state) and is built out of a base/ primitive rather than a
// native tag directly. This is the base -> component relationship
// described in references/components.md#base-vs-components:
//   base/button.js (Button)  ->  components/login-button.js (LoginButton)
//
// Local, component-owned state like isLoading stays a plain hook
// (useState) — it doesn't need to be a signal, since nothing outside
// this component reads it. Shared state belongs in stores/store.js.

import { html } from "../html.js";
import { useState } from "https://cdn.jsdelivr.net/npm/preact@11.0.0/hooks/+esm";
import { Button } from "../base/button.js";

/**
 * @param {{onLogin: () => void | Promise<void>}} props
 */
export const LoginButton = ({ onLogin }) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleClick = async () => {
    setIsLoading(true);
    try {
      await onLogin();
    } finally {
      setIsLoading(false);
    }
  };

  return html`
    <${Button}
      label=${isLoading ? "Logging in..." : "Log in"}
      onClick=${handleClick}
      disabled=${isLoading}
      class="btn btn-primary login-button"
    />
  `;
};
