---
id: golden-bloom
name: Golden Bloom
family: canvas-a2
renderer: canvas2d
poster: assets/posters/golden-bloom.jpg
complexity: M
source_lines: 276
dpr_max: 1.5
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Golden Bloom

## 1. Identity

Hundreds of small golden-green seed glows packed on a phyllotaxis spiral around
frame centre, pulsing in two index-wave beats that resolve into visible spiral
arms.

## 2. Perceived look

Dense, glowing, and strictly circular: dots on a sunflower packing, gold at the
centre, yellow-green at the rim, falling to black at the corners. Individual
dots are soft 16–41 px discs with a pale core at 640x400, growing to
25.139–64.418 px at 1080p. Contrast is high but the centre saturates toward pale
gold where hundreds of additive sprites overlap. There is no subject other than
the disc.
At t = 3 s the 8- and 13-arm Fibonacci spirals are clearly readable, and the
bloom is a few percent above its mean size (the breath amplitude is ±6%).

## 3. Frame anatomy

1. **Ground** — full-rect linear gradient from (0, 0) to (W, H), stops
   `#050402`, `#03060a` at 0.5, `#010302`. Opaque, repainted every frame,
   `source-over`.
2. **Core wash** — additive radial gradient centred at frame centre, radius
   `0.62·max(W, H)`, `rgba(96, 62, 14, 0.4)` to `rgba(40, 44, 22, 0.16)` at
   0.35 to `rgba(4, 12, 10, 0)`.
3. **Seeds** — one square sprite blit per seed from 18 pre-baked 48 px glows,
   composite `lighter`, `globalAlpha` 0.12–0.95.
4. **Vignette** — radial gradient at centre, inner radius 0.3R, outer
   R = `0.8·max(W, H)`, `rgba(1, 3, 3, 0)` to `rgba(1, 3, 3, 0.6)`.

Canvas alpha is false and the ground covers every pixel; no host backdrop shows.

## 4. Motion law

No seed translates. Radius scales by `grow = 1 + 0.06·sin(frame·0.0037)`,
period 1698.245 frames (28.304 s). Angle is `i·φ + spin + twist·t`, with spin
0.0016 rad/frame — one turn in 3926.991 frames (65.45 s) — and
`twist = 0.62·sin(frame·0.0009)`, period 6981.317 frames (116.355 s), so the
differential shear is bounded to ±0.62 rad instead of winding up. The two beat
waves run at 0.0125 rad/frame (8.3776 s period) and 0.009 rad/frame
(11.635 s). Each seed twinkles on its own period of 3.116–7.272 s. Motion is
open-ended and entirely reversible.

## 5. Technique and math

Count: `clamp(round(W·H / 620), 640, 2100)` — 640 at 640x400 (413 before the
clamp), 2100 at 1920x1080 (3345 before the clamp).

Layout is phyllotaxis. With `reach = 0.53·hypot(W, H)`, the unit radius is
`radiusUnit = reach / sqrt(count)`: 15.811 px at 640x400, 25.478 px at
1920x1080. Seed i (1-based) sits at angle `θ = i·φ + spin + twist·t` and radius
`r = radiusUnit·√i·grow·(1 + 0.05·(bloom − 0.5))`, where φ = π(3 − √5) =
2.399963 rad (137.5078°). The outermost seed reaches `reach` = 400.001 px at
640x400 and 1167.541 px at 1080p, just past the 377.358 px half-diagonal, so the
corners are included.

Beat: `beat = sin(i·0.052 − wave) + 0.62·sin(i·0.031 + 0.72·wave)`, normalized
as `bloom = clamp((beat / 1.62 + 1)·0.5, 0, 1)`. Because the index is also the
angle, the two beat frequencies interfere into the 8- and 13-arm spirals the
source comment names. `bloom` drives size, alpha and a ±2.5% radius modulation.

Twinkle: `sparkle = 1 + 0.18·sin(frame·0.024·rate + phase)` with rate in
0.6..1.4 and phase uniform; `bloom` is re-clamped to 1.15 after multiplying.

Size: `minSize = spacing·0.8`, `sizeSpan = spacing·1.25`, where
`spacing = sqrt(W·H / count)` — 20 px at 640x400, 31.423 px at 1080p, giving
diameters 16–41 px and 25.139–64.418 px. Hue index is
`round(clamp(t·17·1.06, 0, 17))` with t = i/count, so the last 5.7% of seeds
all map to the outer hue.

Alpha: `clamp(0.34 + 0.61·bloom^0.85·(1.08 − 0.28t), 0.12, 0.95)`, which fades
the rim by 0.28 and keeps the centre near saturation. Seeds are culled if they
fall more than one spacing outside the rect.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | device pixel ratio clamp | L |
| seedArea | 620 | 300–1400 | area per seed; count = area / seedArea | H |
| minSeeds | 640 | 300–1200 | count floor | M |
| maxSeeds | 2100 | 1200–4000 | count ceiling | M |
| radiusFill | 0.53 | 0.4–0.62 | bloom radius as a fraction of the diagonal | H |
| hues | 18 | 8–32 | number of baked hue steps | M |
| hueRange | [38, 104] | any two hues | centre-to-rim hue span | H |
| armA | 0.052 | 0.02–0.1 | first beat frequency per index | H |
| armB | 0.031 | 0.01–0.08 | second beat frequency per index | H |
| armBias | 0.62 | 0–1 | weight of the second beat | M |
| phaseSpeed | 0.0125 | 0.004–0.03 | beat travel, rad/frame | H |
| rotation | 0.0016 | 0–0.006 | global spin, rad/frame | M |
| shear / shearSpeed | 0.62 / 0.0009 | 0–1.2 / 0–0.003 | bounded differential twist and how fast it saturates | M |
| twinkle | 0.18 | 0–0.4 | per-seed size and alpha pulse | L |
| sizeRange | [0.8, 2.05] | 0.5–3 | sprite diameter in spacing units | H |
| alphaRange | [0.34, 0.95] | 0.2–1 | stored alpha span | M |
| breathe | 0.06 | 0–0.2 | slow global radius pulse | L |
| vignette | 0.6 | 0.3–0.9 | corner darkening | M |
| warmup | 60 | 20–200 | hidden pre-roll frames | L |

