---
name: tailwind
version: 1.0.1
author: Amr
specialized: tailwind
description: 'Tailwind CSS v4 (v3-compatible), one battery, six modules: design-system (token scales, oklch/P3, theme namespaces), config (CSS-first directives @theme/@source/@plugin/@utility/@custom-variant, @apply/@layer/@reference scoped-style fix), migration (v3-to-v4 decision, audit-codemod-verify, single breaking-change catalog, traps and shims), dynamic-classes (runtime bg-${x}-500 never generates: four ranked fixes, @source inline grammar), utility-soup (3-use extraction, component-vs-@apply, prettier/eslint sorting, clsx/twMerge), validator (cross-module review rules, v3/v4 detection, advisory CI). The router picks ONE module and reads only its method.md. Triggers: Tailwind setup or @theme tokens, v3 to v4 upgrade, classes work in dev but not production, safelist or @source inline, too many utility classes one line, Cannot apply unknown utility class, tailwind-merge, audit or review a Tailwind codebase. Not for general styling architecture (styling build/retrofit levels).'
when_to_use: Any Tailwind CSS task — configuring v4, defining theme tokens, migrating v3 to v4, fixing classes missing in production, refactoring utility soup, or auditing a Tailwind codebase.
argument-hint: '[design-system|config|migration|dynamic-classes|utility-soup|validator] <target>'
---

# tailwind — one battery, six modules of Tailwind CSS practice

Name a module and the target; with no module named, the dispatch table decides. Each module is a
complete workflow in its own folder. The rule that spans them: **load one `method.md`** — never run
several modules' machinery for a one-module job.

## Modules

| Module | The request sounds like | Method |
|---|---|---|
| `design-system` | "what spacing/color is this", "design tokens for Tailwind", "oklch vs hex", "extend the theme" | [`design-system/method.md`](./design-system/method.md) |
| `config` | "set up Tailwind v4", "how does `@theme` work", "`@apply` fails in scoped style", "custom utility / variant" | [`config/method.md`](./config/method.md) |
| `migration` | "upgrade v3 to v4", "borders disappeared after upgrade", "should I even migrate", "safelist moved" | [`migration/method.md`](./migration/method.md) |
| `dynamic-classes` | "classes work in dev but not production", "`bg-${color}-500` does nothing", "safelist dynamic values" | [`dynamic-classes/method.md`](./dynamic-classes/method.md) |
| `utility-soup` | "30 classes on one element", "when do I extract a component", "class order keeps drifting", "twMerge conflict" | [`utility-soup/method.md`](./utility-soup/method.md) |
| `validator` | "audit my Tailwind code", "pre-PR check the styling changes", "find all dynamic classes" | [`validator/method.md`](./validator/method.md) |

## Dispatch

- **Setting up or extending a project** → `config` (directives) with `design-system` (values) beside it
  for token choices. The CSS-first setup is the entry point; token scales answer "what value exists".
- **An existing project changed when you bumped it** → `migration` owns the breaking-change catalog;
  it is the single owner — no other module restates those tables.
- **Style exists in DOM but not in CSS** → `dynamic-classes`; the plain-text scanner rule explains all
  such failures.
- **Markup readable?** → `utility-soup`. **Code review / CI** → `validator` (reports only; the fix
  lives in the module it cites).

## Shared laws

- **The scanner reads plain text, never code.** A class must exist as a complete literal token in
  some scanned file to be generated. Every other law is downstream of this one.
- **Tokens over raw values.** `@theme` namespaces (`--color-*`, `--spacing`, `--breakpoint-*`) are the
  single source of truth; arbitrary values are the escape hatch, not the default.
- **v4 by default, v3 by explicit need.** v4 requires Safari 16.4+/Chrome 111+/Firefox 128+ and drops
  preprocessors; if the project cannot meet that baseline, it stays on v3.4 with full v3 rules. Never
  define the same token in both `@theme` and the JS config.
- **Extraction is earned.** Components on the third copy; `@apply` is for non-framework contexts.
- **Conditional styling is a lookup, not a build.** A static map of prop → complete class string is
  the Tailwind form of the parent battery's `build` rule 4 (`/styling`).

## Layout

```
tailwind/
  SKILL.md            # this router
  design-system/      # method.md + references/
  config/             # method.md + references/
  migration/          # method.md + references/   (single owner of all v3→v4 breaking-change tables)
  dynamic-classes/    # method.md + references/   (single owner of the @source inline grammar)
  utility-soup/       # method.md + references/
  validator/          # method.md + references/
```

## Source

Adapted from [Impertio-Studio/TailwindCSS-Claude-Skill-Package](https://github.com/Impertio-Studio/TailwindCSS-Claude-Skill-Package)
(MIT) — a nine-sub-skill meta-skill consolidated into this six-module battery. Origin package paths,
workspace-specific review rules, and pointers to skills the package never shipped were revoked; the
per-module verified `tailwindcss.com` sources were kept.
