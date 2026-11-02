# Stack: React with Motion

> Owner of Motion/framer-motion API implementation notes. Routing lives in ../../SKILL.md.

Notes for projects using the Motion library for React. Check which package the project already uses before adding anything: new work uses `motion` with imports from `motion/react`; a project on the older package keeps it, and migration is a follow-up. Verify props against the installed version.

## Basics

```tsx
import { motion, AnimatePresence, MotionConfig, useReducedMotion } from "motion/react";

<motion.div
  initial={{ opacity: 0, scale: 0.95, y: 8 }}
  animate={{ opacity: 1, scale: 1, y: 0 }}
  exit={{ opacity: 0, scale: 0.95, y: 4 }}
  transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
/>
```

Never `initial={{ scale: 0 }}` (the entry-scale band: ../timing-and-tokens.md). Set `style={{ originX, originY }}` or a transform-origin for anchored surfaces.

## Springs and transitions

```tsx
transition={{ type: "spring", duration: 0.4, bounce: 0 }}      // perceptual
transition={{ type: "spring", stiffness: 500, damping: 40 }}   // physical
transition={{ layout: { type: "spring", duration: 0.4, bounce: 0.15 } }}
```

Use a duration-based ease for opacity and color, a spring for position, scale and anything gesture-driven.

## Presence and exit

```tsx
<AnimatePresence mode="popLayout" initial={false}>
  {open && <motion.div key="panel" exit={{ opacity: 0 }} />}
</AnimatePresence>
```

- `AnimatePresence` must stay mounted; only its children toggle.
- Each direct child needs a stable, unique `key`; changing the key re-runs the animation.
- `mode="popLayout"` lets siblings re-layout while an exit plays; `mode="wait"` plays the exit first (slower, use sparingly).
- `initial={false}` skips the first mount animation.
- Pass `custom` to `AnimatePresence` and the child so exiting elements receive the latest direction.

## Layout animation

```tsx
<motion.div layout />                       // animates size and position changes
<motion.div layoutId="card-42" />            // shared element between two places
```

Layout animation uses transforms to animate size and position. Children can distort; set `layout` on them as well or use `layout="position"`. For container resizes, wrap content in its own layout child. Avoid layout animation on very large trees.

## Variants and stagger

```tsx
const list = { show: { transition: { staggerChildren: 0.04, delayChildren: 0.02 } } };
const item = { hidden: { opacity: 0, y: 8 }, show: { opacity: 1, y: 0 } };
<motion.ul variants={list} initial="hidden" animate="show">
  <motion.li variants={item} />
</motion.ul>
```

Stagger semantics and order rules: ../synchronization.md. Reverse stagger on exit with `staggerDirection: -1`, and keep exit offsets shorter.

## Gestures and values

```tsx
<motion.button whileTap={{ scale: 0.97 }} transition={{ duration: 0.14 }} />
<motion.div drag="x" dragElastic={0.15} dragConstraints={{ left: 0, right: 0 }}
  onDragEnd={(_, info) => info.velocity.x > 500 && dismiss()} />
```

Use motion values (`useMotionValue`, `useTransform`, `useSpring`) for values that change continuously (drag, scroll) so React does not re-render each frame.

## Reduced motion

```tsx
<MotionConfig reducedMotion="user">{children}</MotionConfig>   // transform and layout animations are disabled, opacity kept
const reduce = useReducedMotion();
```

Combine with explicit gentler variants for spatial effects; the reduced-motion policy is owned by ../performance-and-accessibility.md.

## Performance notes

- The `x`, `y` and `scale` shorthands are applied by the library on the main thread (main-thread rules and property tiers: ../performance-and-accessibility.md). Hardware-accelerated paths exist for opacity, transform strings, clip-path and filter.
- Prefer one parent animation over many independent child animations.
- Do not animate `width`, `height`, `top` or `left`.

## Pitfalls

- Reusing the same `key` for different content (no exit plays).
- Removing the `AnimatePresence` child from a parent that unmounts.
- Passing new object literals for variants on every render (use constants).
- Starting from `scale: 0`.
- Forgetting the reduced-motion configuration.
