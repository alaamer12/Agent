---
id: cosmic-anomaly
name: Cosmic Anomaly
family: webgl-f3
renderer: three
poster: assets/posters/cosmic-anomaly.jpg
complexity: L
source_lines: 532
dpr_max: 2
deps: [three]
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Cosmic Anomaly

## 1. Identity

A blinding blue-white particle sphere pulses at the center of the frame, wrapped
in several thin particle rings that tumble around it, all glowing through heavy
bloom against a deep blue nebula.

## 2. Perceived look

Overexposed, blooming, electric blue. The core is not a solid disc — it is
32,000 additive points packed on a sphere at radius 5, so dense that bloom melts
them into a white-hot ball with a ragged, breathing edge. Around it, 8 tilted
rings of 3,200 points each read as irregular bracelets of grit, some passing in
front of the core, some behind. The background is a photographic blue nebula
(HDR), darkest at the corners. Everything has a halo; nothing is crisp except the
fine ring grains. Contrast is maximal at the core and low in the nebula.

## 3. Frame anatomy

A three.js scene rendered through a two-pass composer.

1. **Background** — an equirectangular HDR nebula (`HDR_blue_nebulae-1.hdr`,
   loaded from spacespheremaps.com), used as both `scene.background` and
   `scene.environment`. Until it loads, the canvas is transparent and the host
   gradient shows.
2. **Core sphere** — 32k points, additive, custom shader with noise displacement.
3. **Orbit rings** — 8 × 3,200 points, additive, same shader.
4. **Starfield** — 7,000 points spread over a 48,000-unit cube, additive,
   separate twinkle shader.
5. **Fog** — `FogExp2(0x02020A, 0.01)` (`#02020A`) dims distant particles.
6. **Composer** — `RenderPass` then `UnrealBloomPass(strength 0.9, radius 0.4,
   threshold 0)`.

Renderer is `alpha: true`, clear color `(0,0,0,0)`, DPR clamped to 2, output
color space sRGB. Additive blending with `depthWrite: false`; depth testing is
otherwise on, so ring points behind the core are correctly hidden by nearer
points only through occlusion of writes — effectively there is little sorting.

## 4. Motion law

The main group — sphere plus rings — yaws by 0.00008 rad per frame (≈0.0048 rad/s
at 60 fps, one turn in 21.8 minutes), pitches `−0.22 + 0.02 sin(0.08 t)`, and
bobs 0.08 units at 0.12 rad/s. The core breathes ±1.5% at 0.18 rad/s. Each ring
spins about its own axes at `0.00008 (index + 1)` rad per frame — frame-rate
dependent by design — and its Y scale pulses ±4.5% at 0.6 rad/s with a per-ring
phase. Particle shaders add a pulse of ±4% and a 3D simplex wobble on a
0.18-units/s drift. Open-ended; nothing loops. The pointer moves a soft highlight
that follows the cursor at 0.03 lerp; it does not move the camera.

## 5. Technique and math

**Core distribution.** Fibonacci-sphere spiral: for `i` of 32,000,
`phi = acos(−1 + 2i/N)`, `theta = sqrt(N π) · phi`, position
`5 (cos θ sin φ, sin θ sin φ, cos φ)`, size `0.1 + 0.18 rand`. Colors are a
four-stop interpolation across index: `#4360FF → #B38CFF → #43C3FF → #3540FF`,
so the sphere has a violet-to-cyan drift rather than one color.

**Rings.** 8 rings at radius 7.5 with radial noise ±0.3 (thickness 0.6), vertical
noise ±0.135, each particle at a uniform angle. Each ring is randomly rotated on
X and Y by up to π, which is what breaks the coplanar look. Ring colors come from
HSL: hue `0.58 + 0.12 (i/8) + 0.05 (j/3200)`, saturation 0.65, lightness 0.6 —
a narrow blue-violet band.

**Displacement.** The point vertex shader evaluates 3D simplex noise at
`position · 0.24 + 0.18 t` on three offset axes (`+0, +10, +20`) and displaces
by 0.7 units. That is a large offset relative to sprite size but small relative to
the 5-unit sphere: it roughens the silhouette rather than reshaping it.

**Sprite shading.** Screen-space mouse distance is measured from the un-displaced
projection (`screenPos = clip.xy / w`) and converted to
`1 − smoothstep(0, 0.4, dist)`; it brightens and enlarges nearby points by 25%.
Point size is `size · 320 / −mv.z · pulse`, with `pulse = 1 + 0.04 sin(0.3 t +
0.6 |position|)`. The fragment is `glow = exp(−3r)` (r = squared radius in sprite
space) times a hash twinkle `0.6 + 0.3 rand`, and alpha `smoothstep(0, 1, glow)`.

**Starfield.** 7,000 points in a 48,000 cube, HSL hue `0.58 + 0.08 rand`,
saturation 0.25, lightness 0.4–0.8; size `0.45 + 0.9 rand`; twinkle
`0.8 + 0.18 sin(0.8 t + 0.06 x + 0.1 y)`; same exponential glow at `exp(−4r)`,
alpha × 0.7. Fog kills most of them; only the nearest few hundred show.

