---
id: halftone-tide
name: Halftone Tide
family: canvas-a3
renderer: canvas2d
poster: assets/posters/halftone-tide.jpg
complexity: S
source_lines: 243
dpr_max: 1.5
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Halftone Tide

## 1. Identity

A rotated hex lattice of cyan dots on near-black, its radii swelling into broad
tide bands that sweep across the frame.

## 2. Perceived look

A crisp printed screen: hard-edged circular dots, no blur, high contrast between
cyan ink and the `#04060a` ground. Dots run 1.65–5.78 px in radius at 640x400,
spaced 10.33 px apart on a lattice tilted 14.9°. Tone is carried entirely by dot
size. At t = 3 s three or four vertical crest bands are visible, the largest
dots near white-cyan, the troughs nearly bare.

## 3. Frame anatomy

1. **Base fill** — opaque `#04060a` across the frame; there is no clear call,
   this fill is the clear.
2. **Wash** — one diagonal linear gradient from (0, 0) to (W, H):
   `rgba(11, 18, 25, 0.8)`, `rgba(6, 11, 16, 0.35)` at 0.55, `rgba(2, 4, 7, 0.85)`.
3. **Dots** — 20 `Path2D` batches filled `source-over`, each with its own
   `globalAlpha` from 0.5497 to 0.97. Buckets 0–15 use flat
   `hsl(186, 100%, 63%)`; 16–19 use the crest gradient. Canvas alpha is false.

## 4. Motion law

Phases advance on the frame counter, incremented before painting. The sweep
moves 0.0125 rad per frame — a 502.65-frame period, 8.38 s at 60 fps. The ripple
moves 0.0165 (380.75 frames, 6.35 s); the tilt 0.0042 (1495.9 frames, 24.93 s).
The sweep direction rotates 0.00062 rad per frame, one revolution in 10134.4
frames, 168.9 s. The ripple origin walks a Lissajous with periods of 3306.9 and
2444.8 frames (55.1 s and 40.7 s). A 40-frame warmup runs before the first
visible paint. Motion is open-ended.

## 5. Technique and math

Spacing is s = clamp(√(WH/2400), 8.5, 24): 10.3279 px at 640x400, the 24 px cap
at 1920x1080. Rows sit at j·s·0.8660254 with a half-spacing stagger on odd rows,
rotated 0.26 rad about the center. With base = √(WH), each site evaluates:

- travel = sin(((x·dx + y·dy)·2π·2.4/base) − 0.0125·f), (dx, dy) the rotating
  unit direction
- ripple = sin(hypot(x − fx, y − fy)·2π·3.6/base − 0.0165·f), with
  fx = W/2 + 0.36W·cos(0.0019f) and fy = H/2 + 0.33H·sin(0.00257f)
- tilt = sin(((x/W) − 0.55·(y/H))·1.1·2π + 0.0042·f)
- h = clamp(0.5 + 0.5·(0.52·travel + 0.3·ripple + 0.18·tilt), 0, 1), then
  h ← h²(3 − 2h)
- r = s·(0.16 + 0.4·h^1.35), bucket = floor(20·h), clamped to 19

The sweep is a plane wave of wavelength √(WH)/2.4 — 210.79 px at 640x400, 20.41
dot spacings. The ripple is circular at √(WH)/3.6, 140.53 px. The tilt adds 1.1
cycles across the width with 0.55 of that frequency along height, so the field
never reads as concentric rings. Because coverage follows r², the tone curve is
effectively h^2.7. Crest dots overlap their neighbours by 12% (0.56·s against a
0.5·s touch radius); trough dots cover 9.3% of their cell.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | DPR clamp | L |
| cells | 2400 | 1200–4000 | dot density; s = √(WH/cells) | H |
| minSpacing / maxSpacing | 8.5 / 24 | 6–12 / 18–32 | small and large frame bounds | M |
| gridAngle | 0.26 rad | 0–0.6 | lattice rotation | H |
| minRadiusFactor / maxRadiusFactor | 0.16 / 0.56 | 0.08–0.25 / 0.4–0.62 | trough and crest size | H |
| buckets | 20 | 8–32 | alpha steps | M |
| crestBuckets | 4 | 0–8 | gradient-painted buckets | M |
| sweepWaves / sweepSpeed | 2.4 / 0.0125 | 1.2–4 / 0.004–0.03 | plane wave | H |
| rippleWaves / rippleSpeed | 3.6 / 0.0165 | 1.5–6 / 0.004–0.04 | circular wave | H |
| tiltWaves / tiltSpeed | 1.1 / 0.0042 | 0.5–2 / 0–0.01 | diagonal asymmetry | M |
| rotateSpeed | 0.00062 | 0–0.002 | sweep spin | M |
| inkHue | 186 | 150–220 | ink color | H |
| inkLight | 63% | 45–80% | ink lightness | M |
| alphaRange | [0.5, 0.97] | 0.3–1 | dot opacity range | M |
| warmup | 40 frames | 0–120 | hidden phase advance | M |

