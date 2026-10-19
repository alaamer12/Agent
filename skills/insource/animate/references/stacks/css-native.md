# Stack: CSS and native web APIs

> **Connections** (paths are relative to `references/`)
> - Read when: plain CSS, Web Animations, view transitions, scroll-driven CSS, Tailwind, or Vue or Svelte without an animation library.
> - Skip when: React with Motion already covers the need.
> - Read next: `stacks/nextjs-transitions.md` (for route transitions in Next.js).

Notes for projects with no animation library, or when the platform can do the job. Check browser support in the project's target list before relying on newer features, and keep a fallback.

## Contents
- Transitions
- Entry and discrete properties
- Keyframes
- Web Animations API
- Sampled curves
- View transitions
- Scroll-driven animation
- Relational selectors
- Utility frameworks

## Transitions

```css
.card {
  transition: transform 200ms var(--ease-enter), opacity 200ms var(--ease-enter);
}
```

Name the properties. `transition: all` is never right: it animates properties nobody meant to and can fall off the compositor. Transitions retarget when interrupted; use them for anything triggered rapidly.

## Entry and discrete properties

```css
.dialog { opacity: 1; transform: none;
  transition: opacity 200ms var(--ease-enter), transform 200ms var(--ease-enter),
              display 200ms allow-discrete, overlay 200ms allow-discrete; }
@starting-style { .dialog { opacity: 0; transform: scale(0.95); } }
.dialog:not([open]) { opacity: 0; transform: scale(0.95); }
```

`@starting-style` lets an element transition from its first style when it enters the DOM; `transition-behavior: allow-discrete` lets display and overlay participate in the exit. Where unsupported, fall back to a mounted attribute set on the next frame.

## Keyframes

Use keyframes for predetermined sequences (loading shimmer, a staged entrance). They restart from zero when re-triggered, so do not use them for rapid toggles. Use `animation-fill-mode: both` for entrances so there is no flash before the delay.

## Web Animations API

```js
const a = el.animate(
  [{ opacity: 0, transform: 'translateY(8px)' }, { opacity: 1, transform: 'none' }],
  { duration: 240, easing: 'cubic-bezier(0.22, 1, 0.36, 1)', fill: 'both' }
);
await a.finished;
// interrupt and reverse from the current state:
a.reverse();
```

`updatePlaybackRate`, `reverse()` and `commitStyles()` make interruption and sequencing straightforward without a library.

## Sampled curves

`linear()` accepts sampled points, so springs and overshoot curves can be expressed in CSS:

```css
transition-timing-function: linear(0, 0.45, 0.78, 1, 1.17, 1.21, 1.18, 1.12, 1.05, 1.02, 1);
```

## View transitions

```js
if (document.startViewTransition) {
  const t = document.startViewTransition(() => updateDom());
} else updateDom();
```

```css
.hero-image { view-transition-name: hero; }
::view-transition-old(root), ::view-transition-new(root) { animation-duration: 250ms; }
::view-transition-group(hero) { animation-duration: 350ms; animation-timing-function: var(--ease-move); }
```

- Names must be unique on the page at the time of the snapshot.
- The browser snapshots and crossfades by default; customize with the pseudo-elements above.
- Direction-aware: set a data attribute on the root before the transition and select on it in the pseudo-element rules; remove it after `t.finished`.
- Cross-document support differs from same-document support: check the target browsers.
- Provide the non-supporting fallback: update the DOM without animation.

## Scroll-driven animation

```css
.progress { animation: grow linear both; animation-timeline: scroll(); }
.reveal { animation: rise linear both; animation-timeline: view(); animation-range: entry 0% entry 60%; }
```

Use only with a fallback for engines without support (an intersection observer reveal or no animation).

## Relational selectors

`:has()` lets CSS express relationships without script, such as de-emphasizing siblings while one is hovered:

```css
.list:has(.row:hover) .row:not(:hover) { opacity: 0.55; }
```

## Utility frameworks

When the project uses a utility framework, define the easing and duration tokens in its theme, and inspect generated CSS for hover utilities (some already gate with the hover media query). Arbitrary-value animation classes are fine for single-use keyframes; repeated ones belong in the theme.
