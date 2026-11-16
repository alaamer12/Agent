---
id: warp-field
name: Warp Field
family: webgl-f3
renderer: webgl1
poster: assets/posters/warp-field.jpg
complexity: L
source_lines: 435
dpr_max: 1.5
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Warp Field

## 1. Identity

Two and a half thousand stars rush outward from a small empty vanishing point,
each drawn as a thin blue-white streak with a bright head, the whole field slowly
rolling.

## 2. Perceived look

Sharp, high-contrast radial motion in the style of a jump to hyperspace. Lines
are one pixel wide at the center and fan out, thickening and stretching toward the
frame edges. Heads are tiny hot points with a soft halo, mostly blue-white with
a few warm amber ones. The center 5% of the frame is a clean black hole where
nothing is drawn. Density is highest at mid-radius, sparsest at the corners.
Background is near-black navy. At 3 s, everything reads as streaks rather than
dots — faster than a starfield, slower than a full warp flash.

## 3. Frame anatomy

Two draw calls, both from static buffers, both additive (`SRC_ALPHA, ONE`), both
depth-test-free with depth writes off. The buffer is cleared to
`rgb(0.004, 0.007, 0.018)`.

1. **Clear** — near-black navy.
2. **Streaks** — 2600 line segments (5200 vertices), alpha 0.52, one-pixel-wide
   GL lines, colored by depth.
3. **Heads** — 2600 point sprites, alpha 0.9, sized up to 30 px, with a core plus
   halo falloff.

Canvas is opaque (`alpha: false`, `antialias: true`). No host backdrop shows.
Additive order does not matter; heads are drawn last only by convention.

## 4. Motion law

A star's phase is `fract(seedDepth − 0.2 t)`, so every star travels the depth
span 0.42…3.6 and wraps at the near end. The phase advances at 0.2 cycles/s, so
one crossing takes `1/speed` = 5 s (the 3.18-unit span moves under it at an
average 0.636 units/s, not 0.2). Because all phases are uniformly distributed,
the population is steady — there is no visible respawn moment. The projection
divides twice, so screen radius is ∝1/z² and screen speed grows roughly as 1/z³:
a star that takes seconds to cross the middle blinks past the edge in a few
frames. The whole cylinder
rolls at 0.02 rad/s plus a 0.28 rad swell with a 153.2 s period, and the viewpoint
drifts on two summed sines per axis (amplitudes 0.075 and 0.034 in x, 0.06 and
0.027 in y; periods 114.2, 278.3, 165.4, 262.5 s). Open-ended, no loop.

## 5. Technique and math

**Data.** 2600 stars, each 5 floats: `(x, y, depthSeed, starSeed, tail)`. The line
buffer duplicates each star with `tail = 0` and `tail = 1`; the head buffer holds
one copy. Stars are seeded on a disc: angle uniform, radius
`1.75 · u^0.62` (denser at the axis than a uniform disc), so the density on screen
falls off toward the edges after perspective.

**Per-vertex motion.** `phase = fract(depth − 0.2 t)`,
`z = 0.42 + phase · 3.18 + tail · 0.2`. The tail vertex sits 0.2 world units
farther away, so the segment is a radial streak whose on-screen length is
proportional to `1/z²` — that inverse-square is why near stars streak hardest.
Positions rotate by `roll = 0.02 t + 0.28 sin(0.041 t)`, then subtract the drift
offset; that is a camera drift, not star motion. Projection is the family's
inverse-square form: the shader writes `gl_Position = (xy·focal/z, 0, z)`, and
because clip w is also z the hardware divides a second time — the final screen
radius is `xy·focal/z²`, with `focal = (1.18/aspect, 1.18)`. The pre-divide
`xy·focal/z` is what feeds the hole test. Note the head
and both tail vertices project with the same `x, y`, so the line is always
exactly radial in NDC — a screen-space trick, not true 3D orientation.

**Color.** `depthT = (z − 0.42)/3.18`, `col = mix(hot, deep, depthT^0.7)` with
hot `(0.9, 0.96, 1.0)` and deep `(0.12, 0.3, 0.88)`: arrivals are white, departures
blue. 4.2% of stars (`step(0.958, starSeed)`) mix 80% toward amber
`(1.0, 0.74, 0.5)`. Alpha is `(1 − 0.9 depthT) · emerge · sparkle`, where
`emerge = smoothstep(0.05, 0.2, |ndc|)` suppresses the vanishing point and
`sparkle = 0.45 + 0.85 fract(7.13 starSeed)` gives per-star brightness.

