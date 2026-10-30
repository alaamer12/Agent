---
id: hologram-scan
name: Hologram Scan
family: webgl-f1
renderer: webgl1
poster: assets/posters/hologram-scan.jpg
complexity: M
source_lines: 333
dpr_max: 1.5
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Hologram Scan

## 1. Identity

Four wireframe radar planes stack in perspective and recede into a dark teal
void, while a bright horizontal scan bar sweeps up the stack.

## 2. Perceived look

Thin cyan lines on near-black, with a red-blue fringe that widens where planes
converge. Each plane carries a square grid, concentric rings and 20 radial
spokes inside a rectangular frame. Density rises toward the horizon where four
sheets overlap; edges are crisp and glowing, the sky empty. A wide gaussian scan
bar crosses every 4.5455 s. At t = 3 s the stack sits in the lower two thirds
and the frame flickers faintly.

## 3. Frame anatomy

1. **Void** — flat deep fill `#020407`, no gradient.
2. **Horizontal haze** — a soft glow rising from the emitter below the stack,
   added at 0.1.
3. **Plane sheets** — four intersect-and-draw planes, each accumulating grid,
   rings, spokes and frame edge into one intensity.
4. **Chromatic composite** — the same field evaluated at three zooms, weighted
   0.52 red, 1.0 green, 1.06 blue.
5. **Scan bar** — screen-space gaussian plus a slower ghost bar, adding cyan.
6. **Flicker and scanline comb** — temporal gain and a 2 px horizontal
   modulation.
7. **Tonemap and vignette** — 1 - exp(-1.8 x), then radial darkening.

One fullscreen triangle, no blend or depth; alpha false hides the host backdrop.

## 4. Motion law

The scan bar rises from y = -0.85 to 0.85 in 4.5455 s (0.22 cycles/s); its ghost
runs at 0.37 times that rate, period 12.2857 s. Planes bob 0.04 units at 0.45
rad/s, period 13.963 s, each offset 1.9 rad. Shimmer modulates each sheet at 0.7
rad/s (8.976 s). The camera sways 0.22 units in x at 0.11 rad/s (57.120 s) and
follows the pointer by 0.18 vertically and 0.1 in depth. Brightness flickers at
41 rad/s and 12.7 rad/s.

## 5. Technique and math

The centred coordinate p is divided by the short axis, then offset by the
pointer times (0.02, 0.015). Three channel passes call one plane function with
zoom 1.006, 1.0 and 0.994. Inside, direction =
normalize(q.x·zoom, q.y·zoom·0.8 − 0.12, 1.4) — the zoom scales only the two
coordinates, not the −0.12 offset — and origin =
(0.22 sin(0.11 t), 1.1 + 0.18 pointer.y, -2.4 - 0.1 pointer.x).

For i = 0 to 3, plane height is y_i = 0.02 + 0.32 i + 0.04 sin(0.45 t + 1.9 i).
A plane is tested only when direction.y < -0.002; hit distance rt = (y_i -
origin.y) / direction.y, accepted for 0.15 < rt < 11.0, and hit point w = origin
+ rt direction. Line half-width is pw = rt * 1.6 / min(width, height).

Each sheet takes a max of four fields: square grid |fract(1.15 w.x) - 0.5| /
1.15 and the same in z; rings on rr = length(w.x, 0.85 w.z) at 1.9 per unit;
spokes from atan2(w.z, w.x) * 20 / 2π, arc distance |fract(a) - 0.5| * (2π / 20)
* rr. Falloff is 1 / (1 + 6 e^4) with e = min(|d| / w, 3). Weights are 1 grid, 0.8 rings, 0.28 spokes. A frame edge at
max(|w.x|, |0.85 w.z|) - 2.6 adds at 0.5 weight and 1.2 width. Sheets attenuate
by exp(-0.34 max(0, rt - 1)) and shimmer by 0.55 + 0.5 sin(0.7 t + 2.1 i).

Scan is screen space: scanY = fract(0.22 t) * 1.7 - 0.85, a 0.045-wide gaussian
(18 px) multiplying channels by 1 + 2.4 scan; a ghost at 0.37 rate adds 0.3.
Haze is max(0, 0.55 - p.y) times a 0.5-wide x gaussian at 0.1. Color is deep +
(0.52, 1.0, 1.06) channels + holo * (0.10 scan + 0.05 ghost), times flicker
0.93 + 0.05 sin(41 t) + 0.04 sin(12.7 t + 1.3) and the comb 0.92 + 0.08 sin(π
y_device), all mediump.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | device-pixel clamp | L |
| gridFreq | 1.15 | 0.7–1.6 | square cells per unit | H |
| ringFreq | 1.9 | 1.1–2.8 | rings per unit | H |
| spokes | 20.0 | 12.0–32.0 | radial wedges | M |
| scanSpeed | 0.22 | 0.1–0.5 | cycles/s; 4.5455 s period | H |
| linePx | 1.6 | 0.8–2.5 | width multiplier by distance | H |
| planeCount | 4 | 2–6 | stacked sheets | H |
| planeStep | 0.32 | 0.2–0.5 | vertical gap | H |
| chroma | 0.006 | 0.0–0.02 | channel zoom spread | M |
| cameraY | 1.1 | 0.7–1.6 | eye height | H |
| verticalSquash | 0.8 | 0.6–1.0 | ray y compression | M |
| atten | 0.34 | 0.1–0.6 | distance falloff | M |
| exposure | 1.8 | 1.2–2.4 | tonemap gain | H |
| pointerGain | 0.02 / 0.015 | 0–0.05 | pointer shift | L |

