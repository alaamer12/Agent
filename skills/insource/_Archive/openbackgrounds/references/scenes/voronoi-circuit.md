---
id: voronoi-circuit
name: Voronoi Circuit
family: webgl-f1
renderer: webgl1
poster: assets/posters/voronoi-circuit.jpg
complexity: M
source_lines: 331
dpr_max: 1.5
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Voronoi Circuit

## 1. Identity

A blue cellular lattice fills a near-black ground; every cell boundary is a
glowing trace, pulses run along individual edges, and sparse square pads and
flickering dots mark selected cells.

## 2. Perceived look

Smooth, faceted cells 53.3333 px across at 640x400, drawn as 1.6 px cyan-blue
boundaries with a 7 px halo. Interiors are a blue-black wash with a soft centre
bevel; some carry a thin square pad outline. Edges are crisp with a luminous
falloff. Contrast is high on traces and low in fills, with no focal point, only
travelling pulse beads. At t = 3 s the frame is full-bleed.

## 3. Frame anatomy

1. **Ground** — flat deep color `#020307`, no gradient.
2. **Cell wash and bevel** — per-cell tint from the node hash, plus a soft centre
   bevel, both additive.
3. **Edge traces** — gaussian core on the F2 - F1 boundary, gain scaled by pulse.
4. **Halos** — a 7 px exponential skirt at 0.22, under every trace.
5. **Pulses** — narrow bright beads travelling along the trace, added to the
   same edge term.
6. **Nodes and pads** — flickering dots in 12% of cells, square outlines in 45%.
7. **Tonemap and vignette** — exponential exposure, radial darkening.

One fullscreen triangle, no blend, no depth, no cull; context alpha false, so the
host backdrop is hidden.
## 4. Motion law

The whole lattice creeps left at 0.12 cells/s and up at 0.07 cells/s, i.e.
6.4 px/s and 3.7333 px/s at 640x400, so cells slide rather than boil. The
pointer shifts the sampling by 0.35 cells, at most 18.6667 px. Each feature
point orbits an ellipse of semi-axis 0.38 cells with period 19.042 s; the
swapped hash components give the two axes different phases. A pulse crest crosses
one cell in 1.49–2.99 s (speed 0.335–0.669 cells/s, 17.867–35.68 px/s by edge
seed), and passes a fixed point every 1.3–2.6 s. Node brightness flickers at
3.1 rad/s, period 2.027 s. No loop.

## 5. Technique and math

The centred coordinate p is divided by the short axis. Lattice space is
q = p * 7.5 + pointer * 0.35 + (0.12 t, -0.07 t); one cell is one unit and a cell
measures wpx = 7.5 / min(width, height) in screen units. For the 3x3
neighbourhood of floor(q), each feature point is cell + 0.5 + 0.38 * sin(0.33 t
+ 2π * swappedHash), where the hash is a sine hash of the integer cell (dot with
127.1/311.7 and 269.5/183.3, then fract(sin(x) * 43758.5453)). The two nearest
distances F1 and F2, with points s1 and s2, come from an insertion pass.

The boundary estimate is edge = (F2 - F1) / 2. The core is
exp(-(edge / (1.6 * wpx))^2), clamped at 1; the halo is 0.22 *
exp(-edge / (7 * wpx)). The travel coordinate is along = dot(f - (s1 + s2) / 2,
bisector), with f the fractional part of q and bisector the unit vector
perpendicular to s2 - s1. With edge seed e, phase = 1.15 * along - 0.55 t *
(0.7 + 0.7 e) and pulse = (0.5 + 0.5 sin(2π phase))^14, gated by e > 0.3.

Nodes use the second hash component of cell + s1 + 4.31: node =
exp(-(F1 / (3.2 wpx))^2) * [seed > 0.88] * (0.55 + 0.45 sin(3.1 t + 20 seed)).
Pads draw when seed > 0.55 as a square outline of half-size 0.2 cells, width
1.3 wpx. Bevel is max(0, 1 - 1.8 F1) / 8.33. Color adds, in order: deep; cell
tint * (seed * 0.35 + 0.2) * (bevel + 0.12); edge color * (trace * (0.55 + 2.6
pulse) + pad + halo); node color * (1.8 node + 1.4 pulse * trace); cell tint *
2 bevel. Tonemap 1 - exp(-1.7 col), then 1 - 0.65 * smoothstep(0.4, 1.15, r).

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | device-pixel clamp | L |
| cells | 7.5 | 4.0–12.0 | cells across the short axis; 53.3333 px at 640x400 | H |
| edgeWidth | 1.6 | 0.8–3.0 | trace half-width in pixels | H |
| haloWidth | 7.0 | 3.0–14.0 | halo half-width in pixels | M |
| pulseFreq | 1.15 | 0.5–2.5 | crests per cell of edge | H |
| pulseSpeed | 0.55 | 0.2–1.2 | bead travel rate | M |
| edgeColor | rgb(0.16, 0.56, 1.0) | hue 205–220 | boundary color | H |
| nodeColor | rgb(0.65, 0.95, 1.0) | hue 185–195 | node and pulse highlight | H |
| cellColor | rgb(0.05, 0.16, 0.4) | hue 215–230 | interior wash | M |
| deep | rgb(0.006, 0.012, 0.028) | near-black | ground | M |
| pointerGain | 0.35 | 0–0.6 | lattice shift, cell units | L |
| drift | 0.12 / 0.07 | 0–0.25 | creep in cells/s, x then y | L |

