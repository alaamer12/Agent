---
id: event-horizon
name: Event Horizon
family: webgl-f1
renderer: webgl1
poster: assets/posters/event-horizon.jpg
complexity: M
source_lines: 325
dpr_max: 1.5
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Event Horizon

## 1. Identity

A black hole sits at frame center: a perfectly black disc rimmed by a thin photon
ring, ringed by a tilted golden accretion disk and a halo of lensed light, over a
sparse warm starfield.

## 2. Perceived look

Smooth, luminous, and softly blurred — nothing is sharp except the two ring
edges. The shadow is a clean black circle about 30% of the frame height. Around
it a thin bright ring, then a tilted ellipse of molten gold sliced into petals by
a rotating grain, then a broad brown halo. Two horizontal beige streaks
(left dimmer, right brighter) flare out of the disk like lensed jets. Stars are
tiny single-pixel points, sparse and warm-white. Background is a deep brown-black,
never blue-black. Contrast peaks at the photon ring; the disk is mid-tone.

## 3. Frame anatomy

One fragment pass, no geometry, no blending that matters (alpha 1).

1. **Background** — deep brown `deep` color everywhere, plus the starfield,
   suppressed inside the shadow.
2. **Lensed sky** — the starfield is sampled three times along the radial bend
   direction, smearing stars toward the hole.
3. **Accretion disk** — a Gaussian band in tilted radius, modulated by a spiral
   grain and a Doppler term.
4. **Lensed arc, photon ring, halo** — three more Gaussians in screen radius.
5. **Post** — shadow knockout, exponential tone map, radial vignette.

Canvas is opaque (`alpha: false`, `antialias: false`, `depth: false`); no host
backdrop shows.

## 4. Motion law

The disk pattern rotates differentially: `swirl = 2θ + 0.55 t (0.6 + 1.4/(r+0.35))`,
so the angular rate falls from ~1.68 rad/s at the disk's inner edge (r ≈ 0.22)
through ~1.45 at the disk peak (r = 0.34) to ~0.90 at r = 1 — the inner disk
visibly outruns the outer. The grain multiplies swirl by 3 and adds `16 dr` and
`−0.9 t`, so its petals sweep a full period in roughly 1.8 s at the disk peak and
1.5 s at the inner edge. The lensed arc pulses at 1.4 rad/s; the photon ring is static. Stars
are static; only their smear length follows the bend. Open-ended, no loop. The
pointer shifts the whole composition by at most 0.02 in x and 0.014 in y, with no
damping.

## 5. Technique and math

**Coordinates.** `p = (fragCoord − 0.5 · res) / min(res.x, res.y)`, then
`p += pointer · (0.02, 0.014)`. Radius `r = |p|`, direction `dir = p/r`.

**Lensing.** A cheap inverse-square displacement:
`bend = 0.055 / (r² + 0.045)`, sampled point `q = p + dir · 0.22 bend`. The
0.045 floor prevents the displacement from exploding at the singularity and is
what keeps the inner disk from tearing. The shadow mask is
`inShadow = 1 − smoothstep(0.9·0.155, 1.16·0.155, r)`, i.e. fully black below
r = 0.1395, fading to zero by r = 0.1798.

**Stars.** A cell-based point field: cell `floor(14 q)`, offset within the cell
`fract − 0.5`, two hashes set the star's in-cell offset (scaled 0.72), a third
gates 14% of cells (`step(0.86, h)`), a fourth varies brightness in 0.5…1.0.
Star mask `pow(max(0, 1 − 11 d), 9)` — a very tight falloff, so stars are 1–2 px
at 640x400. Color mixes a blue-white `(0.5, 0.62, 0.9)` with a warm white
`(1.0, 0.95, 0.86)` by cell hash. The smear is three taps along `−dir` at 0,
`0.55`, and `1.15` of `smear = clamp(3 bend, 0, 0.5)`, weights 1, 0.7, 0.45 —
a poor man's radial blur that only lengthens near the hole.

**Disk.** Flatten the lensed point `dq = (q.x, q.y / 0.19)`; the small tilt makes
the circular band an ellipse squashed vertically. `band = gauss(|dq|, 0.34, 0.12)`
with `gauss(x, c, w) = exp(−((x−c)/w)²)`. Grain
`0.7 + 0.42 sin(3 swirl + 16 |dq| − 0.9 t)`, Doppler
`0.42 + 0.9 (0.5 + 0.5 cos θ)^1.2` — brighter on the right side, which is the
visible beige flare. `disk = band · grain · doppler`.

**Rings.** `arc = gauss(r, 0.240, 0.03) · (0.62 + 0.5 sin(5 swirl − 1.4 t))` is
the lensed far side of the disk. `photon = gauss(r, 0.1597, 0.009)` is the sharp
ring at 1.03 × shadow radius. `halo = gauss(r, 0.403, 0.2) · 0.3` is the brown
glow. All are multiplied by `1 − inShadow`, and the shadow is then knocked out
again after tone mapping with `1 − 0.995 inShadow` so nothing, not even the tone
map, can lift the black disc.

