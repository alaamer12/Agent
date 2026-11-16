# Porting

The scene descriptions are framework-neutral. Only the mount/teardown shell
changes; the math, constants, and draw order do not.

## Lifecycle equivalents

| step | Vue 3 | React 18+ | vanilla |
| --- | --- | --- | --- |
| mount | `onMounted` in `<script setup>` | `useEffect(() => {…}, [])` | after the canvas exists in the DOM |
| size | `container.offsetWidth` | `ref.current.offsetWidth` | `element.offsetWidth` |
| loop | `requestAnimationFrame` | `requestAnimationFrame` | `requestAnimationFrame` |
| resize | `window.addEventListener("resize", fn, { passive: true })` | same, removed in the effect cleanup | same |
| teardown | `onBeforeUnmount` | effect cleanup function | `destroy()` on unmount or route change |

Rules that survive the port:

- Start the loop only after the first size measurement. A canvas sized 0x0
  produces a division by zero in aspect correction and a blank frame forever.
- Cancel the pending frame id, not just "stop looping", or a queued callback
  paints once after teardown and throws on a null context.
- Keep a single `startTime` per mount. Recomputing the origin on resize resets
  every phase and produces a visible jump.
- Rebuild data after a resize when density is area-derived; otherwise the scene
  keeps the particle count from the old size.

## Canvas 2D

- `ctx.setTransform(dpr, 0, 0, dpr, 0, 0)` once per resize keeps all drawing
  code in CSS pixels.
- Trails use either a translucent full-rect fill or `clearRect`; the scene
  document says which. Do not substitute one for the other — a trail scene
  cleared every frame loses its whole character.
- `globalCompositeOperation = "lighter"` is additive light. Restore
  `"source-over"` afterwards or every later fill behaves differently.
- `filter: blur()` and `shadowBlur` are the most expensive canvas features and
  differ slightly across engines. Where a scene relies on them, the family doc
  gives a cheaper substitute (pre-blurred sprite atlas).
- `Path2D` batching matters above ~2,000 segments per frame; drawing one path
  per particle is the usual bottleneck.

## Raw WebGL1

All originals target WebGL1 with GLSL ES 1.00: `attribute`, `varying`,
`gl_FragColor`, no `in/out`, no integer textures. Reconstructions should stay
on WebGL1 unless the target explicitly requires WebGL2; the shaders port
mechanically but the attribute names and precision qualifiers change.

- Use one oversized triangle or a full-screen quad for fragment-only scenes.
  Both are fine; a quad costs one more vertex and no extra state.
- `highp` in fragment shaders is not guaranteed on mobile; scenes that need it
  (WarpField, FractalDrift, EndlessRange, LiquidChrome, NebulaCurrents) say so.
  Elsewhere `mediump` is sufficient and cheaper.
- Explicitly lose the context on teardown. Browsers cap live contexts (~16);
  a gallery that mounts 50 scenes will start dropping the oldest otherwise.
- Point sprites: `gl_PointSize` is in device pixels, so multiply by the DPR
  clamp. Mobile GPUs often cap point size at 63 px — the particle-cloud family
  doc covers the workaround.

## three.js

The seven three.js scenes use plain `ShaderMaterial` with hand-written GLSL and
a `THREE.Clock`. Two traps:

- **Color management.** Since r152, `THREE.Color` converts to linear working
  space by default. Hand-written shaders bypass three's output pass, so colors
  uploaded through `THREE.Color` arrive darker than authored unless you either
  disable color management or upload display-space values directly. The scene
  documents list the authored values in display space.
- **Addons.** `EffectComposer`, `UnrealBloomPass`, `RGBELoader`, and
  `OrbitControls` live under `three/addons`. If the host cannot use addons,
  approximate bloom with an additive back-face shell or a sprite layer, as
  ChromaticKnot and PulseOrb already do.

Dispose geometry, materials, render targets, and the renderer; call
`renderer.forceContextLoss()`. Skipping this leaks a GL context per switch.

## Dependencies

| dependency | used by | substitute |
| --- | --- | --- |
| `simplex-noise` (2D) | ConstellationNet, FireflyMeadow, FlowField, IsoDrift, SilkStrands, GalaxySpiral | any simplex returning −1..1 with an isotropic permutation |
| `simplex-noise` (3D) | ContourMap, SmokeWisps | same, 3D variant |
| `three` | 7 scenes | none — the scenes are three-specific; port the math if three is unavailable |
| `three/addons` | CosmicAnomaly only | bloom can be faked; OrbitControls is trivial; the HDR environment is an external asset |

## External assets

Only CosmicAnomaly fetches a remote HDR environment from `spacespheremaps.com`.
It is not required for the look; the scene works with a flat color background,
but the reflections lose their horizon band. Every other scene is
self-contained: no images, fonts, or network requests.
