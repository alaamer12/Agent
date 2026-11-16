---
name: styling
version: 1.1.1
author: Amr
specialized: none
lint-accept:
  mixed-composition: "Intentional hybrid: build/retrofit are internal platform-neutral levels; specialized/scss, specialized/tailwind and specialized/daisyui are independent technology-bound child skills. Keep as-is."
description: 'Styling experience, one skill, two levels: build (write NEW styling right on any stack — per-module stylesheets, no monolith, role-named tokens as single source of truth, a downward-only layer chain, expressive names, conditional styling as a lookup not a build, runtime values through a dynamic channel) and retrofit (take an EXISTING project''s hardcoded/duplicated styling into a token-driven system: inventory, incumbent gate, one evidence-based native-vs-library decision, pixel-safe migration slices, no-hardcoding guards, before/after parity evidence). The router picks ONE level and reads only its method.md. New work or styling structure is yours → build; existing mess to centralize and prove parity → retrofit. Triggers: organize CSS/XAML/QML, design tokens, style layer chain, inline dumps, built class strings, styleup, style-up, make styles maintainable or professional, remove hardcoded styles, centralize colors/typography/spacing. Not for visual redesign (denoise) or component galleries (components).'
when_to_use: The user asks how to organize or write new styling (build), or to make an existing project's styling maintainable, token-driven and enforced with parity evidence (retrofit).
argument-hint: "[build|retrofit] <target>"
---

# styling — one skill, two levels of styling experience

Name a level and the target; with no level named, the dispatch test below decides. Each level is a
complete workflow in its own folder. The only rule that spans them: **load one `method.md`** —
never run both levels' machinery for a one-level job.

## Levels

| Level | The request sounds like | Method |
|---|---|---|
| `build` | "how do I organize CSS/XAML/QML", "write new styling", "design tokens for a new surface", "the style layer chain", "inline dumps / built class strings" | [`build/method.md`](./build/method.md) |
| `retrofit` | "styleup this project", "make styles maintainable / professional", "remove hardcoded or duplicated styles", "centralize colors/typography/spacing", "introduce design tokens into existing code" | [`retrofit/method.md`](./retrofit/method.md) |

## Dispatch — the levels get confused

- **build is greenfield.** Styling structure is yours, or new work slots into the project's existing
  chain. It constructs the project so a true design system can exist — structure, chain, naming,
  decisions made right the first time.
- **retrofit is brownfield.** Code already written: hardcoded/duplicated values to inventory, migrate
  into tokens with parity evidence, and lock with guards. It works inside the styling system the
  project already uses.
- Both share one goal — enhance the styling experience — at different layers. A retrofit that
  graduates leaves the project styled correctly; new work after a retrofit follows build.

## Shared laws

- **Tokens are the single source of truth.** Role-named, never raw values at consumption sites.
- **Styling is a chain of layers, imports point downward only.** The layer count is the project's
  call, not this skill's.
- **Conditional styling is a lookup, not a build.** Runtime values go through a dynamic channel.
- **The ledger both levels optimize:** maximum reusability, minimum overriding, maximum flexibility,
  minimum inline styling.
- **Platform-neutral.** HTML/Web, Blazor, MAUI, Qt and every other styling system — mechanism names
  differ, the layers do not. [bracketed] options are illustrative, not a closed menu.

## Boundaries — other skills

| Situation | Skill |
|---|---|
| Redesigning an existing UI for calm/readability | `denoise` |
| Reviewing component × state coverage | `components` |
| Deriving which states a screen must handle at all | `stateful` |
| Choosing a styling library/framework from scratch | `techstack` / `thebest` |

## Specialized skills — fixed technology

`specialized/` groups technology-specific skills. Each keeps its own `SKILL.md` and stays independently
invocable; the two levels above remain platform-neutral. When a project commits to one technology, use
its specialized skill for that language's mechanics instead of bending the general levels.

| Technology | Skill | Use it for |
|---|---|---|
| SCSS / Sass | `/scss` (in `specialized/scss`) | Sass module system (`@use`/`@forward`), mixins, functions, `@extend`, loops, nesting, compilation — the SCSS idiom the platform-neutral levels only sketch in [brackets] |
| Tailwind CSS | `/tailwind` (in `specialized/tailwind`) | v4 CSS-first config (`@theme`/`@source`/`@utility`), token scales, v3→v4 migration, dynamic-class generation, utility-soup tooling, review rules — itself a six-module battery |
| daisyUI | `/daisyui` (in `specialized/daisyui`) | daisyUI 5 on Tailwind 4: class names for 76 components, semantic colors, themes, install/config/usage rules, the component discovery protocol — the official daisyUI skill, kept verbatim |

Reach for a specialized skill only when the project actually uses that technology; otherwise the
platform-neutral level applies.

## Layout

```
styling/
  SKILL.md            # this router
  build/              # greenfield level
    method.md
    references/       # 01-structure-and-tokens, 02-conditional-and-runtime, 03-composition-and-variants, 04-layer-chain-and-naming
    examples/         # styling-polyglot-walkthrough
  retrofit/           # brownfield level
    method.md
    references/       # library-decision
    scripts/          # capture_matrix.py, palette_diff.py
    examples/         # web-token-layer, maui-token-layer
  specialized/        # fixed-technology skills (own SKILL.md, independently invocable)
    scss/             # SCSS/Sass mechanics → /scss
    tailwind/         # Tailwind CSS battery (6 modules) → /tailwind
    daisyui/          # official daisyUI 5 skill (meta: install/config/usage/colors) → /daisyui
```

## Done

Each level owns its done-list: [build](./build/method.md) (rules + procedure) and
[retrofit](./retrofit/method.md#definition-of-done).