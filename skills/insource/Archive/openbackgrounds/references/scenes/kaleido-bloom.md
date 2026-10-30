---
id: kaleido-bloom
name: Kaleido Bloom
family: canvas-a2
renderer: canvas2d
poster: assets/posters/kaleido-bloom.jpg
complexity: M
source_lines: 412
dpr_max: 1.5
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Kaleido Bloom

## 1. Identity

Five layers of asymmetric bezier petals, mirrored through 8–12 radial folds and
counter-rotating around a white-magenta core on a near-black violet ground.

## 2. Perceived look

Glowing vector linework over translucent fills: crisp 1.25–1.75 px strokes,
soft filled petals, and a hot saturated centre that clips to white. The
silhouette is a rosette with radius 69% of the half-diagonal; its points run
past the top and bottom edges. Magenta and violet dominate; blue-green
appears only where the hue cycle swings low. Edges are antialiased, not
blurred, so the flower reads as glass. At t = 3 s the outer layer has rotated
about 68° and every petal is mid-morph.

## 3. Frame anatomy

1. **Ground** — full-rect radial gradient at centre, radius
   `0.78·max(W, H)`, `#0a0417` to `#05030f` at 0.45 to `#010104`. Opaque,
   repainted each frame, `source-over`.
2. **Petal bloom** — additive (`lighter`), five layers. Each wedge draws two
   mirrored petals: a fill in hsla(hue + 26, 92%, light − 16%, layer fill alpha)
   then a stroke in hsla(hue, 92%, light, layer alpha), 1.25–1.75 px, round join
   and cap. A glow bead sits at each tip.
3. **Fold seams** — 8–12 lines, 1.3 px, from 0.12·reach to 1.32·reach,
   `rgba(198, 224, 255, 0.14)`, rotated 8.64°/s; still under `lighter`.
4. **Core** — additive radial gradient of radius `0.34·reach·pulse`, plus
   12–60 orbiting spark sprites.
5. **Vignette** — radial gradient, inner 0.34R, outer R = `0.76·max(W, H)`,
   `rgba(2, 1, 8, 0)` to `rgba(2, 1, 8, 0.72)`.

Canvas alpha is false; no host backdrop shows.

## 4. Motion law

`time` is the raw frame counter, so every rate is per frame at 60 fps. Layer
spins are 0.00105, −0.00152, 0.00205, −0.00268 and 0.00058 turns/frame — one
turn in 15.873, 10.965, 8.130, 6.219 and 28.736 s. Each layer's length breathes
between 0.67 and 1.01 of its base on periods of 19.18–57.54 s. Four independent
sines drive each layer's control points, so the shape never repeats. The base
hue cycles 192→322 in 1388.889 frames (23.148 s); the core pulses at 0.011 and
0.037 rad/frame (9.52 s and 2.83 s); sparks orbit at 0.054–0.252 rev/s with a
wobble of 4–16% of their radius. Nothing accumulates.

## 5. Technique and math

Symmetry order is `folds = round(uniform(8, 12))`, fixed at mount. Reach is
`0.345·hypot(W, H)` = 260.378 px at 640x400 and 760.003 px at 1920x1080.

Each layer has a scale, fold multiplier, spin, stroke width, alpha, fill and
wobble gain. In array order, the tuples `(scale, foldMul, speed, width, alpha,
fill, wobble)` are (1.0, 1, 0.00105, 1.75, 0.62, 0.085, 1.0), (0.74, 1,
−0.00152, 1.5, 0.7, 0.1, 1.35), (0.52, 2, 0.00205, 1.3, 0.56, 0.07, 1.7),
(0.3, 2, −0.00268, 1.25, 0.66, 0.11, 2.1), (1.22, 1, 0.00058, 1.35, 0.3,
0.045, 0.7). Wedge count is `folds·foldMul`; with multipliers 1, 1, 2, 2, 1
that is 7·folds wedges — 56 to 84 — hence 112 to 168 fills and strokes, and 56
to 84 beads.

Petal geometry in the rotated wedge frame, with y up-negative: a cubic from
(0, 0) to (L, 0) with controls (L·w1, −h1) and (L·w2, −h2), closed by a cubic
through (L·w2·0.86, h2·0.6) and (L·w1·1.24, h1·1.42), where
L = reach·layerScale·breathe, h1 = L·bulgeA and h2 = L·bulgeB. The mirrored pass
flips the sign of every y control and multiplies h1 by 1.28 and h2 by 0.72 —
that asymmetry is what makes the wedge a butterfly rather than a leaf. w1 =
0.26 + 0.15·sin, w2 = 0.6 + 0.19·cos, bulgeA = 0.3 + 0.16·sin, bulgeB = 0.19 +
0.11·cos, all driven by `time × 0.0024–0.0037 × wobble + layerOffset`.

Wedge hue is `baseHue + 46·sin(2·wedge + spin/2) + 9·layer`; saturation is
fixed at 92; stroke lightness is `62 + 12·sin(time·0.004 + f)`. The bead sits
at 1.01·L with diameter `width·5.5·(0.85 + 0.3·sin(time·0.01 + f))`, alpha
`0.75·layerAlpha` clamped 0.12–0.85.

