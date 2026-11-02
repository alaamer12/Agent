# SVG and clip-path

> Owner of clip/mask reveals, before and after sliders, line drawing, morphs and the mask-versus-clip edge rule. Routing lives in ../SKILL.md.

Vector animation, reveals, masks and shape-following motion.

## Clip-path reveals

Clip-path animates on the compositor in current engines and does not change layout, so it is the right tool for reveals that follow an element's geometry.

```css
.reveal { clip-path: inset(0 100% 0 0); transition: clip-path 500ms var(--ease-move); }
.reveal.on { clip-path: inset(0 0 0 0); }
```

Variants: `inset(0 0 100% 0)` reveals top-down; `circle(0% at var(--x) var(--y))` to `circle(150% at var(--x) var(--y))` reveals from a point such as the pointer or trigger; use `inset(... round r)` to keep corners. A tab strip can show the active tab's color by clipping a duplicate colored layer to the active tab's bounds and animating the clip.

## Masks

Use a mask when the edge should be soft or fadeable (a gradient mask wiping a feathered edge). Masks cost more than clip-path; keep them small or use them once.

## Before and after sliders

Stack two images, clip the top one with an inset driven by the pointer position, and move the handle with transform. During the drag the usual pointer-tracking rules apply (gestures.md).

## Hold-to-confirm fills

The hold-to-confirm recipe (fill, duration, snap-back) is owned by playbooks-micro.md; implement the fill as a clip-path inset here.

## Line drawing

Animate `stroke-dashoffset` from the path's length to 0. Measure the length with `getTotalLength()` instead of guessing.

```js
const path = document.querySelector('path.draw');
const len = path.getTotalLength();
path.style.strokeDasharray = len;
path.style.strokeDashoffset = len;
path.getBoundingClientRect();                       // commit the starting state
path.style.transition = 'stroke-dashoffset 600ms cubic-bezier(0.22, 1, 0.36, 1)';
path.style.strokeDashoffset = 0;
```

For several paths, stagger by 60 to 100ms in drawing order. For round caps, start slightly before the end so the cap does not pop.

## SVG transform traps

- CSS transforms on SVG children default to a different origin than HTML: set `transform-box: fill-box` and `transform-origin` before scaling or rotating (the matching symptom row: debugging.md).
- Do not mix the SVG `transform` attribute and CSS transforms on the same element.
- Filters on large SVG groups are expensive; apply blur to a small group or pre-render.

## Morphing

Path morphs need the same number of points and compatible commands; use a morph helper or interpolate between pre-normalized paths. For icons that swap shapes, a short crossfade with scale and 2 to 4px blur is often better than a morph.

## Ambient life

Gentle idle motion (float, pulse, drifting gradients) gives static art life. Use offset durations so loops never sync and keep amplitude small; the looping policy (pause off-screen, reduced motion) is owned by performance-and-accessibility.md (Looping and off-screen work).

## Checklist

- [ ] Path length measured, not guessed
- [ ] Transform origin and box set for SVG children
- [ ] Clip-path used instead of animating size
- [ ] Soft edges only where a mask is needed
- [ ] Loops pause off-screen and under reduced motion
