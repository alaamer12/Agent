# Performance and accessibility

> Owner of property cost tiers, reduced-motion policy, main-thread rules, will-change, input devices and hover-on-touch, looping, the scroll-listener ban, and focus mechanics. Routing lives in ../SKILL.md.

Rules that apply to every build. The audit script checks the mechanical ones.

## Property tiers

| Tier | Properties | Cost |
|---|---|---|
| Compositor only | transform, opacity (plus filter, clip-path, background-color in current engines) | Cheapest |
| Paint | box-shadow, border-radius, color | Redraw each frame |
| Layout | width, height, padding, margin, top, left, border-width | Most expensive |

Swap down a tier when you can:

| Instead of animating | Animate |
|---|---|
| width or height to grow or shrink | scale |
| margin, top, left to move | translate (percentages are relative to the element) |
| box-shadow | filter drop-shadow, or a pre-rendered shadow layer fading in |
| border-radius | clip-path inset with round |

The scale version looks identical and cannot regress on a slower device. Take the option with no downside. `scale()` also scales children (text, icons, borders): a feature for press feedback, a trap when an inner element must stay fixed.

## Implementation order

CSS transitions, then the Web Animations API, then CSS keyframes, then JavaScript frame loops. Under load, CSS stays smooth while script-driven animation drops frames. Transitions retarget when interrupted; keyframes restart from zero, so use keyframes only for predetermined sequences. Use a starting-style rule for entry from the DOM when supported, with a mounted-attribute fallback for older engines.

## Main-thread discipline

- Do not start an animation and expensive work in the same tick (mounting a large tree, parsing, fetching). Start the motion, let a frame land, then do the work, or defer it to the end event.
- Chunk unavoidable work against a time budget (about 5ms per slice) and yield between slices.
- Never drive animation from a scroll listener writing state; use an intersection observer for triggers and scroll-timeline or a motion value for scrubbing.
- Do not drive drag with a CSS variable on a container: every update recalculates every child. Set transform directly on the moving element.
- Script animation shorthands (separate x, y, scale properties in some libraries) run on the main thread; when motion must survive a busy page, animate a full transform string or use CSS or the Web Animations API.
- Do not measure layout every frame.

## Layers and will-change

Promote only what animates, only during the animation, and remove the hint afterwards. Many permanent layers cost more than none. A shaky 1px shift at the start or end of a transform animation usually means a handoff between layers; hint the property for the duration.

## Looping and off-screen work

Pause loops when off-screen (intersection observer toggling the paused state). Pause rather than hide, so state is preserved. Stop continuous canvas or frame work once an animation settles.

## Theme switching

Disable transitions during theme changes so every themed property does not animate at once: set an attribute on the root, flip the theme, force a reflow, and remove the attribute on the next frame.

## Reduced motion

Policy: keep content visible and keep user-triggered feedback, replace spatial travel with immediate state changes or restrained fades, pause decorative loops, and disable scroll-scrubbed and pinned effects. Reduced does not mean zero: keep opacity and color changes that aid comprehension, drop movement and scale.

```css
@media (prefers-reduced-motion: reduce) {
  .surface { transition: opacity 150ms ease; transform: none; }
  .ambient { animation-play-state: paused; }
}
```

Every spec and every build states its reduced-motion variant. Test the same task in that mode.

## Input devices

- Gate hover motion with `@media (hover: hover) and (pointer: fine)`; touch devices replay hover on tap. Some frameworks already gate their hover utilities: inspect the generated CSS before adding another gate.
- Tappable controls respond at 0ms on press and set `touch-action: manipulation`; interactive targets are at least 44px (gesture-specific use of these: gestures.md).
- During direct manipulation keep the element locked to the pointer with no easing; ease only after release.

## Focus and keyboard

Keyboard focus and repeated navigation stay immediate. An animated state change may play as long as focus placement and task completion do not wait for it. Keep visible focus styles on anything interactive, including inside prototypes. Whether such an animation should exist at all is the gate's verdict (gate.md).

## Checklist

- [ ] Only compositor properties (or a labeled container tween)
- [ ] No `transition: all`
- [ ] Interruptible where triggered rapidly or by gesture
- [ ] Reduced-motion variant defined and tested
- [ ] Hover gated; touch and keyboard complete the same task
- [ ] Loops pause off-screen; hints removed after use
- [ ] No animation starting in the same tick as heavy work
