---
name: ascii
description: Build ASCII and character-based animations for web, terminal, or CLI. Use when the user asks for an ASCII animation, terminal intro or loader, image or video to ASCII, retro or hacker text motion, generative plasma or wave fields, character-art shaders, Three.js AsciiEffect, per-character cascade or domino effects, gradient or masked coloring on glyphs, or interactive ASCII. Always clarify the desired kind of animation with the user before coding. Supports Bun.Image as the preferred image pipeline when Bun is available.
license: MIT
metadata:
  version: "1.1.0"
---

# ASCII Animation

**Sub-skill of the [`animation`](../SKILL.md) meta-skill** — reached as `/animation ascii <kind>`. Character-based motion lives here; UI-state motion lives in [`../life/SKILL.md`](../life/SKILL.md).

Render motion entirely with text characters. Output is lightweight, distinctive, and works in browsers (`pre`/canvas), terminals (ANSI), and over 3D scenes (Three.js `AsciiEffect`).

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

Also confirm target (web standalone HTML, Node/Bun terminal, or both), color needs (mono vs gradient vs truecolor), and any source image/video.

Only after the user picks (or clearly states) a kind, proceed to implementation.

## Core concept — the brightness ramp

Map luminance `0..1` to a character whose visual density matches:

```js
const ch = ramp[Math.round(lum * (ramp.length - 1))];
```

Common ramps (dark → light):

- Compact 10: ` .:-=+*#%@`
- Block shades: ` ░▒▓█`
- 70-level Paul Bourke (photo fidelity) — see [references/rendering.md](references/rendering.md)

Perceptual luminance:

```js
const lum = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255;
```

Invert for dark text on light background: `lum = 1 - lum`.

## Character cell aspect (the #1 gotcha)

Monospace cells are roughly **twice as tall as wide** (`fontAspect ≈ 0.5`). Sampling a square pixel grid stretches the image vertically. Correct it:

```js
const rows = Math.round(cols * (imgH / imgW) * 0.5);
```

Measure the real ratio once with canvas `measureText` when precision matters. Full tables and helpers → [references/rendering.md](references/rendering.md).

## Image pipeline — Bun.Image preferred, sharp fallback

When converting images on the server or CLI:

1. **Bun ≥ 1.3.14** — use built-in `Bun.Image` (zero native deps, drop-in style for resize/metadata). Preferred.
2. **Node or older Bun** — use `sharp`.

The packaged script `scripts/img-to-ascii.mjs` auto-detects the runtime and chooses the pipeline. Manual pattern:

```js
// Bun path (preferred when available)
const meta = await Bun.file(path).image().metadata();
const rows = Math.round(cols * (meta.height / meta.width) * 0.5);
// Resize then obtain pixels — see script for the concrete dual path

// sharp path
import sharp from 'sharp';
const { data, info } = await sharp(path).resize(cols, rows).removeAlpha().raw().toBuffer({ resolveWithObject: true });
```

Do not force sharp on a modern Bun install.

## Web rendering choices

| Need | Approach |
|------|----------|
| Simple generative / mono | `pre` + `textContent` (≤ ~120×60 @ 30 fps) |
| Per-char color, large grid, 60 fps | Canvas `fillText` per cell |
| 3D scene | Three.js `AsciiEffect` — call `effect.render`, append `effect.domElement` |
| Selectable text | Prefer `pre` |

Always set `line-height: 1; letter-spacing: 0; font-family: monospace; white-space: pre`.

## Motion patterns (optional enhancements)

Use only when the user’s chosen kind benefits from them. Do not force.

### 1. Whole-shape wave / domino cascade

Reveal or pulse a fixed silhouette in spatial order (left→right, top→bottom, radial, random):

```js
// delay based on position → staggered appearance
const delay = (x / cols + y / rows) * totalMs;          // diagonal wave
// or: const delay = Math.hypot(x - cx, y - cy) * speed; // radial
const visible = t >= delay;
const localT = Math.max(0, t - delay);
```

Domino-style: each cell stays “fallen” after its delay; wave-style: a traveling band of high luminance.

### 2. Per-character animation inside a fixed shape

Keep the silhouette (mask from image or hand-authored grid). Animate only the glyph or its brightness:

```js
const base = mask[y][x];           // ' ' or solid
if (base === ' ') { out += ' '; continue; }
const phase = (x + y) * 0.3 + t * 0.004;
const lum = 0.5 + 0.5 * Math.sin(phase);
out += ramp[Math.round(lum * (ramp.length - 1))];
```

### 3. Gradient or source-image color

On canvas (or ANSI truecolor), sample color from the source pixel or a procedural gradient and set `fillStyle` / `\x1b[38;2;R;G;Bm` per character. Luminance still picks the glyph; color is independent.

### 4. Mask coloring from a second image

Use one image (or shape) as the ASCII mask / density field and a second image as the color source. Sample both at the same grid coordinate.

### 5. Interactive

Drive a uniform or a local falloff with pointer position, scroll, or keys. Keep the frame function pure in `t` + input state so `?t=N` still freezes a deterministic frame.

## Terminal / CLI loop

```js
const ESC = '\x1b[';
process.stdout.write(ESC + '?25l');           // hide cursor
const id = setInterval(() => {
  process.stdout.write(ESC + 'H');            // home — cheaper than full clear
  process.stdout.write(renderFrame(Date.now()));
}, 1000 / 20);
process.on('SIGINT', () => {
  clearInterval(id);
  process.stdout.write(ESC + '0m' + ESC + '?25h' + ESC + '2J' + ESC + 'H');
  process.exit(0);
});
```

Truecolor: `\x1b[38;2;${r};${g};${b}m${ch}\x1b[0m`. Prefer 12–24 fps for a retro feel.

Full ANSI helpers and plasma example → [references/rendering.md](references/rendering.md).

## Deliverable contract (web)

One self-contained `.html` file that opens directly in a browser — no build step.

- Inline the ramp, grid, and `requestAnimationFrame` loop.
- Drive time from an injectable value (not bare `Date.now()`), and seed any RNG, so frames are reproducible.
- Support the seek harness: `?t=N` renders exactly one frame at simulated time `N` and stops.
- Honor `prefers-reduced-motion` (static frame or slowed loop).
- Correct cell aspect; no vertical stretch.

Verify by screenshotting `?t=0`, `?t=1000`, `?t=2000` (Playwright or any headless tool). Check ramp order, motion evolution, and absence of stretch/invert bugs.

## Quick reference

| Need | Approach |
|------|----------|
| Clarify first | Ask kind + target before coding |
| Generative field | `pre` + sine/noise → ramp |
| Photo fidelity | 70-level Bourke ramp, sRGB luminance |
| Per-char color / 60 fps | Canvas `fillText` |
| Cascade / domino | Spatial delay per cell |
| Per-glyph pulse | Mask + independent phase |
| Gradient / mask color | Luminance → glyph, second sample → color |
| Video | `video` → offscreen canvas → `getImageData` |
| 3D | `AsciiEffect.render(scene, camera)` |
| Terminal | ANSI home + 12–24 fps, hide cursor |
| Image CLI | `scripts/img-to-ascii.mjs` (Bun.Image or sharp) |
| Aspect fix | `rows = cols * imgAspect * 0.5` |

## References & scripts

- [references/rendering.md](references/rendering.md) — ramp tables, sampling math, `pre` vs canvas, ANSI truecolor loop, complete `AsciiEffect` wiring, motion-pattern sketches
- [scripts/img-to-ascii.mjs](scripts/img-to-ascii.mjs) — CLI image → ASCII; auto-selects Bun.Image or sharp
