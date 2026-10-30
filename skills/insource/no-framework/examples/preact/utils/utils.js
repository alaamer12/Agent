// examples/preact/utils/utils.js
// The standard NoF rendering helper set — always render through these
// rather than calling Preact's render() directly against #app. The page
// is rendered via h(component, props), NOT by calling component()
// yourself — that way Preact owns the render and hooks work at the top
// level of a page. Calling a hook-using component directly crashes.

import { h, render } from "https://cdn.jsdelivr.net/npm/preact@11.0.0/+esm";

export const renderToApp = (component) => {
  const app = document.getElementById('app');
  if (!app) {
    console.error("[NoF] #app element not found");
    return;
  }
  app.innerHTML = '';
  render(h(component), app);
};

export const renderToAppWithProps = (component, props = {}) => {
  const app = document.getElementById('app');
  if (!app) return;
  app.innerHTML = '';
  render(h(component, props), app);
};

export const navigateTo = (path) => {
  window.router.navigate(path);
};
