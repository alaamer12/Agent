// examples/preact/html.js
// Binds htm's tagged-template syntax to Preact's h() once, so every
// other file in this directory imports `html` from here instead of
// writing JSX (which needs a compiler) or repeating `htm.bind(h)`
// itself. This is exactly what scripts/init-nof.sh generates as
// js/html.js under --ui preact without --bundler vite. See
// references/ui_libraries.md and
// references/tooling.md#htm-how-preactnano-jsx-stay-no-build-step.
//
// NOTE: versions below are a snapshot — verify current per SKILL.md
// step 0 before trusting them in a real project.

import { h, render } from "https://cdn.jsdelivr.net/npm/preact@11.0.0/+esm";
import htm from "https://cdn.jsdelivr.net/npm/htm@3.0.4/+esm";

export const html = htm.bind(h);
export { h, render };
