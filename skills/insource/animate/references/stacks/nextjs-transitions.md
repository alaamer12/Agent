# Stack: Next.js route transitions

> **Connections** (paths are relative to `references/`)
> - Read when: Next.js App Router route or page transitions, especially with exit animation.
> - Skip when: other frameworks, or in-page transitions.
> - Read next: `stacks/css-native.md` (view transitions); `stacks/react-motion.md` (presence and layout APIs).

Page and route transitions in the App Router. The router replaces content on navigation, so exit animations need extra structure. Verify details against the installed Next.js and animation library versions; the exit approach relies on internals that can change.

## Contents
- Choosing an approach
- Enter-only with a template
- Exit and enter with a frozen router
- View transitions
- Direction awareness
- Debug checklist

## Choosing an approach

| Need | Approach |
|---|---|
| Subtle enter animation on every page | `template.tsx` with an entry animation |
| True exit then enter between routes | `template.tsx` plus a presence wrapper and a frozen router context |
| Shared elements across pages, minimal code | The platform's view transitions |
| Core navigation used constantly | Keep it very light, or a short crossfade only |

Do not block navigation on animation: loading begins immediately and the animation covers the wait.

## Enter-only with a template

A `layout.tsx` persists across navigations; a `template.tsx` creates a new instance for each navigation, so entry animations replay.

```tsx
// app/template.tsx
"use client";
import { motion } from "motion/react";
export default function Template({ children }: { children: React.ReactNode }) {
  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}>
      {children}
    </motion.div>
  );
}
```

## Exit and enter with a frozen router

Exit animations fail by default because the old page unmounts immediately when the router swaps the tree. The standard workaround freezes the router context for the exiting child so it keeps rendering the old content while the presence wrapper animates it out.

```tsx
// app/template.tsx (sketch)
"use client";
import { AnimatePresence, motion } from "motion/react";
import { usePathname } from "next/navigation";
import { FrozenRouter } from "@/components/frozen-router";

export default function Template({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <AnimatePresence mode="popLayout" initial={false}>
      <motion.div key={pathname}
        initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -4 }}
        transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}>
        <FrozenRouter>{children}</FrozenRouter>
      </motion.div>
    </AnimatePresence>
  );
}
```

`FrozenRouter` reads the layout router context once and re-provides that frozen value to its children. It depends on an internal context import from the framework, so pin the version, comment the dependency, and keep the enter-only fallback ready.

## View transitions

Where the framework and browser support it, wrap navigations in the view transition API (see the CSS-native stack file). Give shared elements unique `view-transition-name` values that match across both pages, customize the pseudo-elements, and keep the default crossfade for the rest. Provide a fallback for engines without support.

## Direction awareness

Compute direction from navigation history or route depth (deeper is forward) and expose it to the transition (a data attribute on the root, or the presence `custom` value). Back and forward gestures should reverse the motion.

## Debug checklist

- Exit never plays: the old tree unmounted; check the frozen router and the presence wrapper placement.
- Double animation: both a layout and a template animate; keep one level.
- Flash on first load: use `initial={false}` on the presence wrapper.
- Scroll jumps: reset scroll deliberately at the right time.
- Layout shift: reserve space; use `popLayout` so the exiting page leaves the flow.
- Hydration warnings: avoid random keys or time-based values in the animated wrapper.