## 7. Palette and color

Hologram cyan is `#57F2FF` (hsl 185, 100%, 67%) on void `#020407` (hsl 213, 53%,
2%). The three passes are weighted unequally — 0.52 red, 1.0 green, 1.06 blue —
so even an unchanneled line renders cyan and the chromatic split reads as a red
ghost on one side and blue on the other. Everything is added linearly before the
1 - exp(-1.8 x) tonemap, which keeps the scan bar from clipping to flat white.
Values are display-referred sRGB with no gamma stage.

## 8. Composition and camera

Virtual camera at height 1.1, 2.4 units back, 1.4 forward ray component and 0.8
vertical squash. Rays above q.y = 0.15 see no plane, so the top third stays
empty while the sheets fill the lower two thirds and converge there. The short
axis sets scale; wide frames widen the planes and the fringe, tall frames show
more sky. The 0.4–1.15 vignette darkens the corners, leaving the stack as the
only bright mass.

## 9. Randomness and seeds

No RNG, no hash, and no warmup. Plane heights, camera sway, shimmer, flicker and
scan all follow closed-form sinusoids of frame time. Any start time yields the
same stack at a different phase. Keep the 1.9 and 2.1 phase offsets, which stop
the sheets bobbing in unison.

## 10. Performance budget

One fullscreen triangle and one draw call. The fragment pass runs four plane
intersections three times each, twelve ray-plane tests per pixel, plus one
interpolation per channel. No textures, no loops over pixels. Fill-bound and
ALU-moderate. 60 fps expected at 640x400 and at 1080p with DPR 1.5. Cut order:
drop the chromatic split to one pass (four tests), then DPR, then planeCount to
three, then spokes.

## 11. Host integration

Standard contract. WebGL1, alpha false, antialias false, depth false,
high-performance preference. Size from the holder with a window fallback, clamp
DPR at 1.5, viewport the backing store. Passive window resize and pointermove;
pointer is window-normalized while the holder stays pointer-events-none. Time is
performance.now() minus a stamp set before the first RAF. Teardown deletes the
buffer and program and calls WEBGL_lose_context. No assets.

## 12. Failure modes and tells

- **Lines same thickness at every plane →** width not multiplied by hit distance
  → scale by rt as above.
- **Planes fill the upper half →** ray-down test or the 0.12 horizon offset is
  missing → rays with direction.y >= -0.002 must draw nothing.
- **Rainbow ghosting wider than a few pixels →** channel zoom spread above 0.006
  → keep 1.006/1.0/0.994.
- **Scan bar parallaxes with the stack →** it is computed from world depth → keep
  it in screen space.
- **Heavy strobing →** flicker amplitude above 0.09 → keep 0.05 and 0.04.
- **Planes end in a hard edge →** the 2.6 half-extent frame line is missing or
  the rt cutoff is too short.

## 13. Tuning knobs

1. scanSpeed — 0.15–0.35; slower reads as a scanner, faster as a glitch.
2. gridFreq — 0.9–1.4 changes cell density without touching ring scale.
3. linePx — 1.2–2.0; higher turns the stack into neon tubing.
4. chroma — 0.004–0.008; below 0.003 the split vanishes.
5. planeStep — 0.28–0.38 for stack spacing.

## 14. Verification checklist

- Four distinct sheets visible, stacked in perspective, none above the horizon
  line.
- Cyan dominant, red fringe on one side of each line and blue on the other.
- Scan bar crosses the whole frame every 4.5455 s, unaffected by pointer.
- Lines stay roughly one to three pixels wide near and far.
- Compare to `assets/posters/hologram-scan.jpg` for stack height and hue.

## 15. Porting notes

The rational line falloff is a performance substitute for a gaussian; keep its
clamped 1/(1 + 6 e^4) shape rather than swapping in exp, which shifts line
weight. If the framework renders into a linear buffer, apply the tonemap there
but author the constants as display values. Mediump is enough; the only atan2 is
per plane hit.
