# Motion Parity: Beyond the Still Frame

A still-frame comparison of an ItC component's *end state* (dropdown fully open, drawer fully open) can score perfectly while the *transition itself* is completely wrong — snapping instead of sliding, no easing, a chevron icon that should flip from pointing down to pointing up and doesn't, a modal that should fade its backdrop in and just appears instantly. None of this shows up in a still-frame diff, because a still frame only ever captures a moment, never the motion between moments. If the mockup has deliberate, designed transitions, treat this as its own checklist — separate from the main similarity-scoring loop, because the loop's metrics genuinely cannot detect it.

## Table of contents
1. Why stills can't catch this
2. What to check per ItC component
3. How to extract the mockup's actual transition spec
4. How to verify the native/real implementation

---

## 1. Why stills can't catch this

The convergence loop in `SKILL.md` captures and compares discrete frames — a before-state and an after-state. Any comparison metric run against those two frames tells you whether the *end points* match, never whether the *path between them* matches. A dropdown that snaps open instantly and one that slides open over 250ms with an ease-out curve produce an identical "fully open" still frame — and an identical similarity score — despite being visibly, obviously different to look at in motion. Don't treat a passing score on the open/closed still frames as evidence the transition is also correct; it's evidence of something narrower.

## 2. What to check per ItC component

For every ItC component identified in `debug-state-simulation.md` §1 that has more than one state, check whether the mockup gives it a deliberate transition, and if so, note:
- **What triggers it** (click, hover, focus).
- **What properties actually animate** (height, opacity, transform/position, color) — not just "it animates," but specifically what's moving.
- **Any coupled secondary transform** — an icon that rotates/flips alongside the main transition (a chevron going from pointing-down to pointing-up as a dropdown opens is the classic case), a backdrop that fades in behind a modal, a label that cross-fades.
- **Duration and easing curve**, if it's meant to be replicated precisely rather than just "roughly animated."

## 3. How to extract the mockup's actual transition spec

Don't guess at duration/easing from watching it once — read the actual values:
- Inspect the mockup's CSS for `transition`/`animation`/`@keyframes` properties (duration, timing-function/easing curve, which properties are listed) directly, rather than estimating by eye.
- For any coupled icon-state transform (the chevron-flip case), check whether it's a CSS transform on the same trigger, a class-swap between two icon glyphs, or a small inline SVG/animation — the native implementation needs to replicate whichever mechanism is actually being used, not just "rotate something."
- If the mockup uses easing curves that don't map to a name the target platform has a direct equivalent for (a custom cubic-bezier), find the closest available native easing curve or replicate the bezier directly if the platform's animation system supports custom curves — don't silently fall back to a linear/default curve, which reads as visually "off" even when duration matches.

## 4. How to verify the native/real implementation

- Because this can't be verified by the still-frame similarity loop, verify it separately: capture a short video/GIF pair (mockup transition vs. real-app transition) for each ItC component with a designed transition, and do a direct side-by-side comparison — duration, easing "feel," and whether every coupled secondary transform (the icon flip, the backdrop fade) is present and firing at the right moment.
- Treat this as its own checklist item to close out per ItC component, tracked alongside (not instead of) the still-frame convergence work — a screen isn't fully at parity just because its still-frame score cleared the threshold if its interactive components still snap instead of animate, or animate with the wrong feel.
- This is lower priority than structural/layout parity in general (a wrong easing curve is a smaller UX gap than an element being in the wrong place), but it's still a real, visible gap worth closing before calling a screen "done" if the mockup clearly designed the motion intentionally rather than it being an incidental browser default.
