---
id: field-lines
name: Field Lines
family: webgl-f4
renderer: webgl1
poster: assets/posters/field-lines.jpg
complexity: XL
source_lines: 698
dpr_max: 1.5
deps: []
poster_capture: 640x400
---

# Field Lines — scene reference

## 1. Identity

A teal magnetic-dipole diagram: nested families of field-line arcs sweeping out of a glowing sphere, with bright particle "charges" pooling at the poles, drifting through faint dust on near-black.

## 2. Perceived look

A luminous scientific instrument — think a plasma globe or an auroral magnetosphere staged as a textbook cutaway. The arcs are the structure: thin, cool teal, drawn as discrete polylines whose brightness pulses along their length in soft travelling bands, so the apparatus looks energised rather than static. Near the poles the arcs converge into two bright, fuzzy caps where hundreds of charge sprites pile up; the caps are near-white mint, and they are the brightest thing in the image. The graticule sphere at the centre is barely visible — a faint wireframe globe reading as the source body. Around everything, large, low-alpha dust sprites give a milky teal haze that lifts the black background to a deep sea-green. Contrast is high but soft: no hard edges except the arc polylines, which alias slightly. The 3 s screenshot shows a small, bright mint core wrapped in a cage of teal loops on a black field with a faint haze halo.

## 3. Frame anatomy

Back to front:

1. **Clear colour** — `(0.002, 0.011, 0.013)` at alpha 1; canvas opaque, so the parent backdrop never shows.
2. **Dust** — 800 large point sprites authored in *view* space (not rotated with the apparatus), spread ±11.5 × ±7.0 in x/y around z ≈ −1…1; additive, per-sprite alpha ≈ 0.014–0.095 after `dustAlpha` 0.4, sizes up to 90 px at high resolution.
3. **Far field arcs** — dipole arcs behind the mid-depth, faded by `(1−smoothstep(8.4,16.6,w))^1.5`; alpha ≈ 0.19–0.55 × pulse (0.35–1.35).
4. **Graticule** — 5 meridians + 4 parallels on the 1.0-radius sphere, plus a straight 3.4-unit dipole axis; alpha 0.14, no pulse, colour a darker teal.
5. **Near field arcs** — same geometry at full fade; alpha ≈ 0.55 × pulse.
6. **Charges** — 1500 orbiting sprites + 340 "oval" sprites hugging the sphere; per-sprite alpha `bright × (0.45 + 0.95·pool)` and colour hot→pole mint; sizes 1–90 px, gl.POINTS additive.

Two draw calls: one `gl.LINES` for arcs/graticule, one `gl.POINTS` for charges+dust. No depth buffer, no depth writes, additive `SRC_ALPHA, ONE`, MSAA on.

## 4. Motion law

- **Swing.** Each charge's polar angle is `θ = 90° + (90° − foot)·sin(ωt + φ0)` — a sine between the two mirror points, so speed is zero at the poles and the population naturally pools into bright caps. `ω = (0.10…0.34)·(2.4/L)` rad/s; for a mid-shell L ≈ 2.6 that is 0.092–0.314 rad/s ⇒ periods ≈ 20–68 s.
- **Azimuth drift.** `φ = φ0 + t·0.03·(0.4 + r)`, i.e. 0.012–0.030 rad/s — a slow E×B-style carry; one revolution takes 3.5–8.7 minutes.
- **Apparatus rotation.** `rotX(0.36 + 0.05·sin(0.05t))·rotY(0.07t)`. Yaw period 89.8 s; pitch oscillates ±0.05 rad about 0.36 rad with period 125.7 s.
- **Arc pulse.** Brightness bands travel along each arc: `sweep = 0.5 + 0.5·sin(3.2·θ − 0.7t + 2.4·L)`. With 3.2 rad per radian of polar angle, roughly 1.5 bands fit along a half-arc; the 0.7 rad/s temporal term moves them poleward at about 0.22 rad/s of polar angle.
- **Dust twinkle.** `0.55 + 0.45·sin(2.1t + 41r)` per sprite — period ≈ 3.0 s, decorrelated across the field.
- **Phase at t = 0.** Orientation is rotX(0.36)·rotY(0); each charge starts at `sin(φ0)` on its swing, so the caps are unevenly filled at first and even out within one swing period. Open-ended.

