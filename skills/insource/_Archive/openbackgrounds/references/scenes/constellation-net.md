---
id: constellation-net
name: Constellation Net
family: canvas-a1
renderer: canvas2d
poster: assets/posters/constellation-net.jpg
complexity: L
source_lines: 428
dpr_max: 1.5
deps: [simplex-noise]
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Constellation Net

## 1. Identity

Forty-two glowing nodes at three depths drift on gently curving paths and are
joined by thin links wherever neighbours pass within one link radius, making and
breaking small constellations on near-black navy.

## 2. Perceived look

Sparse and crisp. Links are 1.25 px hairlines; stars are soft blooms 5.09–35 px
across with white cores; 90 dust squares of 1.3–2.2 px give the ground a fine
grain. Coverage is roughly 5–9% of the frame, clustered into 6–10 knots of 3–8
nodes separated by long empty gaps. Background is near-black navy lifting to a
blue haze in the upper right and a violet pool lower left. No focal point. At
t = 3 s the knots have translated 40–80 px and kept their shapes.

## 3. Frame anatomy

1. **Sky** — one linear gradient from (0, 0) to (0.4W, H): `#060b1e`, `#04081c`
   at 0.5, `#01030c`; `source-over`, opaque, repainted every frame.
2. **Halo** — additive radial centred (0.74W, 0.2H), radius 0.68·max(W, H):
   `rgba(28, 58, 122, 0.26)` → `rgba(16, 32, 78, 0.1)` at 0.55 → transparent.
3. **Pool** — additive radial centred (0.16W, 0.86H), radius 0.55·max(W, H):
   `rgba(40, 22, 86, 0.2)` → transparent.
4. **Dust** — axis-aligned fill rects, 1.3–2.2 px, in three alpha buckets
   0.4 / 0.6 / 0.8 of `rgba(198, 218, 255)`, additive.
5. **Links** — five batched path strokes, 1.25 px, round caps, additive, stroke
   alpha 0.2011–0.62.
6. **Stars** — one 64 px baked sprite per node, additive, per-node global alpha
   0.32–0.91.
7. **Vignette** — radial `rgba(2, 4, 14, 0)` → `rgba(2, 4, 14, 0.62)`,
   `source-over`, last.

Canvas is created with `alpha: false`, so the host gradient never shows.

## 4. Motion law

Every node advances at a depth-scaled speed: 0.2346 px/frame at depth 0.3,
0.33252 at 0.62, 0.4488 at 1 — 14.08, 19.95 and 26.93 px/s at 60 fps. Heading is
the node's fixed `dir` plus `sway` times the noise sample, which allows ±2.639
rad of wander around that heading. Nodes wrap: leaving the box by more than
24 px teleports them by W + 48 or H + 48, so the population is conserved and
nothing respawns. Brightness pulses per node at 0.011–0.031 rad/frame, a period
of 202.7–571.2 frames (3.38–9.52 s). Links are rebuilt from scratch every frame.
There is no loop and no lifetime; motion is open-ended.

## 5. Technique and math

Two systems share a frame.

Linking is a uniform spatial hash with cell size `linkDist = 1.24·√(A/n)`:
96.809 px at 640x400 (n = 42), 108.069 px at 1920x1080 (n = 273). Each cell
tests its members and the four half-neighbourhood cells (+1, 0), (−1, +1),
(0, +1), (+1, +1), so no pair is tested twice. A pair links below
`linkDist·(0.62 + 0.38·(d_a + d_b)/2)`: 71.06 px for two depth-0.3 nodes,
96.81 px for two depth-1 nodes, at 640x400. Normalized falloff `1 − dist/span`
selects one of five buckets with stroke alpha `0.16 + 0.46·t^1.5` at t = 0.2 … 1,
giving 0.2011, 0.2764, 0.3738, 0.4891, 0.62. The constant is worth noting:
`1.24·√(A/n)` is 2.48× the mean nearest-neighbour distance of a Poisson field,
which is why the net clumps instead of covering evenly.

Drift samples 2D simplex noise (gradient variant, −1..1) at
`(x·0.0016 + seed, y·0.0016 + frame·0.0019)`. One cell is 625 px and the second
argument slides 0.0019 units per frame, so the heading field breathes without a
third noise axis.

Drawn diameter is `size·7.4·clamp(pulse, 0.35, 1.35)` with
`size = rand(1.35, 2.25) + depth·2.05` and
`pulse = 0.62 + 0.38·sin(frame·pulseSpeed + phase) + 0.1·sin(frame·pulseSpeed·2.7 + seed)`.
Alpha is `clamp(0.3 + depth·0.55·pulse, 0.28, 0.95)`. A node uses the flare
sprite when born with `flare` (depth 1, 50% chance — 9% of all nodes) and its
pulse exceeds 0.8. Size and alpha ride the same pulse, so a node brightens by
growing rather than through a separate opacity animation; the flare swap is the
only discontinuity in a node's life.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | device-pixel-ratio clamp | L |
| nodeArea | 7600 | 5000–11000 | canvas area per node; count = area / nodeArea | H |
| minNodes | 42 | 24–60 | floor for small surfaces | H |
| maxNodes | 460 | 300–700 | cap for large surfaces | L |
| linkSpan | 1.24 | 1.1–1.4 | link radius as √(A/n) multiple; below 1.1 the net breaks | H |
| linkWidth | 1.25 | 0.8–2 | link stroke width in CSS px | M |
| linkAlpha | [0.16, 0.62] | 0.08–0.8 | nearest/farthest bucket opacity | M |
| linkBuckets | 5 | 3–8 | discrete link alpha steps | L |
| dustArea | 2900 | 1500–6000 | area per dust speck; 90 at 640x400 | M |
| dustBuckets | 3 | 1–4 | dust alpha tiers, 0.4 to 0.8 | L |
| drift | 0.34 | 0.15–0.6 | base node speed px/frame | M |
| sway | 0.42 | 0.15–0.7 | noise→heading gain; ±2.639 rad at 0.42 | H |
| noiseScale | 0.0016 | 0.0008–0.003 | inverse noise cell; 625 px cells | M |
| timeScale | 0.0038 | 0–0.008 | field evolution per frame (halved into y) | L |
| starGlow | 7.4 | 5–10 | sprite-size multiplier on node size | H |
| vignette | 0.62 | 0.4–0.8 | corner darkening alpha | M |
| warmup | 120 | 60–300 | hidden frames before first paint | M |

