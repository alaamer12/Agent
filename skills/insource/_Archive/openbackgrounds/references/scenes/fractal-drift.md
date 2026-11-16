---
id: fractal-drift
name: Fractal Drift
family: webgl-f6
renderer: webgl1
poster: assets/posters/fractal-drift.jpg
complexity: M
source_lines: 314
dpr_max: 1.5
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Fractal Drift

## 1. Identity

A drifting Julia set rendered as glowing depth contours — magenta fractal
masses on a dark teal field, ringed by interference bands and dusted with white
specks.

## 2. Perceived look

High-contrast, soft-edged and nebular. The set's interior is near-black; its
boundary blooms into saturated magenta with a thin teal rim. Around each mass,
concentric contour rings read as topographic depth. The ground is a mottled
dark teal rather than black, and a sparse field of white dust specks sits on
top. Edges are smooth gradients, not crisp; the whole frame looks like a
long-exposure astrophotograph. There is no single focal point — two or three
blooms are visible, weighted by where the drift has taken the parameter.

## 3. Frame anatomy

A single fullscreen pass, no blending, no depth, no clearing (the oversized
triangle covers every pixel).

1. **Ground** — deep violet `rgb(0.015, 0.008, 0.03)` modulated by a slow nebular
   sine, which is what turns it into a mottled dark teal-violet.
2. **Contour fill** — teal and magenta mixed by the interference term, weighted
   by the distance-estimate glow.
3. **Core highlight** — near-white `rgb(1.0, 0.95, 1.0)` added where the glow is
   extreme, which produces the bright "plus" shapes at the centers of the
   blooms.
4. **Dust** — sparse white points from a hashed grid.
5. **Post** — exponential tonemap, then a radial vignette to 45% at the frame
   edge.

Canvas is opaque (`alpha: false`); no host backdrop shows through.

## 4. Motion law

Four independent, slow drifts. The domain rotates at 0.02 rad/s (one turn per
313 s). The zoom breathes between 1.26 and 1.44 with period 57.1 s. The Julia
parameter walks a closed wobbled circle with period 139.6 s, so the topology
morphs continuously but returns. Contour bands slide inward at roughly 0.3 rad/s
of phase. Nothing loops exactly; the composition is open-ended. Pointer offset
follows the cursor with a 0.035 gain and no easing.

## 5. Technique and math

Coordinates are centered and normalized by the shorter axis:
`p = (fragCoord - 0.5 * resolution) / min(resolution.x, resolution.y)`, so the
visible vertical span is exactly one unit. Pointer offsets p by up to 0.035.
Then p is rotated by `0.02 t` and scaled by `zoom · (1 + 0.07 sin(0.11 t))`;
that same transformed p feeds the Julia iteration, the nebula term, and the
vignette.

The parameter is `c = 0.7885 * (cos a, sin a) + 0.028 * (cos(3a + 1), sin(2a))`
with `a = 0.045 t`. The base radius 0.7885 places c just outside the main
cardioid, where the Julia set is a connected, filamentary dust — the classic
"smooth" parameter window.

Iteration: `z ← z² + c` from `z = p`, up to 40 iterations, bailout at
`|z|² > 256`. The derivative `d ← 2 z d + 1` is tracked alongside. On escape:

- distance estimate `de = |z| · ln|z| / |d|`, clamped to 3,
- smooth iteration count `mu = iter + 1 − log₂(ln|z| / ln 2)`.

`glow = 1 / (1 + 26 de)` is the core visual term: it is near 1 on the boundary
and falls off within a few hundredths of a unit.

The contour field is
`film = 0.5 + 0.5 sin(0.85 mu + 2.6 ln(1 + 260 de) − 0.3 t)`. Combining the
smooth iteration count with a log of the distance estimate produces rings that
are dense near the boundary and spread out into the ground.

Color composition, in order: ground modulated by a nebular sine; mix toward
teal by `film · (0.16 + 0.95 glow)`; mix toward magenta by
`(1 − film) · (0.12 + 1.05 glow)`; add `1.5 glow⁵` of near-white; add
`0.35 glow²` of teal; add dust. Then `1 − exp(−1.35 col)` and a vignette
`1 − 0.55·smoothstep(0.45, 1.2, |p|)`.

