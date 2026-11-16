---
id: silk-strands
name: Silk Strands
family: webgl-f4
renderer: webgl1
poster: assets/posters/silk-strands.jpg
complexity: XL
source_lines: 435
dpr_max: 1.5
deps: [simplex-noise]
poster_capture: 640x400
---

# Silk Strands — scene reference

## 1. Identity

Five stacked sheets of 26 hair-thin filaments, lit blue-to-magenta with a cyan sheen, undulating like wind-blown silk across a nearly black violet field.

## 2. Perceived look

A landscape of fine, luminous thread rather than a solid surface: each strand is a 1 px polyline whose brightness is low (0.4 alpha at the crests) so the sheets read as translucent gauze layered in depth. Where many strands cross near a crest the overlap saturates into bright ribbons of near-white blue; the troughs are dark and airy, so the field looks woven rather than filled. Colour drifts continuously along each strand and across the sheet — indigo-blue on the left, pink-magenta on the right, with a moving cyan sheen highlight that glints along the folds. The strands are pinned at the left edge (they fade out over the first 6% of their length) and tail off at 86%, which frames the motion as a current flowing left-to-right. The field occupies the middle and lower two-thirds of the frame; the top of the frame stays black. The 3 s screenshot shows a rippling, hazy band of blue-violet thread with a few brighter crossing ribbons and soft black above and below.

## 3. Frame anatomy

Back to front:

1. **Clear colour** `(0.014, 0.008, 0.024)` at alpha 1 — near-black with a violet cast; canvas opaque, so the parent backdrop is not visible.
2. **Far sheets** — the rear two of five sheets, faded by `(1−smoothstep(2.4,6.0,w))^1.2` to well under half alpha; they read as dim, blurred texture.
3. **Middle sheet** — at `w ≈ 3.6`, full fade, where most of the visible weaving happens.
4. **Near sheets** — the front two, brighter and coarser; their crests are the crispest lines in the image.
5. **Sheen glints** — part of the same single draw call; a `pow(…,5)` cyan term that varies along `u` and `v`, so bright bands crawl across the sheets.

One `gl.LINES` draw call. No depth buffer, no depth writes, additive `SRC_ALPHA, ONE`, MSAA on. Because depth is ignored, sheets composite strictly back-to-front by vertex order (sheets built in order, so the last-drawn near sheet lands on top) — but with additive blending the order is visually a wash.

## 4. Motion law

- **Travel.** `travel = 1.9u − 0.16t`; the primary wave (period `2π` in `travel`) has a temporal period of **6.25 s** and moves along `u` at 0.16/1.9 ≈ 0.084 u/s = **0.72 world units/s**, toward +x (downstream).
- **Harmonics.** Four more waves at 4.1, 9.7, 15.3 and 2π frequencies in `travel`, with independent phase and `v` terms; two of them add their own time drift (−0.7t and +1.3t), so the pattern never repeats exactly.
- **Amplitude envelope.** `gain = 0.44·(0.22 + u^1.4)` — amplitude is 0.097 at the pinned end and 0.537 at the tail, so strands look anchored on the left and loose on the right.
- **Sheet lift.** A slow per-strand swell `0.26·sin(2.2u + 0.11t + 0.5·phase)·(0.4 + 0.6v)` — period 57.1 s — so whole sheets heave vertically with a cross-strand gradient.
- **Sway.** `yaw = 0.16·sin(0.049t + 0.2z)` (period 128.2 s), `pitch = 0.07·sin(0.033t + 1.4)` (period 190.4 s), applied as rotX·rotY to the whole field.
- **Iridescence.** `0.5 + 0.5·sin(3.4u + 2.4v + 0.12t + 0.3φ)` — colour bands drift at 0.12 rad/s (period 52.4 s).
- **Sheen.** `pow(0.5 + 0.5·sin(6.2u − 0.23t + 1.1v), 5)` — a narrow highlight sweeping at 0.23 rad/s (period 27.3 s); 6.2 rad across u is just under one full cycle, so there is about **one** sheen band across the field at any instant, not a comb of them.
- **Phase at t = 0.** Waves at `travel·2π` with each strand's `φ = 1.71·sheet`; yaw pitch at their sine values at t = 0. Open-ended, no loop.

## 5. Technique and math

Each strand's resting shape is baked on the CPU with 2D simplex noise; all oscillation, colour and projection happen per vertex.

