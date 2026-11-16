---
name: animation
version: 2.0.1
author: Amr
specialized: none
description: 'Animation battery — a router over three internal methods. Routes any motion request to the method that holds the functionality: `life` (UI motion — micro/component/transition: hover and press feedback, entrances and exits, view/page/route transitions, stagger and sequence choreography, scroll, gestures and springs, onboarding intros, discovery, review, debugging, matching a recording), `ascii` (character/terminal motion — ASCII intro or loader, image/video to ASCII, plasma and wave fields, per-glyph cascades, Three.js AsciiEffect), `svg` (25 named SVG/logo animation styles — chrome-liquid, draw-fill, elastic-entrance, neon, unroll and 20 more, with light/dark variants). Use when the user asks for animation, motion, transitions, a page or route to move, an animated logo, a retro/ASCII effect, or wants an interface to "feel alive", even if no one says the word animate. Adds no rules of its own; the performing method owns those. Out of domain: static visual quality, state galleries, mockup fidelity, real video.'
when_to_use: Any motion or animation request — UI transitions, micro-interactions, animated logos/SVGs, ASCII or terminal motion — where the work must first be assigned to the right internal method. Also /animation.
argument-hint: "[life|ascii|svg] <command or style> <target>"
---

# Animation

The `animation` Battery-Skill: one address for the motion domain, three internal methods underneath it.
**This file contains no functionality.** It decides which method to read and nothing else — no workflow,
no standards, no references, no scripts. Everything that constrains the work lives in the method that
performs it. The methods are parts of this battery, not separately installable skills: `/animation` is
the only entry point, and the whole `animation/` tree installs as one unit.

## Methods

| What the request actually is | Read | Entry form |
|---|---|---|
| Interface motion: one element (hover, press, state swap, number roll), a whole component as one visual unit, view/page/route transitions forward **and** back, entrances and exits, coordinating several elements moving together (stagger, sequence, choreography), first-run and onboarding intros, scroll-linked motion, gestures and springs, finding what should (or must not) animate, prototyping options before building, reviewing or debugging existing animation, matching a recorded animation | [`life/method.md`](life/method.md) | `/animation life micro\|component\|transition <target>` |
| Motion made of characters: terminal intro or loader, image/video → ASCII, generative plasma/wave/noise fields, per-glyph cascade or domino, Three.js `AsciiEffect`, glyph-level coloring and masking | [`ascii/method.md`](ascii/method.md) | `/animation ascii <kind>` |
| A static SVG logo/icon animated with one of 25 named treatments (`liquid`, `draw`, `load`, `elastic`, `rise`, `iris`, `neon`, `pulse`, `flip`, `comet`, `focus`, `crt`, `chroma`, `mosaic`, `ripple`, `spark`, `engrave`, `grain`, `tide`, `polarity`, `blinds`, `assemble`, `lantern`, `pinwheel`, `unroll`), including light/dark variants of an existing file | [`svg/method.md`](svg/method.md) | `/animation svg <style> <file.svg>` |

## When more than one row fits, in this order

1. A `.svg` target or one of the 25 named SVG effects → **svg**.
2. Glyphs, a terminal, or character-art output → **ascii**.
3. Everything else about an interface moving → **life** (the default, and the one that owns transitions —
   there is deliberately no separate transition method).
4. Not motion at all → leave the domain (below); do not force a method.

Pick **one** method per target and finish there. Do not split one request across two because the boundary
feels interesting; name the other method in a line only if the user might genuinely want it next.

## Out of this domain

| The request is really about | Go instead |
|---|---|
| a layout, spacing, hierarchy or contrast problem with nothing moving | UI-quality skills (e.g. `denoise`, `anti-slop`) |
| which states a component should have and seeing them side by side | `design` prototype mode (stories/components catalog) |
| an implementation matching a mockup or a reference recording | `parity` |
| producing an actual video, GIF, or demo reel | none of these methods |
| 3D scenes, games, WebGL engines beyond UI-level motion | none of these methods |

Interface *sound* is an optional note inside `life`, not a method — sound design has no home here.

## The contract of this level

- **The router states no rules.** Motion tokens, easing/easing-curve discipline, `prefers-reduced-motion`,
  performance and accessibility, the craft bar, the clarify-before-coding duty, fill-rule preservation — each
  of those lives with its owner: `life/references/timing-and-tokens.md`,
  `life/references/performance-and-accessibility.md`, `life/references/review-standards.md`,
  `ascii/method.md` (mandatory intent clarification), `svg/method.md` (per-style foundations).
- **A rule that must hold across methods is written into each owner, not up here.** Duplicating it in the
  router creates a second place for the same rule to go stale.
- **Coverage claims belong to methods.** This level asserts none: routing to three tested methods does not
  make the router "tested", and each method's own verification section is the honest source for where it
  has actually been exercised.
- **If this file starts explaining how to animate, it is wrong** — move that text into the method that owns
  it and leave a router row pointing at it.
- **Scripts:** `life`'s optional scripts need Python 3.9+ (standard library only; the match-existing set
  additionally needs ffmpeg, opencv-python, numpy, scipy). `ascii`'s bundled scripts are MIT-licensed.

## Layout

```text
animation/            <- this router only
├── SKILL.md
├── life/             <- UI motion: micro · component · transition (method.md + references, scripts, assets, examples)
├── ascii/            <- character/terminal motion (method.md + references, scripts)
└── svg/              <- 25 SVG/logo animation styles (method.md + references, scripts, examples)
```

The methods have no `SKILL.md` on purpose: a nested entrypoint would make each one a separately
inventoried, separately versioned, separately installable skill. The battery's single row in the catalog,
single `version`, and single junction are what keep the motion domain one address.
