// examples/utils/utils.js
// The standard NoF rendering helper set — always render through these
// rather than calling van.add() directly against #app.

import van from "https://cdn.jsdelivr.net/npm/vanjs-core@1.6.0/src/van.min.js";

export const renderToApp = (component) => {
  const app = document.getElementById('app');
  if (!app) {
    console.error("[NoF] #app element not found");
    return;
  }
  app.innerHTML = '';
  van.add(app, component());
};

export const renderToAppWithProps = (component, props = {}) => {
  const app = document.getElementById('app');
  if (!app) return;
  app.innerHTML = '';
  van.add(app, component(props));
};

export const navigateTo = (path) => {
  window.router.navigate(path);
};