## 7. Palette and color

Eighteen glows from hue 38 to 104 in steps of 3.882 — sample colours:
`#FFBE4D` hsl(38.1, 100%, 65.1%), `#C8F04A` hsl(74.5, 84.7%, 61.6%),
`#56F81B` hsl(104, 94%, 54%). The
sprite ramps hsla(hue, 100%, 92%, 1) at the centre through 74% at 0.16, 54% at
0.36, 38% at 0.66, to hsla(hue, 80%, 30%, 0) at the edge. Ground `#050402` →
`#03060a` → `#010302`; core wash `rgba(96, 62, 14, 0.4)`; vignette
`rgba(1, 3, 3, 0.6)`. Display sRGB throughout; additive stacking is what turns
the centre gold rather than any per-seed colour choice.

## 8. Composition and camera

A single centred disc with no horizon, sized to `0.53` of the diagonal so the
outer seeds overshoot the corners by 6%. Only 51% of the seeds fall inside the
rect at 640x400 (about 326 of 640) and 48% at 1080p (about 1017 of 2100); the
rest are culled off-frame. The bloom overfills the height at 16:9 and the width
in portrait, so both crops look intentional. There are no safe margins, and the
vignette supplies the only edge treatment.

## 9. Randomness and seeds

`Math.random()` only; any seed, same distribution. Seed positions are
deterministic from the index — only `phase` (uniform 0..2π) and twinkle `rate`
(uniform 0.6..1.4) are random, one pair per seed at build. Sixty warmup frames
(1 s) advance the wave clock so the first visible frame lands mid-unfurl rather
than on the symmetric pose every wave shares at phase zero.

## 10. Performance budget

640–2100 sprite blits per frame from 18 baked 48 px canvases, plus two
gradients rebuilt per frame (core wash, vignette). At 640x400 that is roughly
326 visible draws; at 1080p about 1017. Fill is modest because most sprites are
under 65 px. DPR capped 1.5; comfortably 60 fps on integrated graphics. Cut
order: `maxSeeds`, then `radiusFill`, then DPR, then `hues`.

## 11. Host integration

Standard contract: positioned `inset: 0` host, size from
`offsetWidth/offsetHeight` with a window fallback, passive resize listener, a
synchronous 60-frame warmup, then RAF. Context is
`getContext("2d", { alpha: false })`. Sprites are baked once at mount and are
size-independent; resize rebuilds only the count, `radiusUnit`, `spacing` and
the two per-seed arrays. Teardown removes the listener, cancels the frame, stops
the meter, and nulls sprites, phase and rate.

## 12. Failure modes and tells

- **Dots on concentric rings instead of a spiral →** radius uses i instead of
  √i; the packing becomes a set of hoops.
- **Even scatter with no arms →** golden angle replaced by an even angular
  step, or both beat amplitudes zero.
- **Arms wind into mush over minutes →** shear accumulating as `frame·0.62`
  rather than a bounded sine.
- **Centre blows out to flat white →** additive sum too high; keep the 0.28·t
  rim fade, the 0.95 clamp and the area-derived count.
- **Bloom does not fill the corners →** `radiusFill` below 0.5 or count not
  clamped to `minSeeds` at small sizes.
- **Static frame at load →** warmup skipped, leaving the wave at its symmetric
  zero phase.

## 13. Tuning knobs

1. `seedArea` — lower for a finer packing (300–1400).
2. `radiusFill` — 0.45 for a tighter bloom, 0.6 to fill corners (0.4–0.62).
3. `armA` — raise for more, thinner arms (0.02–0.1).
4. `hueRange` — widen toward 20–120 for more lime, narrow for pure gold.
5. `twinkle` — 0.1 for calm, 0.3 for a shimmering field.

## 14. Verification checklist

- Centre hue near 38, rim near 104; no blue or magenta dots.
- 640 seeds at 640x400 and 2100 at 1920x1080, by the area formula.
- Dot diameter 16–41 px at 640x400.
- Spiral arms countable at 8 and 13; no concentric rings.
- Additive centre is pale gold, never a flat white disc.
- Whole bloom breathes ±6% on a 28.304 s cycle.
- Compare to `assets/posters/golden-bloom.jpg`: same dot packing, same
  gold-to-green radial ramp. Exact seed phases will differ.

## 15. Porting notes

Compute φ as π(3 − √5); using 137.5° instead of 137.5078° bends the outer arms.
Sprites can be shared across instances, but the per-seed phase and rate arrays
cannot. No filters or blend modes beyond `lighter`.
