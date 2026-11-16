---
id: neon-horizon
name: Neon Horizon
family: webgl-f1
renderer: webgl1
poster: assets/posters/neon-horizon.jpg
complexity: M
source_lines: 345
dpr_max: 1.5
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Neon Horizon

## 1. Identity

A banded cream-and-magenta sun hangs over a horizon line, and a magenta-and-cyan
perspective grid scrolls toward the viewer across a dark indigo ground.

## 2. Perceived look

Hard-edged neon over a soft gradient sky. The sun is a 160 px disc with two to
three horizontal cuts and a wide orange bloom; the ground is a fan of magenta
rows and converging cyan columns, thinning to a bright line at the horizon.
Contrast is high on the grid and low in the violet sky; scanlines add a faint
comb. The sun is the only focal point. At t = 3 s the rows are mid-scroll.

## 3. Frame anatomy

1. **Sky** — vertical two-stop mix from `#240847` at the horizon to `#03030F` at
   the top, curved by a 0.75 power.
2. **Stars** — hash points in a 170-per-unit cell grid, twinkling, added.
3. **Sun** — disc plus band cuts, mixed over the sky, then a bloom term added.
4. **Haze** — orange gaussian band 0.03 wide at the horizon, gain 0.55.
5. **Ground fill** — `#04020A` mixed over the sky at 0.86 below the horizon.
6. **Perspective grid** — magenta rows and cyan columns added, fogged near the
   horizon.
7. **Sun reflection** — a 0.15-wide vertical column, gain 0.30.
8. **Finish** — exponential tonemap, 2 px scanlines, radial vignette.

One fullscreen triangle, no blend or depth; alpha false hides the host gradient.

## 4. Motion law

Grid rows scroll toward the viewer at 0.55 world units/s, one row every 0.2597 s
at a fixed screen point (3.85 rows/s). A brightness wave travels with the depth
coordinate at 1.16875 units/s, so rows brighten in sequence. Stars twinkle at
2.0 rad/s with hashed phase. The pointer shifts the horizon by 0.025 and the
scene by 0.04 horizontally, at most 10 px and 16 px at 640x400. Nothing loops;
the sun never moves. Stars fade in with height above the horizon.

## 5. Technique and math

The centred coordinate p is divided by the short axis. Horizon h = 0.035 -
0.025 pointer.y; p.x is offset by 0.04 pointer.x. Sky is mix(skyLow, skyTop,
pow(clamp((p.y - h) / 0.85, 0, 1), 0.75)). Stars sample suv = (p - (0, h)) *
170, a 2.3529 px cell; 4.5% of cells carry one (hash > 0.955), jittered ±0.3
cell, profile pow(max(0, 1 - 10 distance), 6), brightness
0.6 + 0.4 sin(2 t + 40 hash).

The sun sits at (0, h + 0.235), radius 0.2 (80 px), crown 12 px below the top.
Disc mask is 1 - smoothstep(0.985 r, 1.015 r, distance). Depth d = clamp((sunY -
p.y) / 0.4, 0, 1) reaches 0.5 at the disc bottom, so pow(d, 1.35) * 7 spans
2.7460 band cycles. b = |fract(pow(d, 1.35) * 7) - 0.5| * 2, cut =
smoothstep(0.12, 0.55, b), weighted by smoothstep(0.05, 0.6, d). Sun color mixes
crown to base by pow(d, 0.7). Bloom is
exp(-(min(max(0, distance - 0.2) / 0.17, 4))^2) * 0.5, tinted 40% toward base.

Ground: y = max(h - p.y, 0.0018), z = 0.35 / y. Rows use s = (z + 0.55 t) * 7,
screen distance |fract(s) - 0.5| / (0.35 * 7 / y^2). Columns use
xw = p.x * 0.35 / y * 6 with derivative 0.35 * 6 / y. Both divide by their p.y
derivative, so the line gaussian exp(-(min(d / 0.0034, 6))^2) stays 1.36 px
wide at every depth. Row pulse is (0.5 + 0.5 sin(1.6 z + 1.87 t))^5. fog =
smoothstep(0, 0.055, y), ground = 1 below h, and the fill mixes at 0.86.
Reflection: sunTop * exp(-(min(|p.x| / 0.15, 5))^2) * exp(-2.6 y) * 0.30.
Tonemap 1 - exp(-1.5 col), scanlines 0.95 + 0.05 sin(π y_device), vignette
`1 − 0.45·smoothstep(0.5, 1.25, |p − (0, 0.3h)|)` — note the vignette centre
is shifted up by 0.3·horizon, not the frame centre. All arithmetic is mediump.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | device-pixel clamp | L |
| camHeight | 0.35 | 0.2–0.6 | eye height | H |
| scroll | 0.55 | 0.2–1.0 | rows per second | H |
| rowFreq | 7.0 | 4.0–12.0 | rows per world unit | H |
| colFreq | 6.0 | 3.0–10.0 | columns per world unit | M |
| lineThick | 0.0034 | 0.002–0.006 | half-width, 1.36 px | H |
| sunRadius | 0.2 | 0.12–0.28 | disc radius, 80 px | H |
| bandFreq | 7.0 | 4.0–12.0 | cut count on the disc | M |
| pulseFreq | 1.6 | 0.8–3.0 | row-wave frequency | M |
| rowColor | rgb(1.0, 0.16, 0.72) | hue 315–325 | horizontal rows | H |
| colColor | rgb(0.1, 0.9, 1.0) | hue 180–195 | converging columns | H |
| horizon | 0.035 | 0.0–0.1 | horizon height | H |
| skyTop | rgb(0.012, 0.01, 0.06) | violet-black | sky at the top | M |
| skyLow | rgb(0.14, 0.03, 0.28) | violet | sky at the horizon | M |
| haze | rgb(1.0, 0.42, 0.16) | orange | horizon glow | M |
| sunTop | rgb(1.0, 0.92, 0.36) | cream | sun crown | H |
| sunBottom | rgb(1.0, 0.12, 0.55) | magenta | sun base | H |

