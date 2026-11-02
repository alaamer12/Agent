---
name: svg
description: "Animate a static, flat SVG logo or icon (solid-fill <path> elements) with one of twenty-five animation styles: chrome-liquid, draw-fill, loading-loop, elastic-entrance, rise, iris, neon, pulse, flip, comet, focus (rack-focus, blur resolves), crt (TV power-on + scanlines), chroma (RGB ghosts converge), mosaic (tiled mask dissolve), ripple (turbulence warps geometry), spark (a travelling spark reveals), engrave (emboss under raking light), grain (noise-threshold dissolve), tide (wavy waterline rises), polarity (inverting band sweeps), blinds (slats open), assemble (fragments fly in and lock), lantern (a wandering light reveals), pinwheel (wedges scale open), unroll (falls from a top hinge). Per-style signatures are in the SKILL.md table. Trigger when the user asks to animate a logo/SVG, names any of these effects, wants an existing treatment replicated on a new file, or needs light/dark theme variants. Always preserves fill-rule=evenodd so letterform holes (Arabic ص/ه, Latin a/o/e) never fill in solid."
argument-hint: "<style> <file.svg>  (style: liquid|draw|load|elastic|rise|iris|neon|pulse|flip|comet|focus|crt|chroma|mosaic|ripple|spark|engrave|grain|tide|polarity|blinds|assemble|lantern|pinwheel|unroll)"
---

# SVG Logo Animation

**Sub-skill of the [`animation`](../SKILL.md) meta-skill** — reached as `/animation svg <style> <file.svg>`.
This is the 25-style SVG/logo treatment path; general UI motion (micro, component, transition) is
[`../life/SKILL.md`](../life/SKILL.md).

Turns a static SVG (flat `<path>` elements with solid fills) into an animated version using one of
**twenty-five animation styles**. This file is the router: it identifies styles and nothing else. Shared
build rules, scaling, validation and delivery live in
[`references/foundations.md`](references/foundations.md); each style's template and geometry live in its
own recipe — **the recipe is the sole home of its numbers.**

## Read order

| The job is | Read |
|---|---|
| animate a target with a named style | [`references/foundations.md`](references/foundations.md) (once, fully) + `references/<style>.md` only |
| replicate an existing animated file onto a new one | foundations + the recipe matching that file's style; copy structure and ordering, re-derive every number for the new SVG's size — never literal seconds or pixels |
| color-only light/dark variant of an already-animated logo | foundations §8 alone — no recipe re-read |
| an effect outside the 25, or a new mechanic | [`references/rejected-mechanics.md`](references/rejected-mechanics.md) first — four measured failures are already recorded there |

No command or an unknown command: ask ONE question offering the twenty-five; if asking is impossible,
default to `liquid`.

## The 25 styles

