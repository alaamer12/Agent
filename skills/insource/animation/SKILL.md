---
name: animation
description: 'Animation meta-skill — a router, nothing more. Routes any request about motion to the sub-skill that actually holds the functionality: `life` (UI motion — micro, component, transition, entrances and exits, hover/press feedback, scroll, springs, onboarding intros, discovery, prototypes, animation review), `ascii` (character/terminal motion — ASCII intro or loader, image or video to ASCII, plasma and wave fields, per-glyph cascades, Three.js AsciiEffect), `svg` (25 SVG/logo animation styles — chrome-liquid, draw-fill, loading-loop, elastic-entrance, neon, ripple, mosaic, unroll, with light/dark variants). Use when the user asks for animation, motion, transitions, a page or route to move, an animated logo, a retro/ASCII effect, or wants an interface to "feel alive", even if no one says the word animate. Adds no rules, standards, references, or checks of its own: those belong to the sub-skill performing the work. Out of this domain: static visual quality, component state galleries, mockup fidelity, real video.'
when_to_use: Any motion or animation request — UI transitions, micro-interactions, animated logos/SVGs, ASCII or terminal motion — where the work must first be assigned to the right sub-skill. Also /animation.
argument-hint: "[life|ascii|svg] <command or style> <target>"
---

# Animation

The Viber `animation` Meta Skill: one address for the motion domain, three sub-skills underneath it.
**This file contains no functionality.** It decides which sub-skill to read and nothing else — no workflow,
no standards, no references, no scripts. Everything that constrains the work lives in the sub-skill that
performs it.

## Route

| What the request actually is | Read | Entry form |
|---|---|---|
| Interface motion: one element (hover, press, state swap, number roll), a whole component as one visual unit, view/page/route transitions forward **and** back, entrances and exits, first-run and onboarding intros, scroll-linked motion, gestures and springs, finding what should (or must not) animate, prototyping options before building, reviewing or debugging existing animation, matching a recorded animation | [`life/SKILL.md`](life/SKILL.md) | `/animation life micro\|component\|transition <target>` |
| Motion made of characters: terminal intro or loader, image/video → ASCII, generative plasma/wave/noise fields, per-glyph cascade or domino, Three.js `AsciiEffect`, glyph-level coloring and masking | [`ascii/SKILL.md`](ascii/SKILL.md) | `/animation ascii <kind>` |
| A static SVG logo/icon animated with one of 25 named treatments (`liquid`, `draw`, `load`, `elastic`, `rise`, `iris`, `neon`, `pulse`, `flip`, `comet`, `focus`, `crt`, `chroma`, `mosaic`, `ripple`, `spark`, `engrave`, `grain`, `tide`, `polarity`, `blinds`, `assemble`, `lantern`, `pinwheel`, `unroll`), including light/dark variants of an existing file | [`svg/SKILL.md`](svg/SKILL.md) | `/animation svg <style> <file.svg>` |

## When more than one row fits, in this order

1. A `.svg` target or one of the 25 named SVG effects → **svg**.
2. Glyphs, a terminal, or character-art output → **ascii**.
3. Everything else about an interface moving → **life** (the default, and the one that owns transitions —
   there is deliberately no separate `transition` skill).
4. Not motion at all → leave the domain (below); do not force a sub-skill.

Pick **one** sub-skill per target and finish there. Do not split one request across two because the boundary
feels interesting; name the other sub-skill in a line only if the user might genuinely want it next.

## Out of this domain

| The request is really about | Go instead |
|---|---|
| a layout, spacing, hierarchy or contrast problem with nothing moving | UI-quality skills (e.g. `accessible`, `anti-slop`) |
| which states a component should have and seeing them side by side | `components` |
| an implementation matching a mockup or a reference recording | `parity`, `visual-parity-testing` |
| producing an actual video, GIF, or demo reel | `create-video` |
| 3D scenes, games, WebGL engines beyond UI-level motion | none of these sub-skills |

Interface *sound* is an optional note inside `life`, not a sub-skill — sound design has no home here.

## The contract of this level

- **The router states no rules.** Motion tokens, easing/easing-curve discipline, `prefers-reduced-motion`,
  performance and accessibility, the craft bar, the clarify-before-coding duty, fill-rule preservation — each
  of those lives with its owner: `life/references/timing-and-tokens.md`,
  `life/references/performance-and-accessibility.md`, `life/references/review-standards.md`,
  `ascii/SKILL.md` (mandatory intent clarification), `svg/SKILL.md` (per-style foundations).
- **A rule that must hold across sub-skills is written into each owner, not up here.** Duplicating it in the
  router creates a second place for the same rule to go stale.
- **Coverage claims belong to sub-skills.** This level asserts none: being the parent of three tested
  sub-skills does not make the parent "tested", and each sub-skill's own verification section is the honest
  source for where it has actually been exercised.
- **If this file starts explaining how to animate, it is wrong** — move that text into the sub-skill that owns
  it and leave a router row pointing at it.

## Layout

```text
animation/            <- this router only
├── SKILL.md
├── life/             <- UI motion: micro · component · transition (+ references, scripts, assets, examples)
├── ascii/            <- character/terminal motion (+ references, scripts)
└── svg/              <- 25 SVG/logo animation styles (+ references, scripts, examples)
```

Nested sub-skills are not separate slash commands: the CLI surfaces `animation`, and routing is what loads
`<sub-skill>/SKILL.md`.
