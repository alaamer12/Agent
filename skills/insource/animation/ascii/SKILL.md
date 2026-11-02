---
name: ascii
description: Build ASCII and character-based animations for web, terminal, or CLI. Use when the user asks for an ASCII animation, terminal intro or loader, image or video to ASCII, retro or hacker text motion, generative plasma or wave fields, character-art shaders, Three.js AsciiEffect, per-character cascade or domino effects, gradient or masked coloring on glyphs, or interactive ASCII. Always clarify the desired kind of animation with the user before coding. Supports Bun.Image as the preferred image pipeline when Bun is available.
license: MIT
metadata:
  version: "1.1.0"
---

# ASCII Animation

**Sub-skill of the [`animation`](../SKILL.md) meta-skill** — reached as `/animation ascii <kind>`. Character-based motion lives here; UI-state motion lives in [`../life/SKILL.md`](../life/SKILL.md).

Render motion entirely with text characters. Output is lightweight, distinctive, and works in browsers (`pre`/canvas), terminals (ANSI), and over 3D scenes (Three.js `AsciiEffect`). This file is the router: it holds the clarification duty and the facts every job needs. Everything deeper — ramp tables, sampling helpers, renderer comparisons, ANSI loops, `AsciiEffect` wiring, motion-pattern code — has one home: [references/rendering.md](references/rendering.md).

## Mandatory first step — clarify intent

Before writing any code, ask the user what kind of ASCII animation they want. Use a short clarifying question (or the `ask_user_question` tool when available). Offer concrete choices; do not assume.

Typical kinds (not exhaustive):

| Kind | What it looks like |
|------|--------------------|
| Generative field | Plasma, sine waves, noise, tunnels, rain — pure math → ramp |
| Image → ASCII | Static photo or logo converted once |
| Video / webcam → ASCII | Live or file frames mapped every tick |
| Shape / logo cascade | Fixed silhouette; characters light up in wave, domino, or typewriter order |
| Per-character motion | Each glyph in a fixed shape animates independently (pulse, cycle ramp, flicker) |
| 3D scene → ASCII | Three.js `AsciiEffect` over a mesh |
| Terminal loader / intro | CLI banner, spinner, or short loop with ANSI |
| Interactive | Mouse/keyboard drives luminance, color, or reveal |

Also confirm target (web standalone HTML, Node/Bun terminal, or both), color needs (mono vs gradient vs truecolor), and any source image/video. Only after the user picks (or clearly states) a kind, proceed to implementation.

## The three facts every job needs

**Brightness ramp.** Map luminance `0..1` to a character whose visual density matches:

```js
const ch = ramp[Math.round(lum * (ramp.length - 1))];
```

Compact 10-level (dark → light): `` ` .:-=+*#%@` `` · block shades (near-continuous fades, meters): `` ` ░▒▓█` ``. The 70-level Bourke ramp, 16-level extended, ordering caveats and when each fits → [rendering.md](references/rendering.md).

**Perceptual luminance**, with inversion for dark-on-light:

```js
const lum = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255;   // lum = 1 - lum to invert
```

**Character cell aspect — the #1 gotcha.** Monospace cells are roughly **twice as tall as wide** (`fontAspect ≈ 0.5`); sampling a square pixel grid stretches the image vertically. Correct it:

```js
const rows = Math.round(cols * (imgH / imgW) * 0.5);
```

Measure the real ratio once with canvas `measureText` when precision matters (helper in rendering.md).

## Renderer decision

| Need | Approach |
|------|----------|
| Simple generative / mono, selectable text | `pre` + `textContent` (≤ ~120×60 @ 30 fps) |
| Per-char color, large grid, 60 fps | Canvas `fillText` per cell |
| 3D scene | Three.js `AsciiEffect` |
| Terminal loader / intro | ANSI home + 12–24 fps, hide cursor |

Required CSS (`line-height: 1`, `letter-spacing: 0`, `white-space: pre`), the full comparison table and code, the frame loop with cleanup, truecolor escapes and complete `AsciiEffect` wiring → [references/rendering.md](references/rendering.md).

## Image pipeline

1. **Bun ≥ 1.3.14** — built-in `Bun.Image` (zero native deps) for resize/encode/metadata. Preferred.
2. **Raw RGB pixels** for luminance sampling still require `sharp` (or a canvas/`getImageData` path in the browser) even under Bun.

The packaged `scripts/img-to-ascii.mjs` auto-detects the runtime and picks the pipeline. Dual-path code → [references/rendering.md](references/rendering.md).

## Motion patterns

Wave/domino cascade, per-glyph pulse, gradient or source-image color, second-image mask coloring, interactive falloff — use only when the chosen kind benefits. Complete, tested implementations are in [references/rendering.md §motion-pattern sketches](references/rendering.md). Keep every frame function pure in `(t, inputState)` so `?t=N` stays deterministic.

## Deliverable contract (web)

One self-contained `.html` file that opens directly in a browser — no build step.

- Inline the ramp, grid, and `requestAnimationFrame` loop.
- Drive time from an injectable value (not bare `Date.now()`), and seed any RNG, so frames are reproducible.
- Support the seek harness: `?t=N` renders exactly one frame at simulated time `N` and stops.
- Honor `prefers-reduced-motion` (static frame or slowed loop).
- Correct cell aspect; no vertical stretch.

Verify by screenshotting `?t=0`, `?t=1000`, `?t=2000` (Playwright or any headless tool). Check ramp order, motion evolution, and absence of stretch/invert bugs.

## References & scripts

- [references/rendering.md](references/rendering.md) — ramp tables, luminance variants, sampling + cell-aspect helpers, `pre` vs canvas, ANSI loop + truecolor, `AsciiEffect` wiring, motion-pattern sketches, image-pipeline dual path
- [scripts/img-to-ascii.mjs](scripts/img-to-ascii.mjs) — CLI image → ASCII; auto-selects Bun.Image or sharp