## 5. Technique and math

All geometry is CPU-built once and uploaded; only the vertex shaders animate.

- **Dipole arcs.** A magnetic dipole field line satisfies `r = L·sin²θ`. For shell `s` of 7, `L = 1.35 + (4.8 − 1.35)·s/6`. Each line is truncated where it re-enters the core sphere: `foot = asin(√(core/L))`, then `θ` sweeps `foot → π − foot` in 52 samples (51 segments). 12 longitudes per shell ⇒ 7 × 12 × 51 = **4284 segments**. Point: `(r sinθ cosφ, r cosθ, r sinθ sinφ)` with φ the longitude.
- **Graticule.** 5 meridians (half-circles every 36° of azimuth) and 4 parallels (rings at θ = π/5, 2π/5, 3π/5, 4π/5), each sampled at 45 points (44 segments) on the radius-1 sphere ⇒ 396 segments. Plus a single dipole-axis segment from y = −1.7 to +1.7.
- **Line data.** 7 floats/vertex: position xyz, then `L`, `θ`, unused, `kind` (0 arc, 1 graticule, 2 axis). Vertex shader rotates with the shared `toCamera` (rotX(tilt + swell·sin 0.05t) · rotY(0.07t)), then `w = max(q.z + 11, 0.05)`, `gl_Position = (q.xy·focal/w, 0, w)` — the same inverse-square double divide as the other f4 scenes. Fade `(1 − smoothstep(8.4, 16.6, w))^1.5`. Colour lerps arc→darker guide by `step(0.5, kind)`; alpha = fade × (0.55 arc / 0.14 guide) × (0.35+sweep for arcs, 1.0 for guides).
- **Charges.** 11 floats: `L, φ0, ω, phase` + `r1, brightness, size, isDust` + view-space dust xyz. `foot = asin(√(core/L))`; `θ = π/2 + (π/2 − foot)·sin(ωt + phase)`; `r = L sin²θ`; pos as above. `φ = φ0 + t·0.03·(0.4 + r1)`.
- **Dust.** `q = mix(rotated(p), dustPos, isDust)` — dust is stored directly in view space so it does not rotate with the apparatus.
- **Charge shading.** `pool = smoothstep(0.5, 1, |sin(ωt+phase)|)` (1 near the poles); `fade = (1 − smoothstep(8.4,16.6,w))^1.35`; `bright = brightness·fade·(0.45 + 0.95·pool)`; `haze = brightness·fade·twinkle·0.4`; alpha = `mix(bright, haze, isDust)`; colour `mix(hot, pole, pool)`.
- **Sprite.** `gl_PointSize = clamp(size·focal·height·0.5/max(w,0.4), 1, 90)`; fragment disc `k = 1 − 2d`, halo `k^2.2`, core `k^12` added as `(0.9, 1.0, 0.95)`, alpha `v_alpha·1.25·(0.12 + 0.88·halo)`.
- **Sizing.** `focal = 15.6·min(1, aspect/1.6)`; the outermost shell spans `w ≈ 11 ± 4.8`; composition is set by `lMax·focal/distance² = 4.8·15.6/121 = 0.619` of the shorter axis.

## 6. Parameters

