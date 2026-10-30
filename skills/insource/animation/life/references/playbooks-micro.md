# Playbook: micro

> **Connections** (paths are relative to `references/`)
> - Read when: the command is micro: a button, icon, badge, toggle, number, text swap, hover, press, focus, loading indicator, success or error feedback.
> - Skip when: the command is component or transition.
> - Read next: `timing-and-tokens.md` (for values); `svg-and-clip-path.md` (for drawn checks, fills and masks); `springs.md` (for physical press feel).

Animating a single element or a small visual unit: a button, icon, badge, toggle, number, input, link, chip. Small in scope, but it can be interactive, synchronized, and as creative as the tier allows.

## Contents
- Workflow
- State inventory
- Standard recipes
- Creative lanes for micro
- Number and text changes
- Success, error and loading
- Checklist

## Workflow

1. List the element's states (below) and which pairs need a designed reverse.
2. Gate each state: frequency decides which states animate at all. A button pressed 100 times a day gets press feedback and nothing else.
3. Classify interaction: press, hover and focus are interactive; success and error are not.
4. Choose technique and timing per state, then check the pairs share a family (easing, duration).
5. Build every state, including disabled and reduced motion.

## State inventory

| State | Animate? | Notes |
|---|---|---|
| rest | n/a | The reference every other state returns to |
| hover | Only on devices that hover; low frequency elements | Subtle; 100 to 200ms |
| focus | Immediate visible indicator, optional short fade | Never remove the outline; keyboard users depend on it |
| press / active | Yes, almost always | 0ms response, scale 0.97 |
| disabled | No motion; static change | Do not animate toward unavailable |
| loading | Spinner or progress; button keeps its size | Avoid layout shift |
| success / error | Yes, rare tier | Confirm in place |

## Standard recipes

Press feedback

```css
.btn { transition: transform 140ms var(--ease-press); }
.btn:active { transform: scale(0.97); }
```

Hover that does not flicker on touch

```css
@media (hover: hover) and (pointer: fine) {
  .card { transition: transform 150ms var(--ease-enter); }
  .card:hover { transform: translateY(-2px); }
}
```

Hover target flicker: when the hovered element moves out from under the pointer, animate an inner element and keep the hover target (the wrapper) static.

Toggle or checkbox: animate the thumb with transform, color with a 200ms ease; indeterminate and checked share a curve. Radio: scale the dot from 0.8 to 1 with opacity; the ring changes color only.

Icon swap (two icons, one slot): animate both icons with opacity, scale from 0.25 to 1 and a 4px blur, so the swap reads as one object changing. Keep both mounted for a continuous crossfade, or use presence animation with an exit.

Badge or count pop: spring from scale 0.6 to 1 with a light bounce; the number swaps with the number rule below.

Input focus: ring fades in 150ms; label floats with transform, not font-size changes.

Hold to confirm: fill progress with a clip-path inset that tracks the hold (about 2s linear while pressed), snap back in 200ms on release, with ease-out. Pair with a tiny 0.97 press scale.

## Creative lanes for micro

| Lane | Micro idea | Notes |
|---|---|---|
| Light and material | A sheen sweeps across on hover or on success; glass-like brightening on press; subtle depth shadow that tightens on press | Usually needs the HTML prototype. Keep the sheen on a compositor layer. |
| Self-transformation | Label morphs into a check; button becomes a progress bar then a confirmation | Fix the width to avoid layout shift; clip, don't resize |
| Physics | Magnetic pull toward the cursor with a spring, weighted press with overshoot on release | Cap the pull distance; disable on touch |
| Reveal | Underline draws from the pointer's entry side; fill wipes in with a clip-path | Reverse from the exit side |
| Typographic | Letters shift weight on hover; label rolls vertically like a counter | Keep tabular widths |
| Trace | An outline draws around the element on focus or success | Measure the path length instead of guessing |
| Ambient | Idle glow breathing on a primary call to action | Rare; pause off-screen |

All of these are subject to the gate. A frequently pressed control gets the press recipe and nothing creative.

## Number and text changes

- Use tabular numbers so digits do not shift.
- Odometer roll for values that change on action: digits roll vertically in the direction the value moved, 200 to 300ms, with a slight blur at mid-roll.
- Text swap: outgoing text exits upward 4 to 8px with fade, incoming enters from below; or crossfade with a 2 to 4px blur bridge.
- Never animate a number the user is actively reading or comparing.

## Success, error and loading

- Success: confirm on the control that triggered it. A check that draws in over 300 to 400ms, the label held for a beat, then the control returns to rest. Rare tier only.
- Error: a short horizontal shake (about 4 to 8px, three to four swings, 300ms) on the field, plus a persistent text message for accessibility. Shake alone is not enough.
- Loading: keep the button's dimensions fixed; swap the label with a spinner without resizing; avoid long fade-outs of the label.

## Checklist

- [ ] Press feedback at 0ms response
- [ ] Hover gated to hover-capable devices
- [ ] Focus indicator visible and immediate
- [ ] Each animated state has a designed return
- [ ] No layout shift when states change
- [ ] Reduced motion keeps the confirmation but drops movement
