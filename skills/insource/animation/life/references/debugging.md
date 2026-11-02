# Debugging animation

> Owns symptom→cause→fix; routing lives in `../SKILL.md`.

Symptom first. Use when existing animation "feels off", flickers, jumps or stutters, before deciding whether to improve or redesign.

## Quick symptom table

| Symptom | Likely cause | Fix |
|---|---|---|
| Feels slow or sluggish | Duration too long, ease-in, or delay | Under 300ms for routine, ease-out, remove delays |
| Feels jarring or abrupt | No easing or too-short duration; scale from zero | Ease-out, start from 0.95 plus opacity |
| Jumps at start or end | Missing starting state or layout shift | Define the start with a starting-style or initial state; reserve space |
| Flickers on hover | The animating element moves out from under the pointer | Animate an inner element; keep the hover target static |
| Hover replays on touch | Hover not gated | Gate with the hover media query |
| Stutters under load | Off-compositor work; see performance-and-accessibility.md | Transform and opacity only; defer work; use CSS or WAAPI |
| Restarts when triggered rapidly | Keyframes instead of transitions | Use transitions or interruptible springs |
| Goes the wrong way | Wrong origin or direction logic | Set transform origin; derive direction from the layout |
| Shaky by 1px at start or end | Layer handoff | Hint the property during the animation |
| Content stretches or distorts | Scaling a container with children | Animate position or clip instead; counter-scale children |
| Blur looks muddy or slow | Blur too large | 2 to 4px; cap at 20px |
| SVG rotates around the wrong point | Default origin on SVG | Set transform-box and origin |
| Looks fine alone, wrong together | Mixed clocks in one group | Share duration and easing |
| Never settles | Spring underdamped | Raise damping or lower bounce |

## Method

1. Reproduce and slow it down (quarter speed in the browser's animation inspector).
2. Name the symptom in the table; check its likely cause first.
3. Run the audit script on the file for mechanical causes.
4. Check the pair (is the reverse equally good?), the origin, and the frequency of the action.
5. Apply the smallest fix from the remedy hierarchy.

## Common causes

- Property and promotion causes (`transition: all`, a parent CSS variable updated every frame, animating layout properties, will-change layer management): see performance-and-accessibility.md.
- Entry animation firing again on every re-render (a changing key or remount).
- Exit animations that never run because the element is removed immediately.
- Toggling a class and immediately measuring layout.

## Inspecting in the browser

Use the animation inspector to slow playback and see easing curves; the performance panel to find long tasks that coincide with a dropped frame; layer or rendering overlays to see what is promoted and repainting. Compare 6x CPU slowdown behavior to catch fragile animations.

## When to redesign

If the fix list is longer than the animation, or the purpose fails the gate, redesign instead: run the normal flow from the gate with the existing animation recorded as the baseline.
