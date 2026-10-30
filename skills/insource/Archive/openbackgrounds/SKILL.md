---
name: openbackgrounds
description: Reconstruction kit for 50 animated backgrounds - aurora ribbons, galaxy spiral, particle waves, flow fields, raymarched crystals, metaballs, fluid ripples, wire globes, radar sweeps, film grain. Use when asked to build, recreate, port, match, or choose an animated background for a hero section, landing page, app shell, or preview gallery. Contains descriptive per-scene references, technique-family guides, exact parameters, palettes, a host lifecycle contract, and a Playwright visual verifier. Text and posters only - no source code.
version: 1.0.0
---

# OpenBackgrounds

## What this is

A reconstruction kit for 50 animated backgrounds, one Markdown reference and one
rendered poster each. Every reference describes the look, motion, math, exact
parameters, palette, renderer state, and failure modes well enough to rebuild
the scene from text in any framework, then check it against the poster.

The scenes were authored as Vue 3 SFCs on Nuxt 4 and target the browser directly:
16 Canvas-2D, 27 raw WebGL1, 7 three.js. The descriptions are framework-neutral.

## What this is not

- **Not source code.** There is no GLSL, JS, TS, or Vue in this skill, and no
  fenced code blocks. Formulas are prose and notation only.
- **Not a runtime library.** Nothing is installed or imported; the skill teaches
  reconstruction.
- **Not a license grant.** Author credits are in `references/manifest.json`;
  several scenes are ports of CodePen originals.
- Posters are single-frame targets, not pixel-exact truth. Animation phase
  differs between runs.
- The originals have **no audio reactivity**, no SSR path, and no
  `prefers-reduced-motion` handling. If the target needs those, add them; do not
  expect them in a reference.

## Workflow

1. Resolve the scene id. If the user named one, use it. Otherwise filter
   `references/manifest.json` by keyword or read `references/index.md`.
2. Look at `assets/posters/<id>.jpg`. This is the target.
3. Read the family doc listed in the scene's frontmatter: it carries the shared
   scaffold, math conventions, and helper semantics.
4. Read `references/scenes/<id>.md`.
5. Implement against `references/host-contract.md`.
6. Run `scripts/verify.mjs` against the running page and compare with the poster.
7. Fix using section 12 (failure modes) and section 13 (tuning knobs) of the
   scene doc, in that order.

## Routing

| family | technique | count | effort | reference |
| --- | --- | --- | --- | --- |
| `canvas-a1` | noise-advected particles | 4 | S–L | `references/families/canvas-a1-noise-particles.md` |
| `canvas-a2` | pre-rendered sprite blitting | 4 | M | `references/families/canvas-a2-sprite-blit.md` |
| `canvas-a3` | analytic wave and geometry fields | 4 | S–M | `references/families/canvas-a3-analytic-fields.md` |
| `canvas-a5` | accumulating ink and persistence | 2 | M–L | `references/families/canvas-a5-accumulating-ink.md` |
| `canvas-a4` | sampled heightfield and isolines | 1 | XL | `references/families/canvas-a4-heightfield.md` |
| `canvas-a6` | film emulation | 1 | M | `references/families/canvas-a6-film.md` |
| `webgl-f1` | closed-form fullscreen fragment fields | 11 | S–L | `references/families/webgl-f1-fragment-fields.md` |
| `webgl-f3` | vertex-projected particle clouds | 6 | L–XL | `references/families/webgl-f3-particle-clouds.md` |
| `webgl-f4` | line, ribbon, and strut geometry | 5 | L–XL | `references/families/webgl-f4-line-geometry.md` |
| `webgl-f5` | vertex-displaced solid and instanced mesh | 5 | L–XL | `references/families/webgl-f5-displaced-mesh.md` |
| `webgl-f2` | raymarched SDF and volumetric | 5 | L–XL | `references/families/webgl-f2-raymarch.md` |
| `webgl-f6` | escape-time fractal | 1 | M | `references/families/webgl-f6-fractal.md` |
| `webgl-f7` | CPU simulation to texture | 1 | XL | `references/families/webgl-f7-cpu-texture.md` |

Marquee scenes for orientation: `aurora-waves`, `galaxy-spiral`, `flow-field`,
`particle-waves`, `crystalline-depths`, `fluid-ripples`, `wire-globe`,
`neural-noise`, `event-horizon`, `cosmic-anomaly`.

Full 50-row table: `references/index.md`. Machine-readable metadata (exact
line counts, DPR clamps, dependencies, effort tier, keywords):
`references/manifest.json`.

## Host contract

A scene fills a positioned, full-bleed container, clamps DPR (1.5 for 37 of 50;
the rest are 1.6–2, except AuroraWaves, which does not clamp),
primes hidden state, runs one RAF loop that ticks the FPS meter once per frame,
and destroys everything on unmount. Exactly one scene may be mounted at a time.
The preview host paints `#000000 → #1A0033` behind the canvas, so
transparent-canvas scenes depend on that backdrop.

Read `references/host-contract.md` before mounting. Documented deviations:
CosmicAnomaly (pointer events, remote HDR, bloom), MetaballOrbit (CSS backdrop),
FluidRipples (CPU float texture), AuroraWaves (no DPR clamp, class teardown),
SpectrumCascade (`alpha: true`), DNAHelix and ParticleWaves (`ResizeObserver`).

## Faithfulness rules

- Exact constants beat "looks close". Values in the parameter tables are the
  originals; never round them.
- Time is seconds, space is CSS pixels, angles are radians, speeds are px/s at
  60 fps. If you render at a different frame cadence, convert by dt, not by
  assuming 60 fps.
- Match the render state in section 3 (blend, depth, cull, clear, canvas alpha)
  before tuning anything visual.
- Keep the palette's hue band even when you change saturation or brightness.
- Reproduce the warmup count. Trail and simulation scenes open empty without it.
- Preserve the original's randomness policy: a seeded RNG is only required when
  the scene doc says the poster is seed-exact.

## Verification

`scripts/verify.mjs` needs Playwright and a reachable page that renders a
canvas. It counts animation frames, rejects blank/frozen/error states, and
reports a coarse similarity to the poster (advisory: animation phase differs).

Single page: `node scripts/verify.mjs --url http://localhost:5173/ --selector canvas`.
Whole manifest: `node scripts/verify.mjs --manifest references/manifest.json --url-template "http://localhost:3000/preview/{id}" --out report.json`.

Verdicts: `OK`, `THIN` (alive but nearly flat), `BLANK`, `FROZEN`, `ERROR`.
Poster similarity is reported separately as `poster_diff` (0 = close).

`scripts/lint.mjs` validates this skill, not your implementation; run it only
after editing references.

## Effort tiers

- **S** — one renderer pass, no persistent state. Under a day.
- **M** — one renderer, a handful of stateful elements (particles, layers).
- **L** — multi-layer or geometry pipeline, CPU-side buffers, several programs.
- **XL** — raymarching, volumetric integration, or a CPU simulation with
  per-frame uploads.

## Reading discipline

- Read at most two scene references per request; a family doc plus one scene is
  usually enough.
- Search instead of enumerating: `rg -l "magenta|violet" references/scenes/`,
  or filter `manifest.json` by `keywords`.
- Load one poster at a time.