## 7. Palette and color

Rows `#FF29B8` (hsl 320, 100%, 58%), columns `#1AE6FF` (hsl 187, 100%, 55%),
sun crown `#FFEB5C` (hsl 53, 100%, 68%) into `#FF1F8C` (hsl 331, 100%, 56%) at
the base. Sky runs `#240847` (hsl 266, 81%, 16%) to `#03030F` (hsl 242, 71%,
3%), with orange haze `#FF6B29` (hsl 19, 100%, 58%) and ground `#04020A`.
Emission is added before the 1 - exp(-1.5 x) tonemap; the sun and haze therefore
bleach toward cream where they overlap. All values are display-referred sRGB.

## 8. Composition and camera

Single-point perspective with the camera 0.35 units above the plane, looking at
a horizon 0.035 above centre (14 px at 640x400). The sun's crown sits 12 px
below the top edge and its base 14 px above the horizon; the ground fills the
lower 53.5% of the frame. The short axis sets scale, so columns converge to the
same vanishing point at any width; wide frames add columns, tall frames add rows.

## 9. Randomness and seeds

No RNG and no seed: stars come from a hash of their integer cell, so the field
is fixed and only the twinkle phase varies. Star presence is 4.5% per cell,
jitter uniform in ±0.3 cell, brightness uniform 0.6–1.0. No warmup; the first
frame already shows grid and sun. Compare star placement loosely.

## 10. Performance budget

One fullscreen triangle, one draw call, no textures and no loops. Per pixel:
three hashes, two smoothsteps, one exponential per line family, one tonemap.
Fill-bound and cheap; no assets. 60 fps expected at 640x400 and at 1080p with
DPR 1.5. Cut order: DPR, stars, the reflection column, the second scanline term.

## 11. Host integration

Standard contract. WebGL1 with alpha false, antialias false, depth false and
high-performance preference. Size from the holder with a window fallback, clamp
DPR at 1.5, viewport the backing store. Passive window resize and pointermove;
pointer is window-normalized while the holder stays pointer-events-none. Time is
performance.now() minus a stamp set before the first RAF. Teardown deletes the
buffer and program, then calls WEBGL_lose_context. No assets.

## 12. Failure modes and tells

- **Thick lines near the camera, aliased at the horizon →** width applied in
  world space → divide by the p.y derivative.
- **Horizon drifts on its own →** pointer.y wired to time → keep the pointer term.
- **Rows move sideways →** scroll applied to the column coordinate → add 0.55 t
  to z only.
- **Sun clipped by the top edge →** centre above h + 0.235 or radius above 0.2.
- **Sun shows the wrong number of bands →** depth is normalized over 0.4 (so
  `pow(d, 1.35) · 7` spans 2.75 cycles and yields two or three cuts); dividing by
  0.2 instead makes it span 7 cycles and turns the disc into fine stripes.
- **Grid visible above the horizon →** ground mask missing or inverted relative
  to gl_FragCoord's upward y.
- **Frame washes to cream →** bloom or haze doubled; keep 0.5 and 0.55.

## 13. Tuning knobs

1. scroll — 0.3–0.8 for a slower or faster approach.
2. lineThick — 0.0025–0.005; below 0.002 the grid disappears at 1.5 DPR.
3. sunRadius — 0.16–0.24 keeps the crown margin near 12 px.
4. bandFreq — 5–9 for fewer or finer cuts.
5. horizon — 0.0–0.08 recentres the composition.

## 14. Verification checklist

- Horizon 14 px above centre, sun crown 12 px below the top, ground 53.5% at
  640x400.
- Rows magenta (hue 320), columns cyan (hue 187); no green or white grid.
- Row wave travels toward the viewer; rows never move horizontally.
- Line width constant from foreground to horizon.
- No sun or haze clipping, no scanline moire.
- Compare to `assets/posters/neon-horizon.jpg` for sun size and horizon height.

## 15. Porting notes

Keep the derivative-based line widths; an SDF or three.js plane will not
reproduce them. The scanline term runs on device pixels, so it is 2 backing
pixels — 1.333 CSS px at DPR 1.5 — and will alias if resampled. Render
display-referred, no color management.
