# Playbook: component

> Owns component lifecycle recipes, origin choices and the component workflow. Routing lives in ../SKILL.md.

Animating a complete component as one visual unit: dialog, popover, dropdown, drawer, toast, card, menu, accordion, list item, panel. The component may contain many parts; the animation is designed around the component.

## Workflow

1. Identify the component's lifecycle: enter, exit, move or resize, emphasize, and any interactive behavior.
2. Gate each lifecycle step. Occasional surfaces (modals, drawers) get standard animation; frequent ones get the lightest touch.
3. Decide the origin: where the component should appear to come from.
4. Decide the container-versus-children relationship and which synchronization form applies.
5. Choose technique and timing; define the exit as its own design; implement and test interruption.

## Enter, exit, move, emphasize

Enter and exit treatments are owned by entrances-and-exits.md.

| Step | Typical treatment |
|---|---|
| Move | Layout animation to the new position, ease-in-out or a spring |
| Emphasize | A single brief scale or color pulse; never a loop on routine UI |

## Origin

| Component | Origin |
|---|---|
| Popover, dropdown, tooltip, context menu | Its trigger (transform origin set to the trigger side or the pointer point) |
| Modal, dialog | Center; modals do not originate from a trigger |
| Drawer, sheet | The screen edge it attaches to |
| Toast | The edge or corner it lives in; a result on a control is confirmed on the control |
| List item added | Its slot in the list, with neighbors making room |
| Container morph | The trigger itself becomes the surface |

Setting the origin is the single cheapest fix for animation that feels wrong.

## Container versus children

The one-level rule (container moves xor children stagger) and every relation between parts are owned by synchronization.md.

## Standard recipes

Popover or dropdown (origin-aware, fast)

```css
.popover { transform-origin: var(--trigger-origin, top center); }
.popover[data-state="open"]   { animation: pop-in 180ms var(--ease-enter); }
.popover[data-state="closed"] { animation: pop-out 120ms var(--ease-enter); }
@keyframes pop-in  { from { opacity: 0; transform: scale(0.95); } }
@keyframes pop-out { to   { opacity: 0; transform: scale(0.95); } }
```

Modal: overlay fades in; the dialog enters with opacity and scale from 0.95 (or a small translate) within the modal/drawer band in timing-and-tokens.md; the exit is shorter. The paired overlay/dialog clocks follow synchronization.md (Instant).

Drawer: translate from the edge with the drawer curve at the modal/drawer duration band in timing-and-tokens.md. Swipe-to-dismiss follows the finger with no easing and springs after release (see the gestures reference).

Toast: slide and fade in from the edge, 200 to 300ms; new toasts push others with a layout animation; the exit runs 150 to 200ms. Interruption: toasts fire rapidly, so use transitions that retarget, not restarting keyframes (policy: performance-and-accessibility.md).

List item add and remove: new item enters with opacity and an 8px offset; removed items exit and the remainder close the gap with a layout animation. Remove uses a short fade rather than reversing the entrance.

Accordion or collapse: avoid animating height with layout tweens on large content when you can use clipping or grid-row transitions; if a measured-height tween is chosen, label it as a container tween exception — the ruling and values live in timing-and-tokens.md (Resolved conflicts).

Card hover or select: transform lift with the expo curve; shadows change on a separate fading layer.

## Layout changes

- Prefer a layout animation (the library measures before and after and animates the delta with transform) over tweening width or height directly.
- Container resize with content swap: animate the container to the new size while the content crossfades with a small blur bridge, fixing child distortion by counter-scaling or by animating position only.
- Shared element between two places: give both ends the same identifier; use the platform view transition when the stack supports it.

## Creative lanes for component

The idea lanes are owned by creative-direction.md (master lanes table); pick lanes there that suit a whole surface arriving, moving or leaving.

## Checklist

- [ ] Origin set deliberately
- [ ] Exit designed, faster than enter
- [ ] One level of entrance per container
- [ ] Paired parts (surface and overlay) share easing and duration
- [ ] Interruption handled (close mid-open, reopen mid-close)
- [ ] Focus management does not wait on the animation
- [ ] Reduced-motion variant
