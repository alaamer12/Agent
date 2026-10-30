# Principles

> **Connections** (paths are relative to `references/`)
> - Read when: a judgment call the playbooks do not settle, or when you need to explain why a choice is right.
> - Skip when: a recipe already fixes the decision.
> - Read next: `entrances-and-exits.md` (for arrival and departure rules); `playbooks-component.md` (to apply the principles).

The reasoning behind the playbooks. Use it to make judgment calls the recipes do not cover, especially for entrances, exits and states that come in pairs.

## Contents
- Purpose
- Disney's principles applied to UI
- Paired states
- Continuity and spatial consistency
- Delight scales inversely with frequency
- Perceived speed

## Purpose

Animation exists to explain hierarchy, confirm an action, guide attention, maintain continuity, or add earned polish. If it serves none of these, delete it.

## Disney's principles applied to UI

| Principle | Application |
|---|---|
| Squash and stretch | Small elasticity on entry (scale 0.95 to 1) makes elements feel less rigid. Exaggerate only in rare, playful moments. |
| Anticipation | A slight opposite wind-up (a 4 to 10px offset before sliding) creates expectation. Keep it tiny and never on frequent actions. |
| Staging | Enter from where the user's attention is: list items from the top, modals from the center, sidebars from their edge, popovers from their trigger. |
| Pose to pose | Define a clear start state and end state, then let the browser interpolate. |
| Follow-through and overlap | Children lag slightly behind the container (50 to 100ms). The container arrives first, content follows. |
| Slow in, slow out | Entrances ease out: fast start, gentle landing. |
| Arcs | Natural movement curves. Combine small x and y offsets instead of straight lines where it fits the personality. |
| Secondary action | Pair a fade with a small scale or blur; add depth without a second big motion. |
| Timing | Matches weight and size: light and small is quick; large or important can take longer. |
| Exaggeration | Scale and offset amounts rise with how rare and expressive the moment is. |
| Solid drawing | Keep a consistent sense of space: elements from behind scale up, from the side slide, from a trigger grow out of it. |
| Appeal | Entrances feel welcoming. Avoid jarring pops. |

## Paired states

If open animates, close animates. If hover has motion, focus and pressed get equivalent feedback. If forward is designed, reverse is designed. Polishing only one half is the most common craft failure. Paired parts (surface and overlay, tooltip and arrow) share easing and duration.

## Continuity and spatial consistency

- Elements visible in both states change in place; do not duplicate or hard-cut shared elements.
- Overlays, trays and panels grow from the element that opened them. Where shapes allow, let the trigger become the surface.
- Confirm in place: the result of an action belongs on the control that caused it. Reserve corner toasts for results with no on-screen origin.
- Direction matches layout: forward goes the way reading goes, backward the opposite.

## Delight scales inversely with frequency

Rarer moments earn more personality. Frequent actions must be nearly invisible. Keep roughly 90% of a surface familiar and 10% novel, and put quiet structure between novel beats.

## Perceived speed

A fast ease-out feels quicker than a slow one of the same duration. Instant secondary tooltips, short spinners, and a visible immediate response to input make an interface feel fast. Smooth transitions feel faster than hard cuts at identical load times.