**Color.** `col = deep + 0.85 (1−inShadow) starCol + 0.85 mid·heat + 0.6 hot·heat²
+ 0.75 (1,0.97,0.92) photon² (1−inShadow)`, where
`heat = 1.15 disk + 0.85 arc + 1.7 photon + halo`. The square on `heat` is what
turns the disk core white-gold while the outskirts stay orange.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | resolution clamp | L |
| shadow | 0.155 | 0.10–0.22 | black disc radius | H |
| bend | 0.055 | 0.02–0.12 | lensing strength and star smear | H |
| diskRadius | 0.34 | 0.25–0.5 | disk distance from center | H |
| diskWidth | 0.12 | 0.06–0.2 | disk thickness | H |
| tilt | 0.19 | 0.08–0.35 | vertical squash of the disk | H |
| spin | 0.55 | 0.2–1.2 | disk rotation rate | M |
| starScale | 14.0 | 8–24 | star density (cells per p unit) | M |
| star gate | 0.86 | 0.7–0.95 | fraction of cells with a star | M |
| star falloff | 11 / power 9 | — | star size (sharper with larger) | M |
| star smear | 3.0 × bend | 1–5 | radial stretch near the hole | M |
| arc radius | 1.55 × shadow | 1.3–1.8 | lensed-ring position | M |
| photon width | 0.009 | 0.005–0.02 | ring sharpness | H |
| halo radius | 2.6 × shadow | 2.0–3.2 | outer glow spread | L |
| grain contrast | 0.42 | 0.2–0.6 | petal visibility | M |
| doppler gain | 0.9 | 0.4–1.4 | left/right brightness split | M |
| exposure | 1.25 | 1.0–1.6 | tone-map brightness | M |
| vignette | 0.55 | 0.3–0.8 | corner falloff | L |

## 7. Palette and color

Deep `#040305`, mid orange `#D95210`, hot `#FFDB8C`, star blue-white
`#809EE6`, star warm-white `#FFF2DB`, photon highlight `#FFF7EB`. HSL: the disk
gradient runs from hue ≈20° at 86% saturation (`#D95210`) to hue ≈41° at 100%
(`#FFDB8C`); the deep base is hue 270°, 25% saturation, 1.6% lightness, and the
broad halo lifts the visible corners to a dark warm brown (hue ≈25–35° at 5–8%
lightness) — the host gradient never shows because the canvas is opaque.
`1 − exp(−1.25 c)` compresses the disk core to white-gold while leaving the halo
brown. All values are display sRGB.

## 8. Composition and camera

Perfect radial composition: the hole is centered, the disk is an ellipse wider
than tall (tilt 0.19), and the halo bleeds to the frame edges. Shadow diameter is
31% of frame height at any aspect (radial normalization). Wide aspect shows the
full left and right flares; tall aspect crops them, leaving a vertical ring.
Vignette starts at r = 0.55 and cuts brightness by 55% at r = 1.25, so corners
stay dark but never black.

## 9. Randomness and seeds

`hash21` (`fract(p·(123.34,456.21))` plus a dot scramble) drives star position,
gate, and brightness from cell coordinates; there is no seed and no state, so the
star layout is fixed forever. No warmup. Time enters through the swirl (which
also drives the grain) and the arc phase; at t = 0 the grain starts at a fixed
orientation.

## 10. Performance budget

One draw call, three vertices. The starfield is evaluated three times, each with
four hashes, so about twelve hashes per pixel — trivial. The rest is a dozen
Gaussians and powers. This is one of the cheapest scenes in the gallery: 60 fps
at 4K on a discrete GPU, 60 fps at 640x400 practically everywhere. Cut order: DPR,
star taps from 3 to 2, halo term.

## 11. Host integration

Standard contract; window pointer normalized to −1…1, applied without damping.
No textures — the starfield is procedural, not an image. Resize recomputes the
drawing buffer and viewport; radial normalization keeps the hole the same
fraction of the frame height in both orientations. Teardown removes both
listeners, deletes buffer and program, loses the context.

## 12. Failure modes and tells

- **Disk tears or pinches at the center →** the `+ 0.045` floor in the bend
  denominator was dropped; the inverse square goes to infinity.
- **Shadow has a grey wash →** the post-tone-map knockout `1 − 0.995 inShadow`
  is missing; tone mapping lifts the black.
- **Disk appears circular, not elliptical →** the `q.y / tilt` flattening was
  applied before lensing instead of after.
- **No stars →** the gate threshold reversed (`step(0.86, h)` needs ~14% of
  cells above it; `step(h, 0.86)` keeps 86% but the falloff then merges them).
- **Stars are smeared uniformly →** smear ignores `bend`, so it is constant
  across the frame.
- **Photon ring is a fat donut →** width raised above ~0.02, or exposure so high
  that the ring saturates into the halo.
- **Left and right flares are equal →** Doppler term dropped; the `cos θ`
  weighting is what breaks the symmetry.

## 13. Tuning knobs

1. `shadow` — hole size; drives everything else's scale (0.12–0.20).
2. `bend` — how violently the sky wraps (0.03–0.09).
3. `diskWidth` — thin razor ring versus broad torus (0.08–0.18).
4. `spin` — how fast the petals churn (0.3–0.9).
5. `starScale` — sparse deep field versus dense cluster (10–20).

## 14. Verification checklist

- Centered black disc, hard-edged, no grey inside.
- A thin bright ring immediately outside the shadow.
- Elliptical gold band, wider than tall, with visible radial petals.
- Right flare noticeably brighter than the left.
- Sparse warm stars, elongated only near the hole.
- Corners dark brown, not black and not grey.
- Compare with `assets/posters/event-horizon.jpg`: same disc size, ring
  thickness, and petal count; rotation phase differs.

## 15. Porting notes

Everything is screen-space faking — this is not a physical lensing model. Do not
"correct" the inverse-square bend into a real light-ray deflection; the
`0.045` floor and the 0.22 gain are tuned together. Mediump is sufficient and is
what the original ships.