Dust is `pow(hash21(floor(95 p)), 60)`, i.e. one speck per ~95 grid cells with a
very steep power so only a few cells light up.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | device pixel ratio clamp | L |
| zoom | 1.35 | 0.9–2.2 | fractal scale; higher shows deeper filaments | H |
| cRadius | 0.7885 | 0.74–0.82 | Julia parameter radius; topology selector | H |
| cSpeed | 0.045 | 0.01–0.12 | parameter orbit rate in rad/s | M |
| cWobble | 0.028 | 0–0.06 | secondary parameter wobble; filament shimmer | M |
| deScale | 26 | 10–60 | glow falloff; lower = wider blooms | H |
| iterations | 40 | 24–80 | escape-time depth; smoothness of contours | M |
| bailout | 256 | 64–1024 | squared escape radius | L |
| teal | (0.1, 0.78, 0.82) | any | cool lobe of the contour palette | H |
| magenta | (0.95, 0.12, 0.6) | any | warm lobe of the contour palette | H |
| hot | (1.0, 0.95, 1.0) | any | core highlight color | M |
| deep | (0.015, 0.008, 0.03) | any dark | ground color | M |
| rotate rate | 0.02 rad/s | 0–0.05 | domain rotation | L |
| zoom breathing | 0.07 amplitude, 0.11 rad/s | — | 57 s pulse | L |
| dust grid | 95 | 40–180 | speck density | L |
| tonemap gain | 1.35 | 1–2 | overall exposure | M |
| vignette | 0.55 | 0–0.8 | corner darkening | L |

## 7. Palette and color

Teal `#19C7D1` ≈ `hsl(184, 78%, 46%)`, magenta `#F21E99` ≈
`hsl(325, 89%, 54%)`, hot `#FFF2FF`, deep `#04020A`. All values are authored in
display sRGB and written straight to the framebuffer; there is no linear
working space. The interference term makes teal and magenta alternate in bands
rather than blend into violet, which is why the frame stays high-chroma.
Exponential tonemap compresses the near-white cores.

## 8. Composition and camera

Orthographic, no camera. The visible vertical span is 1 unit; horizontal spans
`aspect` units, so wide frames reveal more of the fractal rather than stretching
it. The set is not centered — the parameter drift moves masses across the frame
over the 140 s cycle. The vignette keeps the corners from competing with the
blooms. At portrait aspect the same vertical span shows fewer blooms across.

## 9. Randomness and seeds

Only the dust uses randomness, through a stateless 2D hash of the cell
coordinate (no seed, no state). Everything else is deterministic from time.
There is no warmup: the first frame is fully formed, though it opens at the
t = 0 parameter rather than the poster's phase.

## 10. Performance budget

One draw call, one triangle, 40 iterations per pixel with ~12 float operations
each. Fill-rate bound; at DPR 1.5 and 640x400 the fragment cost is roughly
60 M iterations/s at 60 fps, which a laptop iGPU handles. Cut order: DPR, then
iterations (32 is visually close), then the dust hash.

## 11. Host integration

Standard contract. No props, no external assets, pointer listener on the window
because the root is pointer-transparent. Teardown deletes the buffer and
program and explicitly loses the GL context (the gallery exceeds the browser's
~16 live-context cap). Resize only updates the viewport and canvas size; the
fractal is resolution-independent by construction.

## 12. Failure modes and tells

- **Blobby, soft-edged masses with no filaments →** `cRadius` inside the main
  cardioid (~< 0.74). Move toward 0.79.
- **Frame is a flat magenta wash →** `deScale` too low, so glow saturates
  everywhere. Raise toward 40.
- **Contour rings look like hard concentric circles →** too few iterations for
  the zoom; raise iterations or lower zoom.
- **Aliased sparkle at the boundary (worse than the poster) →** DPR low and
  `antialias` on. The original disables antialias and relies on DPR 1.5 plus
  smooth tonemapping.
- **No dust visible →** dust grid too fine (value too high) or hash power too
  steep.
- **Washed-out corners →** vignette removed.
- **Fractal drifts off-screen on resize →** normalization by the shorter axis
  replaced with per-axis normalization.

## 13. Tuning knobs

1. `cRadius` — topology and how filamentary the set is (0.74–0.82).
2. `deScale` — bloom width and glow spread (18–40).
3. `zoom` — detail level (1.0–1.8).
4. `iterations` — contour smoothness near the boundary (32–56).
5. `teal`/`magenta` — the two-hue contour identity.

## 14. Verification checklist

- Ground is dark but not black, with a visible teal-violet mottle.
- Magenta dominates the blooms; teal appears as rims and thin rings.
- Contour rings increase in density toward each bloom.
- Near-white cores exist but occupy under 2% of the frame.
- Dust specks are sparse, sharp, and single-pixel-ish.
- Motion is slow enough that consecutive frames differ by a few pixels, not by
  a jump.
- Compare with `assets/posters/fractal-drift.jpg`: same two-hue split and the
  same ring scale. Bloom positions depend on the parameter phase and will
  differ.

## 15. Porting notes

Requires highp float: with mediump, the distance estimate at high zoom loses
precision and the contours band visibly. Any complex iteration works; keep the
derivative track — the distance estimate is what makes the edges glow rather
than alias.