Core: radius `reach·0.34·(0.86 + 0.2·sin(0.011t) + 0.07·sin(0.037t))`, hue
`300 + 30·sin(0.002t)`, four stops ending at hsla(280, 90%, 40%, 0). Sparks are
drawn on an ellipse squashed to 0.86 in y.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | device pixel ratio clamp | L |
| foldRange | [8, 12] | 4–24 | integer symmetry order, one roll per mount | H |
| reach | 0.345 | 0.25–0.45 | bloom radius as a fraction of the diagonal | H |
| hueSpan | [192, 322] | any two hues | base hue travel | H |
| hueSpeed | 0.00072 | 0–0.002 | hue cycle, turns/frame | M |
| layers[0].scale | 1.0 | 0.6–1.4 | outer layer length | H |
| layers[0].speed | 0.00105 | 0–0.004 | outer spin, turns/frame | M |
| layers[2].foldMul | 2 | 1–3 | doubles wedge count on the inner layers | H |
| lineWidth | 1.25–1.75 | 0.8–3 | stroke width in CSS px | M |
| layer.alpha | 0.3–0.7 | 0.1–1 | stroke opacity | H |
| layer.fill | 0.045–0.11 | 0–0.25 | fill opacity; the glass body | H |
| layer.wobble | 0.7–2.1 | 0.3–2.5 | per-layer fold wobble; higher = more liquid seams | M |
| seamAlpha | 0.14 | 0–0.4 | fold line visibility | M |
| coreScale | 0.34 | 0.2–0.5 | core radius relative to reach | M |
| sparkArea | 46000 | 20000–90000 | area per spark; count = area / sparkArea | L |
| minSparks / maxSparks | 12 / 60 | 4–120 | spark count clamp | L |
| warmup | 26 | 0–80 | hidden pre-roll frames | L |

## 7. Palette and color

Base hue oscillates 192→322 via `0.5 + 0.5·sin`; each wedge adds ±46, each
layer 9. Fills use hue + 26 at 16 points lower lightness, so a magenta stroke
sits over a plum body. Strokes
are hsl(hue, 92%, 50–74%); fills hsla(hue + 26, 92%, 34–58%, 0.045–0.11). The
core is hsla(300 ± 30, 100%, 92%, 0.85) falling through 72% and 56% to
hsla(280, 90%, 40%, 0). Seams are `rgba(198, 224, 255, 0.14)` (`#C6E0FF`);
ground `#0a0417` → `#05030f` → `#010104`; vignette `rgba(2, 1, 8, 0.72)`. All
display sRGB.

## 8. Composition and camera

Centre-locked, no horizon. Reach is 0.345 of the diagonal, so the petal ring
occupies 69% of the half-diagonal and the outer layer's tips run past the top
and bottom edges at 16:9; the seams, at 1.32·reach, stop just inside the
corners. Wide frames keep the rosette circular and leave more black at the
sides; portrait frames clip the horizontal petals instead.

## 9. Randomness and seeds

`Math.random()` only; any seed, same distribution. `folds` is one integer roll
in 8..12 at mount; sparks get radius 0.24–1.12·reach, direction, speed
0.0009–0.0042 rev/frame, wobble 4–16%, size 4–12 px scaled by reach/260 and a
sprite index. Twenty-six warmup frames (0.43 s) step the clock so the first
visible frame opens mid-morph rather than on the symmetric zero pose.

## 10. Performance budget

112–168 petal fills and the same number of strokes per frame, 56–84 bead
sprites, one core gradient and 12–60 spark sprites. Each wedge costs a
save/translate/rotate/restore plus two path builds, so path count — not fill
area — dominates. Stroke width is fixed in CSS px, so a 1080p canvas gets
relatively thinner lines. DPR capped 1.5; 60 fps on integrated graphics. Cut
order: inner `foldMul`, then sparks, then DPR.

## 11. Host integration

Standard contract: positioned `inset: 0` host, size from
`offsetWidth/offsetHeight` with a window fallback, passive resize listener, a
26-frame synchronous warmup, then RAF. Context is
`getContext("2d", { alpha: false })`. `folds` is rolled once at mount and is
deliberately not re-rolled on resize; resize recomputes only `reach` and the
spark field. Teardown removes the listener, cancels the frame, stops the meter,
and drops the sprite and spark arrays.

## 12. Failure modes and tells

- **Flower looks like a star polygon →** the mirror pass is missing, so each
  wedge draws one petal instead of a mirrored pair.
- **Radial seam lines invisible or harsh →** `seamAlpha` outside 0.08–0.2, or
  the seam pass drawn after the core instead of inside the bloom.
- **Petals collapse to straight lines →** the four control sines lost their
  amplitudes, or `bulgeA`/`bulgeB` are zero.
- **Bloom frozen →** speeds multiplied by delta seconds instead of frames.
- **Core renders as a square →** the fill rect is smaller than twice the
  gradient radius.
- **Centre flat white →** core alpha too high or the core drawn twice.

## 13. Tuning knobs

1. `foldRange` — 6 for a coarse flower, 16 for a fine one (4–24).
2. `reach` — 0.3 to pull the bloom in, 0.42 to fill the frame (0.25–0.45).
3. `layer.fill` — raise to 0.15 for glassier petals.
4. `hueSpeed` — 0 for a fixed violet-magenta palette.
5. `seamAlpha` — 0 to remove the kaleidoscope device entirely.

## 14. Verification checklist

- Symmetry order between 8 and 12, identical on every resize.
- Dominant hue band 250–322 except during the low half of the cycle.
- 112–168 petals and 56–84 beads at 8–12 folds.
- Stroke width 1.25–1.75 CSS px at any canvas size.
- Core white-magenta, roughly 0.34·reach in radius, never square.
- Seams visible as faint blue-white rays, never as bright spokes.
- Compare to `assets/posters/kaleido-bloom.jpg`: same magenta rosette, same
  dark violet ground, same thin glass seams. Folds may differ.

## 15. Porting notes

`lineWidth` is in CSS pixels, so do not scale it with canvas size or DPR — the
transform already handles DPR. Preserve canvas `lineJoin`/`lineCap` round;
SVG stroke defaults differ. Hue rotation must run on the frame counter, not on
wall-clock seconds, or the cycle rate changes with refresh rate.
