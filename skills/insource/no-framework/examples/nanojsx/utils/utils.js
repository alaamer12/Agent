// examples/nanojsx/utils/utils.js
// The standard NoF rendering helper set — always render through these
// rather than calling Nano JSX's render() directly against #app. The
// page is rendered via h(component, props), not by calling component()
// yourself — works for plain function pages and class pages alike (a
// class component can't be constructed without h()).

import { h, render } from "https://cdn.jsdelivr.net/npm/nano-jsx@0.2.1/+esm";

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