- **Resting shape.** For sheet `s` (0–4), `blend = s/4`; `baseZ = (blend−0.5)·4·0.72 = ±1.44`; `baseY = (blend−0.5)·4·0.62 = ±1.24`. Sheets therefore step diagonally in Y-Z (≈0.95 units apart).
- **Strand grid.** Per sheet, 26 strands with `v = i/25`; cross-offsets `crossY = (v−0.5)·1.25`, `crossZ = (v−0.5)·0.55`. Along each strand, 48 samples of `u = k/47`: `x = (u−0.5)·8.6` (−4.3…4.3), `y = baseY + crossY + n2(u·1.7 + 3.1s, 0.06i)·0.3`, `z = baseZ + crossZ + n2(u·1.4 + 11 + 2.3s, 0.06i + 5)·0.24`. The 2D simplex's second coordinate is only stepped 0.06 per strand and the first is shared per sheet — that is what keeps neighbours warp-aligned and the field reading as cloth.
- **Upload.** 5 × 26 × 47 segments × 2 vertices = **12,220 vertices** in one static buffer; 7 floats/vertex: xyz + `u`, `v`, an unused per-strand random seed, and `sheetPhase` (1.71s). The shader reads `sheetPhase` as φ, not the seed.
- **Vertex animation.** `gain` as above, then five additive sines displacing y (2π, 15.3, and sheet-lift), z (4.1, 9.7) and x (2π·0.22). No CPU work per frame.
- **Projection.** `w = max(q.z + 3.6, 0.05)`, `gl_Position = (q.xy·focal/w, 0, w)` with `focal = 1.9` — the same double divide as other f4 scenes, so on-screen scale ∝ `1/w²`. Depth fade `(1−smoothstep(2.4, 6.0, w))^1.2`.
- **Colour.** `irid` mixes blue→magenta; sheen term adds `(0.3, 0.86, 1.0)·0.55·sheen^5`.
- **Alpha.** `0.4 · fold · fade · ends`, where `fold = 0.4 + 0.6·sin(πv)` darkens the outermost strands of each sheet (a curvature cue: the sheet's edge turns away), and `ends = smoothstep(0, 0.06, u)·(1 − smoothstep(0.86, 1, u))` pins both ends.

## 6. Parameters

| name | value | range | effect | sensitivity |
|---|---|---|---|---|
| `maxDpr` | 1.5 | 1–2 | DPR cap; 1 px lines vanish above 1.5 on some DPRs | M |
| `seed` | 20260926 | any u32 | strand meander (noise seeded at seed+313) | M |
| `sheets` | 5 | 2–9 | number of stacked gauze layers | H |
| `strandsPerSheet` | 26 | 8–48 | strand density per sheet | H |
| `segments` | 48 | 24–96 | polyline resolution along each strand | M |
| `length` | 8.6 | 5–12 | world length of the field along x | H |
| `sheetGapY` / `sheetGapZ` | 0.62 / 0.72 | 0.3–1.2 | diagonal spacing between sheets | M |
| `spreadY` / `spreadZ` | 1.25 / 0.55 | 0.5–2 | cross-sheet fan width/thickness | M |
| `meander` | 0.3 | 0.05–0.8 | resting noise displacement of strands | M |
| `waveFrequency` | 1.9 | 0.8–4 | spatial frequency of the primary travel wave | H |
| `flowSpeed` | 0.16 | 0.05–0.5 | temporal rate of the travel wave; period 6.25 s at 0.16 | H |
| `amplitude` | 0.44 | 0.1–1.0 | oscillation gain at the tail | H |
| `pinHold` | 0.22 | 0–0.6 | amplitude floor at the pinned end | M |
| `sheetLift` | 0.26 | 0–0.6 | slow per-strand vertical heave | M |
| `yawAmp` / `yawRate` | 0.16 / 0.049 | 0–0.4 / 0.01–0.15 | whole-field sway | M |
| `pitchAmp` / `pitchRate` | 0.07 / 0.033 | 0–0.2 / 0.01–0.1 | whole-field pitch | L |
| `focal` / `distance` / `refAspect` | 1.9 / 3.6 / 1.6 | 1.2–3 / 2.5–6 / 1.2–2 | zoom, camera offset; focal clamps by aspect/refAspect | H |
| `depthNear` / `depthFar` | 2.4 / 6.0 | 1.5–3.5 / 4–8 | fade window | M |
| `alpha` | 0.4 | 0.15–0.7 | per-vertex base alpha (overlap builds brightness) | H |
| `pinFade` / `tailFade` | 0.06 / 0.86 | 0.02–0.2 / 0.7–0.95 | where strands fade in/out along u | M |

## 7. Palette and color

Ground `#040206` (0.014, 0.008, 0.024). Blue `#2966FF` (0.16, 0.40, 1.0); magenta `#F03DE6` (0.94, 0.24, 0.90); sheen `#4DDBFF` (0.30, 0.86, 1.0). `irid` maps hue roughly from 225° (blue) through 270° (violet) to 305° (magenta) across the field; because the mix is linear in RGB, mid-values pass through desaturated periwinkle rather than through saturated purple. The sheen adds a cool white-cyan, raising lightness at the crests without changing hue much. Additive blending over the violet ground makes every overlap brighter and slightly whiter; no tone map, so dense crossings clip. No gamma handling: values are written as authored.

## 8. Composition and camera

A horizontal band with a slight three-quarter tilt. World extent ±4.3 in x, ±2.6 in z, ±3.0 in y (including envelope and lift). With `focalX = 1.9/aspect` and `w ≈ 3.6`, NDC half-width ≈ 4.3·1.1875/12.96 = 0.39 and half-height ≈ 3.0·1.9/12.96 = 0.44 — so the field is about 78% of frame width and up to 88% of height, with black above and below and strands running off both side edges. `refAspect` 1.6 clamp: identical at 640×400 and 1920×1080; portrait shrinks both axes together so the band becomes shorter. No horizon line; the composition is a centred ribbon, not a landscape with sky.

## 9. Randomness and seeds

Two seeded streams: mulberry32 **20260926** for per-strand `seed` values (one draw per strand, 130 draws, consumed in sheet-major order), and a separate `createNoise2D` from the `simplex-noise` package seeded with **20261239** (seed + 313) for the resting meander. Distributions are uniform. The per-strand seed is uploaded but never read by the shader: all wave phases use `φ = 1.71·sheet`, so strands within a sheet are exactly phase-aligned — that shared phase is the difference between cloth and spaghetti. No warmup; the resting shape is fixed at build time and never changes.

## 10. Performance budget

One draw call, 12,220 vertices, 6,110 segments, no textures. Cost is fill-rate on 1 px additive lines; at `alpha 0.4` most of the image is covered several times over by different sheets, which is the visual point but also the main cost. 60 fps on integrated GPUs at 1920×1080 is comfortable. Cut-first: `sheets` 5→3, then `strandsPerSheet` 26→18, then `segments` 48→32, then `maxDpr` 1.5→1.25.

## 11. Host integration

`absolute inset-0 pointer-events-none` holder; `block w-full h-full` canvas; no input. Sizing from holder offsets × `min(devicePixelRatio, 1.5)`, re-run on `window resize`. The one vertex buffer and one program are deleted and `WEBGL_lose_context.loseContext()` called on unmount. One mount per page (shared FPS meter). Only external dependency is the `simplex-noise` package (`createNoise2D`) at build time — it never ships to the GPU. Fully deterministic; no network.

## 12. Failure modes and tells

- **Looks like spaghetti, not cloth** — the shared-coordinate trick is broken: noise inputs must use `u·1.7 + 3.1·sheet` as x and a *slowly varying* `0.06·strand` as y. Per-strand random offsets destroy the sheet read.
- **Solid glowing slab** — `alpha` too high or too many sheets; keep 0.35–0.45 and 5 sheets. Above ~0.6 the overlaps saturate to white.
- **Field is invisible at the left/right edges only** — `pinFade`/`tailFade` reversed; ends must fade *out* both to 0 at u = 0 and u = 1.
- **Strands flicker / drop out** — DPR above 1.5 with 1 px lines and no MSAA; keep `antialias: true` and the DPR cap.
- **Motion looks like a flag flapping** — one wave dominating; all five sines plus the lift term are needed, and `pinHold` must be > 0 so the pinned end stays still.
- **Colour bands too coarse** — `irid` uses `3.4u + 2.4v`; lowering those frequencies makes the whole sheet one hue.
- **Everything is magenta** — `sheen` term missing or `irid` phase stuck; the blue end only survives because the mix is centred at 0.5.
- **Vertex buffer mismatch** — stride must be 7 floats (28 bytes); `a_pos` at 0, `a_data` at 12.

## 13. Tuning knobs

1. `amplitude` — wave depth; 0.3–0.6 keeps it silk, above 0.8 it becomes ribbon.
2. `sheets` and `alpha` — density; 5 × 0.4 is the rested balance.
3. `strandsPerSheet` — weave fineness; 20–32.
4. `flowSpeed` — how fast the current moves; 0.1–0.25.
5. `focal`/`distance` — band size; keep NDC half-width ≈ 0.4.

## 14. Verification checklist

- Band occupies ≈ 75–80% of frame width, 80–90% of height, with black above and below.
- Dominant hues span blue (225°) through violet to magenta (305°); no green or orange.
- Background luma < 2% in the top tenth of the frame.
- Visible left-to-right travel: a crest sampled over 3 s should move ≈2.2 world units downstream (≈25% of the field width).
- Strands visible as discrete 1 px lines in the troughs, saturated bright crossings at the crests.
- No flicker on resize; no clipping of the field's vertical extent.
- Frame differs from the poster (animated phase) but matches its band height, hue range and black sky.

## 15. Porting notes

`gl.LINES` gives 1 px lines on all platforms; do not rely on `lineWidth`. On a Canvas 2D port, draw each segment with `lineWidth = 0.6` and `globalCompositeOperation = "lighter"` — the additive overlap is what makes the cloth read. If you use three.js `LineSegments`, remember it has no per-vertex alpha by default; a `ShaderMaterial` with the alpha formula is required to keep the pinned ends and the fold darkening.