| name | value | range | effect | sensitivity |
|---|---|---|---|---|
| `maxDpr` | 1.5 | 1–2 | device-pixel cap; arcs are 1 px lines | M |
| `seed` | 20260927 | any u32 | charge positions, sizes, rates, dust | M |
| `core` | 1.0 | 0.6–2.0 | radius of the source sphere; truncates arcs | H |
| `shells` | 7 | 3–12 | number of nested field-line families | H |
| `lMin` / `lMax` | 1.35 / 4.8 | 1.1–2 / 3–7 | inner/outer dipole scale; `lMax` sets frame coverage | H |
| `longitudes` | 12 | 6–24 | meridians of the arc fan (×`arcSamples`) | M |
| `arcSamples` | 52 | 24–96 | polyline smoothness per arc | M |
| `meridians` / `parallels` | 5 / 4 | 3–8 / 2–6 | graticule density | L |
| `graticuleSamples` | 44 | 24–64 | segments per graticule circle | L |
| `charges` | 1500 | 500–4000 | orbiting sprites | H |
| `ovalCharges` | 340 | 100–800 | sprites hugging the footpoint rings | M |
| `dust` | 800 | 200–2000 | broad haze sprites | M |
| `swingMin` / `swingMax` | 0.10 / 0.34 | 0.05–0.6 | pole-to-pole angular speed (×2.4/L) | H |
| `driftRate` | 0.03 | 0–0.1 | azimuthal carry of the charge cloud | M |
| `spin` | 0.07 | 0.02–0.2 | steady yaw rate (rad/s) | M |
| `tilt` / `tiltSwell` | 0.36 / 0.05 | 0.2–0.7 / 0–0.15 | resting pitch and its slow oscillation | M |
| `focal` / `refAspect` | 15.6 / 1.6 | 10–24 / 1.2–2 | zoom via inverse-square projection; shrinks by aspect/refAspect on narrow frames | H |
| `distance` | 11.0 | 7–16 | camera offset; sets both scale and depth range | H |
| `depthNear` / `depthFar` | 8.4 / 16.6 | 6–12 / 14–22 | fade window on `w` | M |
| `arcBrightness` / `graticuleBrightness` | 0.55 / 0.14 | 0.2–0.9 / 0.05–0.3 | line alpha | H |
| `pulseRate` | 0.7 | 0.2–2.0 | speed of the travelling arc band | M |
| `chargeStrength` / `dustAlpha` | 1.25 / 0.4 | 0.6–2 / 0.1–0.8 | sprite alpha multipliers | H |

## 7. Palette and color

Clear `ground` `#010303` (0.002, 0.011, 0.013). Arc teal `#24A894` (0.14, 0.66, 0.58); graticule `#1D897A` (arc×0.6 + (0.03, 0.14, 0.13)); charge hot `#73FFD1` (0.45, 1.0, 0.82) at mid-swing; charge pole `#E0FFF2` (0.88, 1.0, 0.95) at the mirror points; sprite core adds `(0.9, 1.0, 0.95)` × `k^12` so bright sprites go white-mint. Overall hue band 160–175° at high saturation, low lightness in the field, rising to near-white at the caps. Additive blending over a near-black ground means the haze reads as a lifted teal fog rather than grey; there is no tone map, so stacked sprites clip to white at the poles. No gamma correction — colours are authored as if sRGB and written straight to the framebuffer.

## 8. Composition and camera

Centred single object with no horizon. The outermost shell reaches 0.76 of frame height downward and 0.88 across (fractions of the shorter axis per the source comment) — i.e. the arc cage fills most of the frame on a 16:10 view while the dipole poles sit at ≈0.22, well inside. Aspect: `refAspect` 1.6 clamp means 640×400 and 1920×1080 frame identically; portrait shrinks both axes together. The view is a slightly raised three-quarter shot (pitch 0.36 rad ≈ 21°) so the two pole caps are seen as upper and lower bright zones, not a single spike. Safe margins ≈ 10% on all sides at landscape.

## 9. Randomness and seeds

Seeded mulberry32 (`state += 0x6D2B79F5`, imul mixing) with seed **20260927**, consumed in a fixed order: 1500 charges, then 340 ovals, then 800 dust. Distributions: `L = lMin + r^1.4·(lMax−lMin)` (bias toward the inner shells); swing rate uniform in [0.10, 0.34]; size uniform 0.007–0.0155 (charges), 0.0046–0.0123 (ovals), 0.0185–0.071 (dust); dust x/y uniform ±11.5 / ±7.0, z −1…1. No warmup. Changing the seed changes the cap texture and haze pattern but not the silhouette.

