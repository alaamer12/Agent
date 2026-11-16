// examples/nanojsx/html.js
// Binds htm's tagged-template syntax to Nano JSX's h() once, so every
// other file in this directory imports `html` from here instead of
// writing JSX (which needs a compiler) or repeating `htm.bind(h)`
// itself. Nano JSX's h() has the same (type, props, ...children) shape
// htm expects. This is exactly what scripts/init-nof.sh generates as
// js/html.js under --ui nanojsx without --bundler vite. See
// references/ui_libraries.md#nano-jsx.
//
// NOTE: versions below are a snapshot — verify current per SKILL.md
// step 0 before trusting them in a real project.

import { h, render } from "https://cdn.jsdelivr.net/npm/nano-jsx@0.2.1/+esm";
import htm from "https://cdn.jsdelivr.net/npm/htm@3.0.4/+esm";

export const html = htm.bind(h);
export { h, render };