| Style (command) | Signature — what it looks like | Trigger words · aliases | Duration |
|---|---|---|---|
| [`chrome-liquid`](references/chrome-liquid.md) (`liquid`) | Chrome outline draws itself → true colors rise like liquid bottom-to-top → diagonal sheen sweeps | liquid fill, liquid metal, chrome reveal · `chrome` | ~8s, then sheen loops |
| [`draw-fill`](references/draw-fill.md) (`draw`) | Each outline draws itself, then its fill fades in | draw itself, self-drawing, draw on, line by line, sign itself, one-shot intro | ~3.5s one-shot |
| [`loading-loop`](references/loading-loop.md) (`load`) | Outlines draw and reverse endlessly, never filling | loading, progress, loop forever, draws over and over · `loading` | infinite |
| [`elastic-entrance`](references/elastic-entrance.md) (`elastic`) | Logo elastically scales/rotates in, wobbles, glows, fades out | playful, bounce in, elastic, pop in, wobble, animated intro loop | ~8s loop |
| [`rise`](references/rise.md) (`rise`) | Shapes rise from below and fade in, one after another | rise up, staggered, fade in one by one, cascade | ~2.5s one-shot |
| [`iris`](references/iris.md) (`iris`) | Circular clip grows from the center, revealing like a camera iris | iris, circle reveal, cinematic reveal, spotlight (round) | ~1.5s one-shot |
| [`neon`](references/neon.md) (`neon`) | Dark stage, outlines flicker on like a neon sign, then fill glows steady | neon, glow sign, flicker on, dark stage | ~2s, holds |
| [`pulse`](references/pulse.md) (`pulse`) | Logo breathes — calm scale + glow inhale/exhale | breathing, ambient, idle, calm loop | infinite |
| [`flip`](references/flip.md) (`flip`) | Logo flips in like a card around its vertical axis | flip, card flip, 3D reveal | ~0.9s one-shot |
| [`comet`](references/comet.md) (`comet`) | Bright dash traces each outline endlessly like a comet; fills stay lit dimly | comet, energy line, trace, light traces the outline | infinite |
| [`focus`](references/focus.md) (`focus`) | Camera rack-focus — the artwork itself is soft and sharpens, with one deliberate re-blur | rack focus, defocus, blur resolves, soft to sharp, camera focus · `rack-focus`, `defocus` | ~1.4s one-shot |
| [`crt`](references/crt.md) (`crt`) | Hot line on the centreline, logo opens vertically out of it through scanlines that then fade | tv power on, crt, scanlines, band opens from the middle, retro screen · `tv`, `power-on`, `scanline` | ~1.2s one-shot |
| [`chroma`](references/chroma.md) (`chroma`) | Artwork splits into RGB channel ghosts, slides apart, converges back to the exact brand color | chromatic aberration, rgb split, channel separation, anaglyph · `rgb-split`, `chromatic-aberration` | ~1.8s one-shot, dark stage |
| [`mosaic`](references/mosaic.md) (`mosaic`) | Grid of mask tiles each opening on its own jittered beat, so a wave crosses the logo | mosaic, tiles, dissolve in, pixelated reveal, wave of squares · `dissolve`, `tiles` | ~1.4s one-shot |
| [`ripple`](references/ripple.md) (`ripple`) | Fractal noise displaces the actual geometry and the warp relaxes to crisp | ripple, water, liquid warp, refraction, heat haze · `water`, `liquid-warp` | ~1.6s one-shot |
| [`spark`](references/spark.md) (`spark`) | A bright spark travels the logo and the artwork stays lit in its wake | spark, weld, torch, travelling light draws it in · `weld`, `torch` | ~1.6s one-shot |
| [`engrave`](references/engrave.md) (`engrave`) | Blind embossed relief under a raking light that sweeps around, then real colors land | emboss, deboss, engraved, letterpress, blind seal, raking light · `emboss`, `deboss`, `letterpress` | ~1.8s one-shot |
| [`grain`](references/grain.md) (`grain`) | Resolves out of film grain as a noise threshold is raised until nothing is masked | film grain, noise dissolve, static resolves, analog reveal · `noise`, `film-grain`, `static` | ~1.5s one-shot |
| [`tide`](references/tide.md) (`tide`) | A wavy waterline rises and flattens, filling the logo from below | water fills up, wavy line rises, tide, liquid with a meniscus · `fill-up`, `wave-fill` | ~1.6s one-shot |
| [`polarity`](references/polarity.md) (`polarity`) | A band sweeps across and inverts whatever it touches | invert, negative, x-ray, polarity flip, band of inversion · `invert`, `negative`, `xray` | ~1.3s one-shot |
| [`blinds`](references/blinds.md) (`blinds`) | Horizontal slats open one after another, each growing its own height | blinds, shutters, louver, slats open · `louver`, `shutters` | ~0.9s one-shot |
| [`assemble`](references/assemble.md) (`assemble`) | Rectangular fragments fly in from scattered offsets and lock into the whole logo | shatter, pieces fly in, assemble, explode-in · `shatter`, `explode-in`, `pieces` | ~1.6s one-shot |
| [`lantern`](references/lantern.md) (`lantern`) | A soft round light wanders across and blooms, revealing the logo in its path | lantern, spotlight sweep, soft light wanders across · `sweep`, `spotlight` | ~1.5s one-shot |
| [`pinwheel`](references/pinwheel.md) (`pinwheel`) | Wedges each scale up from the center on their own beat, sweeping like a turbine | pinwheel, turbine, wedges open, segmented iris · `iris-blades`, `turbine` | ~1.4s one-shot |
| [`unroll`](references/unroll.md) (`unroll`) | The logo falls into place around a fixed top hinge, like paper unrolling | unroll, paper falls into place, hinged at the top · `paper`, `fall-in` | ~1.1s one-shot |

`/animation svg <command> <file.svg>` must reproduce the matching recipe's treatment (structure and
ordering; numbers re-derived per the foundations scaling table). The four `liquid` / `draw` / `load` /
`elastic` treatments were originally tuned against an external `variations/` reference set that is **not
in this repository** — the recipes in `references/` are the authoritative description, and the fifteen
`examples/*.svg` files (one per newer style) are committed.

## Layout

```text
svg/
├── SKILL.md                          this router — style identification only
├── references/
│   ├── foundations.md                shared build rules: extraction, scaling, hard rules, validation, variants, delivery
│   ├── rejected-mechanics.md         four measured failures — read before inventing a 26th mechanic
│   └── <style>.md × 25               one recipe per style: template + geometry + unique notes
├── scripts/                          extract_paths.py, validate.py (run, never read)
└── examples/*.svg                    worked outputs, one per newer style
```
