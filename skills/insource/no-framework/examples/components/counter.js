// examples/components/counter.js
// The smallest complete VanJS component: state + derive + event handler.
// Kept self-contained (native <button> instead of base/button.js) on
// purpose — this file's job is teaching state+derive, not the
// base/component pattern; see login-button.js for that.

import van from "https://cdn.jsdelivr.net/npm/vanjs-core@1.6.0/src/van.min.js";

const { div, button, p } = van.tags;

export const Counter = () => {
  const count = van.state(0);
  const isEven = van.derive(() => count.val % 2 === 0);

  return div(
    p("Count: ", count),
    p("Even: ", () => (isEven.val ? "yes" : "no")),
    button({ onclick: () => count.val++ }, "+1"),
    button({ onclick: () => count.val-- }, "-1")
  );
};