**Bloom.** Threshold 0 means every lit pixel contributes; strength 0.9 and radius
0.4 give the wide, soft halo. This is the dominant visual effect.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 2 | 1–2 | resolution clamp | L |
| core particles | 32000 | 8000–50000 | sphere density and glow | H |
| core radius | 5 | 2–8 | sphere size | H |
| ring count | 8 | 3–12 | number of bracelets | H |
| ring particles | 3200 | 800–5000 | grain density per ring | M |
| ring radius | 7.5 | 5–12 | how far rings sit from the core | H |
| ring thickness | 0.6 | 0.2–1.5 | ring width | M |
| starfield | 7000 | 0–20000 | background specks | L |
| noise frequency | 0.24 | 0.1–0.5 | roughening scale | M |
| noise amplitude | 0.7 | 0–1.5 | silhouette raggedness | H |
| mouse radius | 0.4 | 0.2–0.8 | highlight size | L |
| bloom strength | 0.9 | 0.4–1.6 | halo intensity | H |
| bloom radius | 0.4 | 0.1–0.8 | halo spread | H |
| bloom threshold | 0 | 0–0.6 | what blooms | H |
| fog density | 0.01 | 0–0.03 | depth falloff | M |
| camera FOV | 70° | 50–90 | perspective | M |
| camera position | (0, 4.5, 18) | — | viewpoint | M |
| group tilt | −0.22 rad | −0.5–0 | system obliquity | M |

## 7. Palette and color

Sphere stops `#4360FF`, `#B38CFF`, `#43C3FF`, `#3540FF`; rings HSL
(h ≈ 0.58–0.75, s 0.65, l 0.6) ≈ `#579CDB` to `#9957DB`; stars ≈ `#5C6E99`.
Background is a photographic HDR nebula, so its colors are not authored and vary
by asset. With threshold-0 bloom the whole frame is lifted; the visible white is
bloom saturation, not a palette color. Renderer output is sRGB and the shaders
work in whatever three.js feeds them; no tone mapping is set, so the composer's
output is the final image.

## 8. Composition and camera

70° vertical FOV, camera at `(0, 4.5, 18)` looking at the origin, so the core
(radius 5) subtends roughly 38% of the frame height and the ring system
(radius 7.5) about 58%. Slight downward tilt of the group (`rotation.x = −0.22`)
shows the rings as ellipses. Wide aspect widens the nebula, tall aspect crops it;
the system stays centered. Bloom bleeds roughly 10% of the frame around the core,
so keep at least that much margin in any crop.

## 9. Randomness and seeds

`Math.random()` throughout: core sprite sizes, per-ring particle jitter and ring
rotations, starfield positions/colors/sizes. No seed, no warmup. Layout differs on
every mount; density, radii, and color bands do not. The HDR load is asynchronous,
so the first few hundred milliseconds render a transparent canvas over the host
gradient.

## 10. Performance budget

About 64,600 point sprites across 10 draw calls, plus a full-resolution bloom
composer (two extra passes and several downsample targets). This is the heaviest
scene in the gallery: desktop GPUs hold 60 fps at 1080p with DPR 2, integrated
GPUs and mobile fall to 30 or below. Cut order: DPR to 1, bloom resolution
(halve the composer size), core particles to 18k, rings to 5.

## 11. Host integration

Deviates from the contract twice. (1) The holder does **not** carry
`pointer-events-none`; only the canvas does, so the holder intercepts pointer
events over its whole area — reproduce this if overlay controls must not receive
them. (2) It fetches an external HDR (`HDR_blue_nebulae-1.hdr`) at mount; offline
or blocked, the scene runs with no background and no environment lighting,
leaving particles over the host gradient. `OrbitControls` is constructed but
disabled (`enabled = false`) and only updated for damping. Teardown traverses
geometries and materials, disposes controls/composer/renderer, calls
`forceContextLoss()`, and disposes the HDR texture.

## 12. Failure modes and tells

- **Frame is a white blob →** bloom strength above ~1.3 with radius 0.4; with
  threshold 0 the core swallows the rings. Note that raising the threshold
  removes bloom, so it cannot cause this failure.
- **No nebula background →** HDR fetch failed; the scene is transparent, not
  black.
- **Points look like flat dots with no halo →** additive blending or
  `depthWrite: false` dropped; the glow is `exp(−3r)`, not a hard disc.
- **Rings are concentric circles, not scattered bracelets →** per-ring random
  X/Y rotations were removed.
- **Sphere surface is smooth and round →** noise displacement amplitude near 0;
  the ragged rim is the 0.7-unit simplex offset.
- **Scene speeds up on high-refresh monitors →** the per-frame increments
  (`rotation.y += 0.00008`) are frame-count based, not time based — faithful to
  the original, but do not "fix" one without the other.
- **Clicking and dragging rotates the camera →** `controls.enabled` was left
  true; the original disables it.
- **Memory climbs after navigation →** geometries/materials not disposed, or
  `forceContextLoss` skipped.

## 13. Tuning knobs

1. Bloom strength and radius — from crisp grit to full white-out (0.6–1.2).
2. Core particle count — density of the ball (20k–40k).
3. Ring radius — how much air sits between core and rings (6.5–9).
4. Noise amplitude — smooth sphere versus ragged anomaly (0.3–1.0).
5. Ring count — sparse armillary versus dense cage (5–10).

## 14. Verification checklist

- Core reads as an overexposed blue-white ball with a ragged rim.
- At least five distinct elliptical rings visible around it.
- Fine grain in the rings, not smooth tubes.
- Nebula background present and blue; corners darker than the center.
- Heavy but smooth bloom; no banding rings around the core.
- Motion is very slow; no visible stepping at 60 fps.
- Compare with `assets/posters/cosmic-anomaly.jpg`: core size, ring spread, and
  bloom radius. Particle positions differ because the RNG is unseeded.

## 15. Porting notes

three.js version matters: `outputColorSpace = SRGBColorSpace` is r152+, and
`forceContextLoss` is the teardown. The bloom pass must render after the scene
with `renderer.autoClear` left alone; moving bloom before the render pass produces
a black frame. The external HDR is a hard dependency for the intended look —
substitute any equirectangular HDR or a procedural nebula if the network is
unavailable.
