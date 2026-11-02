# Stack: Next.js route transitions

> Owner of App Router transition structure: template enter, FrozenRouter exit, view transitions integration, route-transition debugging. Routing lives in ../../SKILL.md.

Page and route transitions in the App Router. The router replaces content on navigation, so exit animations need extra structure. Verify details against the installed Next.js and animation library versions; the exit approach relies on internals that can change.

## Choosing an approach

| Need | Approach |
|---|---|
| Subtle enter animation on every page | `template.tsx` with an entry animation |
| True exit then enter between routes | `template.tsx` plus a presence wrapper and a frozen router context |
| Shared elements across pages, minimal code | The platform's view transitions |

How light frequent navigation should be is gate.md's call; the navigation-versus-animation obligation is owned by ../playbooks-transition.md.

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

Direction awareness (history or route depth, forward and back travel, gesture reversal) is owned by ../playbooks-transition.md; expose the computed direction to the transition as a data attribute on the root or the presence `custom` value.

## Debug checklist

- Exit never plays: the old tree unmounted; check the frozen router and the presence wrapper placement.
- Double animation: both a layout and a template animate; keep one level.
- Flash on first load: skip the mount animation (`initial={false}`, react-motion.md).
- Scroll jumps: reset scroll deliberately at the right time.
- Layout shift: reserve space; keep the exiting page out of the flow with the presence mode documented in react-motion.md.
- Hydration warnings: avoid random keys or time-based values in the animated wrapper.
