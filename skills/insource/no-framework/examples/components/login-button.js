// examples/components/login-button.js
// A "business" component: it knows about the app's concepts (auth,
// loading state) and is built out of a base/ primitive rather than a
// native tag directly. This is the base -> component relationship
// described in references/components.md#base-vs-components:
//   base/button.js (Button)  ->  components/login-button.js (LoginButton)

import van from "https://cdn.jsdelivr.net/npm/vanjs-core@1.6.0/src/van.min.js";
import { Button } from "../base/button.js";

/**
 * @param {() => void | Promise<void>} onLogin
 */
export const LoginButton = (onLogin) => {
  const isLoading = van.state(false);

  const handleClick = async () => {
    isLoading.val = true;
    try {
      await onLogin();
    } finally {
      isLoading.val = false;
    }
  };

  return Button(
    () => (isLoading.val ? "Logging in..." : "Log in"),
    handleClick,
    { disabled: () => isLoading.val, class: "btn btn-primary login-button" }
  );
};
