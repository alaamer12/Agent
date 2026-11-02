# Gestures and drag

> Owner of drag core rules, velocity projection, rubber-banding, axis commitment, pointer capture, dismiss, detents, rotary, reorder and gesture thresholds. Routing lives in ../SKILL.md.

Direct manipulation: dragging, swiping, flicking, rotary controls, detents, swipe to dismiss, drag to reorder. The finger leads; animation only takes over after release.

## Core rules

- While the pointer is down, the element is locked to it with no easing and no delay. Any smoothing during drag makes the interface feel disconnected.
- After release, hand velocity to a spring or a momentum projection so the motion continues naturally (release velocity into the spring: springs.md).
- Record the grab offset on pointer-down so the element does not jump to center on the cursor.
- Set transform directly on the moving element; the parent-CSS-variable ban and its reason: performance-and-accessibility.md (Main-thread discipline).
- Interactive targets are at least 44px; set `touch-action` to the axis you handle so the browser does not scroll against you.

## Velocity and momentum

Track recent pointer samples (position and time over the last 50 to 100ms) and compute velocity at release. Project the landing point as `position + velocity * k` (k around 0.1 to 0.2 seconds of glide), pick the nearest valid resting state from that projection, then spring there with the release velocity as the initial velocity. A quick flick should dismiss even if the distance is short; use both distance and velocity (about 0.11 px per ms as a starting flick threshold).

## Boundaries and rubber-banding

Past a limit, apply increasing resistance (for example movement divided by a growing factor, or a logarithmic curve) instead of a hard stop, and spring back on release. Resistance communicates the edge without an error feel.

## Axis commitment

On a diagonal start, wait for about 10px of movement, then commit to the dominant axis and ignore the other. Without commitment, vertical scroll and horizontal swipe fight.

## Pointer capture

Capture the pointer on pointer-down so the gesture keeps working when the pointer leaves the element; release on pointer-up or cancel. Handle cancel (system gesture, lost focus) by springing to the nearest valid state.

## Swipe to dismiss

- Follow the finger, scale or fade lightly with distance.
- On release: dismiss if the projected position passes the threshold or velocity is high; otherwise spring back.
- Exit path and direction of travel after a gesture dismissal: entrances-and-exits.md (Exits).
- Multi-touch and nested scrolling: prevent a dismiss while the inner content is scrolled away from its top.
- Keep a non-gesture dismiss (a button, the escape key) with the same animation.

## Detents and snapping

For controls with discrete stops (a ruler picker, a snap point sheet): while dragging, the element follows freely; on release, spring to the nearest detent using projection. Add a very light tick animation when passing a detent; sound or haptics are optional extras.

## Rotary controls

Track the angle with `atan2` from the center, unwrap the angle across the 180 degree boundary so it does not jump, and apply resistance outside the allowed range. Snap to detents on release.

## Drag to reorder

The dragged item follows the pointer and lifts (a slight scale and shadow on a separate layer). Other items shift to make room with a layout animation (spring or 200ms ease-out). On drop, the item springs to its slot. Auto-scroll near container edges; announce the new position for assistive tech.

## Checklist

- [ ] No easing while the pointer is down
- [ ] Grab offset preserved
- [ ] Velocity handed to the post-release spring
- [ ] Axis committed; touch-action set
- [ ] Pointer captured; cancel handled
- [ ] Non-gesture alternative exists
- [ ] Reduced-motion: keep drag, drop decorative spring and tilt