## 10. Performance budget

2 draw calls; 9362 line vertices (4681 segments) + 2640 points. Cost is mostly fill: up to ~900 large additive dust sprites at 90 px each on a DPR-1.5 canvas, plus arc overlap where the shell fans converge near the poles. Comfortably 60 fps on integrated graphics at 1920×1080; the dust is the first expense. Cut-first: `dust` 800→350, then `charges` 1500→800, then `arcSamples` 52→36, then lower the point-size clamp from 90 to 48.

## 11. Host integration

`absolute inset-0 pointer-events-none` holder with a `block w-full h-full` canvas; no input at all. Sizing reads holder offset size at mount and on `window resize`, multiplies by `min(devicePixelRatio, 1.5)`, floors at 1 px, writes CSS px back. Teardown cancels RAF, deletes 2 buffers + 2 programs, then `WEBGL_lose_context.loseContext()`. One instance per page (shared FPS meter). No external assets; fully offline.

## 12. Failure modes and tells

- **Caps never light up** — `pool` depends on `|sin(ωt+phase)|`; if `swingMax` is too high the charges transit the poles too fast to pool. Keep ≤0.4.
- **Arcs look like a solid teal disc** — `shells` or `longitudes` too high at 1 px lines; the fan reads as fill. Drop `longitudes` to 8–10.
- **Arc cage clips frame edges** — `lMax` or `focal` too high: coverage scales with `lMax·focal/distance²`. Target 0.62.
- **Apparatus looks flat / face-on** — `tilt` below ~0.25 rad hides the dipole axis; keep 0.3–0.45.
- **Graticule invisible or dominant** — `graticuleBrightness` 0.14 is deliberate; above 0.25 the sphere reads as a wire globe and competes with the arcs.
- **Haze turns grey** — `dustAlpha` above ~0.7 on a non-additive path, or a blend mode other than `SRC_ALPHA, ONE`; the teal lift only works additively.
- **Sprite discs with hard edges** — point-size clamp hit (90 px) cropping the halo; lower dust size range.
- **Charges rotate with the dust** — dust must be stored in view space and mixed in *after* rotation; applying `toCamera` to dust shears the haze with the apparatus.

## 13. Tuning knobs

1. `lMax` then `focal` — frame coverage and zoom; keep the outer shell at 0.6–0.75 of the short axis.
2. `swingMin`/`swingMax` — cap pooling; lower is brighter caps, slower motion.
3. `arcBrightness` — overall line exposure; 0.4–0.7.
4. `chargeStrength`/`dustAlpha` — cap intensity vs haze lift; 1.0/0.3 is the rested look.
5. `pulseRate` — how alive the arcs feel; 0.4–1.2.

## 14. Verification checklist

- Coverage: arc cage 0.6–0.75 of the short axis; pole caps at ≈0.22.
- Dominant hue 160–175° (teal/mint); no warm pixels anywhere.
- Background luma < 3% away from the object, with a visible 5–15% teal lift inside the haze radius.
- Two bright caps visible, roughly 0.25 of the frame height apart, pulsing at ≈20–70 s period.
- Arc pulse travels poleward; sample one arc over 3 s and confirm brightness bands move.
- No clipping at frame edges for aspect ≥ 1.0; no flicker on resize.
- The shipped poster shows a much tighter, dimmer object than the current constants imply; treat `focal`/`distance` (0.62 coverage) as authoritative for scale and the poster as a hue/structure reference.

## 15. Porting notes

The arcs are a `gl.LINES` pass and will not render with `lineWidth > 1` on most platforms — accept 1 px, or replace each segment with a quad ribbon if thicker lines are needed (that changes the additive look and is not the original). In three.js, the double divide can be approximated with `LineBasicMaterial` + a ≤12° perspective camera at 11 units. Dust must stay in view space; if you parent it to the rotating group the haze will smear.
