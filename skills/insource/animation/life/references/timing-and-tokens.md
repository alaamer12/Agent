# Timing and tokens

> The single owner of every duration, easing, stagger, scale and blur range and the tier caps; routing lives in `../SKILL.md`.

One canonical set of values, scoped by tier, so the sources of motion advice stop contradicting each other. The machine-readable copy is `assets/tokens.json`. A project's own tokens always win: detect them in recon and extend them.

Values owned elsewhere: spring presets → springs.md; gesture thresholds → gestures.md; enter/exit asymmetry → entrances-and-exits.md.

## Adopting tokens

1. Search the project for existing easing and duration variables (CSS custom properties, theme files, motion config).
2. If they exist, use them and add only missing names, in the same style.
3. If they do not, add the block at the end of this file to the global stylesheet, and use it everywhere.

## Easing

| Token | Curve | Use |
|---|---|---|
| enter | `cubic-bezier(0.22, 1, 0.36, 1)` | Entrances, exits, transform hovers, default for responding to the user |
| move | `cubic-bezier(0.25, 1, 0.5, 1)` | Slides, drawers, panels |
| onScreen | `cubic-bezier(0.645, 0.045, 0.355, 1)` | Back-and-forth movement that stays on screen |
| drawer | `cubic-bezier(0.32, 0.72, 0, 1)` | iOS-like sheets; the steep start keeps even the top of the drawer band (350ms) feeling quick |
| expo | `cubic-bezier(0.19, 1, 0.22, 1)` | Dramatic reveals, card hovers |
| press | `cubic-bezier(0.25, 0.46, 0.45, 0.94)` | Button press feedback |
| morphOpen | `linear(0, 0.45, 0.78, 1, 1.17, 1.21, 1.18, 1.12, 1.05, 1.02, 1)` | Shape/container morph openings; the overshoot is built into the curve |
| morphClose | `cubic-bezier(0.32, 0.72, 0, 1)` | Morph closings; same curve as drawer |
| constant | `linear` | Spinners, marquees, scroll-scrubbed progress only |

Entering and exiting use ease-out. Moving on screen uses ease-in-out. Hover color and opacity use plain `ease`. Never ease-in on UI: it delays the moment the user is watching. Built-in named curves are weak; prefer the custom curves above, tuned in the browser's curve editor if contested. Use a spring (see the springs reference) when the motion needs physics.

## Duration

| Element | Duration |
|---|---|
| Press feedback | 100 to 160ms |
| Tooltips, small popovers | 125 to 200ms |
| Dropdowns, selects | 150 to 250ms |
| Modals, drawers | 200 to 350ms |
| Hover, color and opacity | 200ms |
| Hover, transform | 100 to 150ms |
| Slide on screen | 200 to 300ms |
| Page transition | 250 to 400ms |
| Rare moments | 300 to 600ms |
| Showcase | 600 to 1600ms with labeled beats |

Scale duration with distance: a 6px shift stays under 150ms; a full-screen slide may exceed 300ms. Enter/exit asymmetry: see entrances-and-exits.md §Exits.

## Tiers

| Tier | Cap | Where |
|---|---|---|
| routine | 300ms | Frequent or functional UI |
| rare | 600ms | Occasional or first-time moments |
| showcase | 1600ms | Marketing, hero, onboarding story; sequences carry labeled beats |

A duration over its cap needs a one-line reason in the spec or report.

## Stagger

| Level | Offset | Notes |
|---|---|---|
| List items | 30 to 50ms | Whole list finishes within about 300ms; group beyond roughly five items |
| Section level | 80 to 100ms | Title block, description, actions |
| Word level | about 80ms | Hero headline only |

Use smaller offsets on small screens. Vary delay and distance by importance. Never block interaction while a stagger plays.

## Distance, scale and blur

- Offsets come from 4, 8, 12, 16, 24px. Entrances usually travel 8 to 16px; exits a fixed 4 to 12px regardless of element size.
- Entrances start at scale 0.95 to 0.97 with opacity; small anchored popovers around 0.92; 0.8 only for rare delight; never from zero.
- Press down to 0.97 (0.96 to 0.98). Hover scale 1.01 to 1.02; 1.05 reads inflated.
- Blur bridges a crossfade at 2 to 4px; up to 8px for a rare entrance; hard cap 20px, and heavy blur is expensive on some browsers.

## Resolved conflicts

| Question | Resolution |
|---|---|
| Ease-out curve value | `enter` token above; a project's existing strong ease-out is equivalent and wins |
| UI under 300ms vs longer entrances | Under 300ms for routine. Longer allowed only for rare and showcase tiers, stated in the report |
| Stagger cap vs per-item offset | 30 to 50ms per item, about 300ms total, group beyond about five items; section and word offsets are separate levels |
| Start scale 0.8 vs 0.9 to 0.97 | 0.95 to 0.97 default, 0.92 popovers, 0.8 only for rare delight |
| Hero sequence 800 to 1600ms vs 300ms | Showcase tier only, with labeled beats |
| Layout tween exceptions | Default never; a deliberate container tween (card resize, container morph) is allowed when labeled `layout_exception` |
| Blur amount | 2 to 4px default, 8px rare entrance, 20px hard cap |
| Drawer and modal duration | 200 to 350ms stands as the canonical range (wider numbers elsewhere are pending correction by their files) |
| Stagger bands | 30 to 50ms items, 80 to 100ms sections, about 80ms hero words: these are THE ranges; other files link here |
| Package name for new work | New React work uses `motion` with `motion/react` imports; follow the project otherwise (details: stacks/react-motion.md) |
| Scroll reveal replay | Reveal once, never replay on scroll-up (implementation: scroll.md) |

## CSS custom properties block

```css
:root {
  --ease-enter: cubic-bezier(0.22, 1, 0.36, 1);
  --ease-move: cubic-bezier(0.25, 1, 0.5, 1);
  --ease-on-screen: cubic-bezier(0.645, 0.045, 0.355, 1);
  --ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);
  --ease-expo: cubic-bezier(0.19, 1, 0.22, 1);
  --ease-press: cubic-bezier(0.25, 0.46, 0.45, 0.94);

  --dur-press: 140ms;
  --dur-popover: 180ms;
  --dur-dropdown: 220ms;
  --dur-modal: 260ms;
  --dur-slide: 260ms;
  --dur-page: 320ms;
  --stagger-list: 40ms;
}
```