## 7. Palette and color

Ink is `hsl(186, 100%, 63%)` — rgb(66, 236, 255), `#42ecff`. The crest gradient
runs `hsl(186, 100%, 63%)` → `hsl(198, 100%, 84%)` (`#80f9ff`) at the midpoint
→ `hsl(180, 100%, 68%)` (`#5cffff`), oriented along the sweep over ±0.6·√(WH).
Ground: `#04060a` with the diagonal wash above. Per-bucket alpha is
0.5 + 0.47·((b + 1)/20)^0.75, so 0.5497 to 0.97. All values are display sRGB.

## 8. Composition and camera

Full-bleed, no camera, lattice anchored at the frame center. Dot scale is
area-derived, so the pattern reads at one physical size until a clamp engages:
at 1920x1080 spacing hits the 24 px cap and the frame holds 4,157 larger dots
instead of 2,772. Wide frames keep 3.0–3.2 sweep wavelengths across the width
because the wave count is per √area. Portrait frames add rows, not bands.

## 9. Randomness and seeds

None. No RNG and no seed anywhere: every dot position and radius is a pure
function of frame index and coordinates, so two runs at the same frame are
pixel-identical. The 40-frame warmup is the only priming; it steps off the
aligned standing pattern at f = 0.

## 10. Performance budget

18,705 lattice sites are tested per frame at 640x400 and 2,772 drawn; the 1080p
frame draws 4,157. Cost is 20 Path2D allocations, 2,772 move-and-arc appends and
20 fills, plus one full-frame gradient. Dot area peaks at 0.29 MPx, so path
appends dominate. DPR 1.5. Cut order: buckets, cells, DPR.

## 11. Host integration

Mount creates the opaque context, resizes (deriving spacing and allocating the
20 paths), runs 40 synchronous drawFrames, adds a passive window resize
listener, starts the meter and the RAF. Resize re-derives spacing and rebuilds
paths but keeps the frame counter, so the tide does not jump. Teardown removes
the listener, cancels the frame, stops the meter and drops the paths and
context. No ResizeObserver.

## 12. Failure modes and tells

- **Lattice reads as a spreadsheet →** gridAngle 0 or the odd-row stagger lost.
- **Dots fuse into blobs →** maxRadiusFactor above 0.56 at this spacing.
- **Flat mid-tone field →** wave weights unbalanced or h not re-centred on 0.5.
- **Visible 20-step alpha rings →** buckets lowered below 12.
- **Dots clipped at the border →** the maxRadius·1.6 cull margin removed.
- **Frame opens on a standing wave →** warmup skipped; every phase is zero at
  t = 0.
- **No near-white crest →** crestBuckets 0, or peak h never exceeds 0.8.

## 13. Tuning knobs

1. `cells` — 1800 for bigger dots, 3200 for a finer screen.
2. `maxRadiusFactor` — 0.5 for airier gaps, 0.6 for solid crests.
3. `sweepWaves` — 3.2 for tighter bands, 1.8 for broad ones.
4. `inkHue` — 200 for colder blue, 170 for a greener sea.

## 14. Verification checklist

- Lattice tilted 0.26 rad; 2,772 dot sites at 640x400.
- Radii between 1.65 and 5.78 px; no dot exceeds 0.56·s.
- Dominant hues 180–198; no warm pixels.
- At least one crest per revolution reaches `#80f9ff`.
- Sweep period 8.38 s; no flicker or per-frame jitter.
- Compare with `assets/posters/halftone-tide.jpg`: the scene is deterministic,
  so the same frame index reproduces the poster exactly.

## 15. Porting notes

Batch dots per bucket rather than per dot; a per-dot fill cannot hold 60 fps.
No filters or blend modes are needed. Keep the frame counter, not wall time, or
the phases break.