**Heads.** World radius `0.022 (0.62 + fract(3.71 starSeed))`, converted to
pixels by `size · focal_y · height · 0.5 / max(z, 0.3)` and clamped to 1–30 px.
The fragment keeps a disc, `k = 1 − 2d`, `halo = k^2.4`, `core = k^9`, adds
`(0.82, 0.9, 1.0) · core`, and multiplies alpha by `0.2 + 0.8 halo`. The core
term is what survives additive blending as a pinpoint.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | resolution clamp | L |
| seed | 20260922 | any | star layout | M |
| stars | 2600 | 800–6000 | density | H |
| speed | 0.2 | 0.05–0.6 | phase cycles/s; one crossing per 1/speed = 5 s | H |
| near | 0.42 | 0.25–0.8 | closest depth; controls max streak | H |
| far | 3.6 | 2.0–6.0 | far depth | M |
| spread | 1.75 | 1.0–3.0 | cylinder radius | M |
| focal | 1.18 | 0.8–1.8 | how wide the field fans | H |
| streak | 0.2 | 0.05–0.5 | world-space tail length | H |
| lineStrength | 0.52 | 0.3–0.8 | streak alpha | M |
| headStrength | 0.9 | 0.5–1.0 | head alpha | M |
| headSize | 0.022 | 0.01–0.04 | head world radius | M |
| hole | 0.05 | 0.02–0.12 | cleared radius at the vanishing point | H |
| driftX / driftY | 0.075 / 0.06 | 0–0.15 | camera sway amplitude | L |
| driftRateX / driftRateY | 0.055 / 0.038 | 0.01–0.1 | sway frequencies, rad/s | L |
| rollRate | 0.02 rad/s | 0–0.06 | constant roll | L |
| rollSwell | 0.28 | 0–0.5 | rolling oscillation | L |
| radial bias | 0.62 | 0.4–1.0 | inner density vs uniform disc | M |
| warm fraction | 0.042 | 0–0.1 | amber star share | L |

## 7. Palette and color

Hot `#E6F5FF`, deep blue `#1F4DE0`, amber `#FFBD80`, ground `#010205`. Values
are display-space and additively summed; overlaps white out, so the center
becomes dense without any tone mapping. Alpha carries the depth cue, not color:
near stars are both whiter and more opaque. There is no vignette — the frame
edges stay as bright as the stars there, which is part of the speed feel.

## 8. Composition and camera

Radial composition centered on the vanishing point at the frame center; `focal`
1.18 and normalization by aspect keep the fan circular at any size. At 640x400
the field covers every pixel outside the 5% clear hole. Ultra-wide aspect shows
longer streaks at the left and right edges because a star exits later; tall
aspect does the same vertically. There is no depth of field and no near clipping
artifact — `z` is floored at 0.001 only for the divide, and stars are hidden by
the hole before they reach it.

## 9. Randomness and seeds

mulberry32, seed 20260922, drawn in a fixed order (angle, radius, depth, seed per
star), so the layout is identical every run. Radius bias `u^0.62` and uniform
angle. No warmup: phases are uniformly distributed at t = 0 by construction, so
the first frame is at full density.

## 10. Performance budget

Two draw calls: 5200 line vertices and 2600 point sprites. GL lines are cheap;
the cost is the head overdraw, which at 30 px max is small. 60 fps at 1080p on
integrated graphics; this is one of the cheapest scenes in the gallery. Cut
order: DPR, head size clamp, star count.

## 11. Host integration

Standard contract, no pointer input and no external assets. Resize recomputes
buffer size, viewport, and focal x by aspect. Teardown deletes both buffers, both
programs, and loses the context; note that both programs share one vertex shader
source and differ only in the fragment stage.

## 12. Failure modes and tells

- **Dots instead of streaks →** `streak` near zero, or the two tail vertices
  carry the same depth.
- **Streaks point randomly instead of radially →** the tail vertex is offset in
  x/y as well as z; the original keeps x/y equal so lines are radial in NDC.
- **Visible warp flash each loop →** phases are not uniform at t = 0; the
  `fract(depth − speed t)` form avoids this, a per-star timer does not.
- **Center is crowded →** hole radius too small, or `emerge` removed.
- **Everything is blue with no white arrivals →** the depth color mix is
  inverted or `depthT` computed from `1 − phase`.
- **Streaks vanish near the camera →** `near` too small; the divide blows the
  line past the clip plane.
- **Whole field judders →** using `Date.now()` instead of the RAF timestamp;
  the original is smooth only with monotonic time.
- **Line thickness varies wildly →** GL line width is set per draw; the original
  leaves it at 1 px, which is the only reliable value across GPUs.

## 13. Tuning knobs

1. `speed` — glide versus hyperspace (0.1–0.35).
2. `streak` — dot-like versus full comet tails (0.1–0.35).
3. `focal` — narrow tunnel versus wide fan (0.9–1.5).
4. `stars` — sparse versus dense (1500–4000).
5. `hole` — tight clean point versus a visible void (0.03–0.09).

## 14. Verification checklist

- A clean black hole at frame center, no streaks crossing it.
- Lines strictly radial, all converging on that hole.
- Streak length grows toward the edges.
- Heads visible as distinct points at the far ends of lines.
- Mostly blue-white; a handful of amber stars.
- No flicker or popping as stars wrap; density steady.
- Compare with `assets/posters/warp-field.jpg`: same fan density and streak
  length; angular positions differ only through the slow roll.

## 15. Porting notes

The vertex shader needs `highp`: the phase is a `fract` of elapsed time, and
mediump quantizes it into visible stutter after a few minutes. In three.js, use
`LineSegments` plus `Points` with two `ShaderMaterial`s sharing one vertex shader;
`gl_PointSize` must be written manually because three.js's default size
attenuation is different.