## 7. Palette and color

Sky `#060b1e` (≈ hsl(227.5, 66.7%, 7.1%)), `#04081c` (≈ hsl(230, 75%, 6.27%)),
`#01030c` (≈ hsl(229.1, 84.6%, 2.55%)). Haze `rgba(28, 58, 122, 0.26)`; pool
`rgba(40, 22, 86, 0.2)`; dust and links `rgba(198, 218, 255)` /
`rgba(186, 214, 255)`, ≈ hsl(218.9, 100%, 88.8%) and hsl(215.7, 100%, 86.5%).
Star stops run white → `rgba(238, 247, 255, 0.94)` at
0.09 of radius → `rgba(186, 216, 255, 0.44)` at 0.22 → `rgba(140, 178, 240,
0.14)` at 0.46 → `rgba(120, 160, 230, 0)` at 1. Flare spikes add
`rgba(226, 240, 255, 0.7)` falling to zero over 32 px. Coloured stops span hue
208–257; only the sprite core is pure white. Additive overlap pushes crossings
toward pale blue-white. Display sRGB throughout, no tonemapping.

## 8. Composition and camera

No camera, full-bleed orthographic. Count and link distance both derive from
area, so clump scale stays roughly constant in pixels while the frame grows: one
link spans 15.1% of the width at 640x400 and 5.6% at 1920x1080, so bigger frames
read sparser. The haze and pool sit at fixed relative positions (74%/20%,
16%/86%) independent of aspect. No safe margins; the 24 px wrap pad is the only
edge allowance. Very tall frames hit the 460 cap and the link distance grows.

## 9. Randomness and seeds

`Math.random()`, no seed; any seed gives the same distribution. Depth is 0.3 /
0.62 / 1 with probabilities 0.44 / 0.38 / 0.18; position is uniform over the
viewport; `seed` is uniform 0–640; `dir` uniform 0–2π; size, pulse speed and
phase are uniform in their ranges. Dust level is `floor(u^1.6·3)`, which puts
50.4% of specks in the dimmest bucket. Warmup: 120 frames.

## 10. Performance budget

42–273 nodes, 90–715 dust rects, five stroke calls, one sprite draw per node,
four full-screen gradient fills (sky, halo, pool, vignette). The 640x400 poster
costs 42 sprite blits; 1080p costs 273. DPR capped at 1.5. Measured class: 60 fps
at 1080p on a laptop iGPU. Cut order: dust count, then node count, then
`starGlow`, then merge the pool gradient into the sky.

## 11. Host integration

Standard contract. Sprites are baked at mount before the first resize; the
context is created with `alpha: false`; `lineCap` is set to round inside resize.
Resize re-derives width and height, rebuilds the backing store, then reruns the
scene builder — which re-randomizes every node and speck, so the net visibly
re-deals. A passive window resize listener is the only event. Teardown cancels
the RAF, removes the listener, stops the meter and drops nodes, dust, the grid
and the five path objects.

## 12. Failure modes and tells

- **Uniform grey web** → link span not depth-modulated; restore the 0.62–1.0
  pair factor.
- **Isolated dots, no net** → link distance from a fixed pixel value instead of
  √(A/n), or the 42-node floor missing at thumbnail size.
- **Blobs instead of pinpricks** → `starGlow` above 7.4, or the sprite's last
  stop above alpha 0.
- **Milky blue wash** → halo and pool painted `source-over`; both need `lighter`.
- **Corners never darken** → vignette inherited the link pass's additive
  composite.
- **Links flicker** → full neighbourhood tested, so pairs land in two buckets;
  use the four half-offsets.
- **Seam at left/right edges** → nodes wrap on a torus but links do not.
- **No flares** → three gates: depth 1, 50% birth roll, pulse above 0.8.

## 13. Tuning knobs

1. `nodeArea` — lower for a denser net (5000–5600).
2. `linkSpan` — 1.15 for tighter knots, 1.35 for one connected web.
3. `linkAlpha` upper bound — 0.4 faint, 0.8 bright.
4. `starGlow` — 5 for pinpricks, 9 for blooms.
5. `dustArea` — 4000 for a cleaner sky, 1500 for visible grain.

## 14. Verification checklist

- 42 nodes at 640x400, 273 at 1920x1080.
- No link longer than 96.809 px at 640x400 (108.069 px at 1080p).
- Background between rgb(1, 3, 12) and rgb(6, 11, 30): navy, never `#000`.
- Coverage 5–9% with 6–10 separate knots of 3–8 nodes.
- Dominant hue 216–230; no green or red anywhere.
- Node brightness varies independently, periods 3.38–9.52 s.
- Compare to `assets/posters/constellation-net.jpg`: same knot size, link
  hairline weight and smoothness. Positions differ.

## 15. Porting notes

Without Path2D, keep the five alpha passes but begin and stroke each bucket
separately, or the per-bucket alpha collapses to one. Bake both sprites at 64 px
once. If the framework's noise is not continuous and in −1..1, the sway turns
into visible heading steps.