## 7. Palette and color

Deep is `#020307` (hsl 224, 65%, 2%), cell wash `#0D2966` (hsl 221, 78%, 22%),
edge `#298FFF` (hsl 211, 100%, 58%) and node `#A6F2FF` (hsl 189, 100%, 82%).
Traces are additive over the wash, so junctions and pulses push toward white-cyan
while cell interiors stay navy. All additions happen before the 1 - exp(-1.7 x)
tonemap, which keeps the brightest beads just below clipping. Values are
display-referred sRGB with no gamma conversion.

## 8. Composition and camera

Orthographic and full-bleed. The lattice is square in short-axis units, so at
640x400 it shows 12 cells by 7.5 and cells read square; wide frames simply
reveal more columns, tall frames more rows. There is no horizon or vanishing
point, no safe margin, and the 0.4–1.15 radial vignette darkens the corners by up
to 65%. At 21:9 the cells remain square and the field counts rise to about 17 by
7.5.

## 9. Randomness and seeds

No RNG and no seed. Every cell property derives from the sine hash of integer
lattice coordinates, which is fully deterministic; any launch reproduces the same
lattice at a different phase. Candidate features move on a fixed sine orbit, not
randomly. No warmup: the first frame is already complete. Compare pattern class,
not exact vertices.

## 10. Performance budget

One fullscreen triangle, one draw call, no textures. Per pixel: nine candidate
hashes (each two sine calls), one pass of distance comparisons, four
exponentials. It is ALU-bound rather than fill-bound. 60 fps expected at 640x400
and at 1080p with DPR 1.5. Cut order: DPR, the halo term, the pad outline, then
the candidate loop to five neighbours (which changes cell shape).

## 11. Host integration

Standard contract. WebGL1 context with alpha false, antialias false, depth false
and high-performance preference. Size from the holder with a window fallback,
clamp DPR at 1.5, viewport the backing store. Passive window resize and
pointermove listeners; pointer is window-normalized while the holder stays
pointer-events-none. Time is performance.now() minus a stamp set before the first
RAF. Teardown deletes buffer and program, then calls WEBGL_lose_context. No
assets.

## 12. Failure modes and tells

- **Cells boil instead of sliding →** feature points animated too fast → keep the
  19.042 s orbit and move the lattice by drift.
- **Edges have constant world width →** wpx omitted from the trace width → derive
  it from cells / min resolution.
- **Pulses blink on the whole edge →** phase keyed on time only → key it on the
  bisector coordinate along.
- **A pulse on every edge →** edge-seed gate missing → keep the 0.3 threshold.
- **Squares in every cell →** pad gate inverted → draw only when seed > 0.55.
- **All cells have a bright dot →** node gate missing → keep seed > 0.88.
- **Crawling hash pattern on mobile →** large sine arguments in mediump → keep
  coordinates near the origin.

## 13. Tuning knobs

1. cells — 5.5–10 for cell scale; below 4 the traces merge.
2. edgeWidth — 1.2–2.2; higher turns the lattice into neon tubing.
3. pulseSpeed — 0.3–0.9 for bead cadence.
4. edgeColor — shift hue 205–220 without losing the cyan nodes.
5. haloWidth — 4–10 for a softer or tighter glow.

## 14. Verification checklist

- Short axis shows 7.5 cells; cells are square at every aspect.
- Traces are 1.6 px cores with visible halos, never flat aliased lines.
- Dominant hues 189–224; no green, red, or white-filled cells.
- Beads travel along edges, crossing a cell in 1.49–2.99 s and passing a fixed
  point every 1.3–2.6 s, not blinking in place.
- About 12% of cells carry a node, about 45% a pad outline.
- Compare to `assets/posters/voronoi-circuit.jpg` for cell scale and hue.

## 15. Porting notes

Keep the sine hash exactly; a different hash changes the cell layout but not the
look class. WebGL1 mediump sine loses precision for large cell coordinates, so
wrap the lattice origin. No color management: constants are display-referred.
