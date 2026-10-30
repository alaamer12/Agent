# Host contract

Every original scene was written against one host. A reconstruction should keep
the same contract so it can be dropped into a gallery, a preview route, or a
single hero section without changes.

## What the host must provide

- A **positioned, full-bleed container**. The scene root is absolutely
  positioned with zero insets. `absolute; inset: 0` resolves against the nearest
  positioned ancestor; if the host forgets `position: relative`, the scene
  escapes to the viewport instead of filling its box.
- A **closed stacking context** sized in CSS pixels. The scene measures
  `container.offsetWidth/offsetHeight` and falls back to
  `window.innerWidth/innerHeight` when the container reports zero.
- **Exactly one mounted scene at a time.** The FPS meter is a singleton
  (40-frame rolling mean, shared state), and several scenes assume they own the
  pointer. Two live scenes will corrupt the reading and double the GPU cost.
- **No host-driven resize calls.** Scenes listen to `window.resize` themselves.
  A host that resizes the container without resizing the window (a panel, a
  split view) must either also listen and forward, or use a `ResizeObserver` —
  only three originals (DNAHelix, ParticleWaves, SpectrumCascade) do this.

## Scene lifecycle

1. Read the container size, clamp `devicePixelRatio` to the scene's `dpr_max`
   (1.5 for 43 of 50 scenes), size the backing store to
   `width * dpr` by `height * dpr`, set the CSS size in pixels, then set the
   2D transform to `dpr` or the GL viewport to the backing size.
2. Create the context. Canvas 2D scenes usually pass `{ alpha: false }`; the
   WebGL scenes pass `{ alpha: false, antialias: true, depth: false, stencil:
   false, preserveDrawingBuffer: false }` unless noted in the scene document.
3. Prime state. Canvas trail scenes run 6–340 hidden frames so the first
   visible frame is not empty; particle scenes build their buffers; GL scenes
   compile programs and upload attributes.
4. Start the FPS meter, then the animation loop. `tick()` is called exactly once
   per rendered frame, before drawing. All timing is derived from
   `performance.now() - startTime` or an accumulating frame counter; nothing
   depends on wall-clock date.
5. On teardown: cancel the animation frame, remove every listener, stop the
   meter, delete GL programs/buffers and call `WEBGL_lose_context`, or drop
   arrays and context references. Scenes are destroyed on switch, never reused.

## Backdrop

The original preview host paints a vertical gradient from `#000000` to
`#1A0033` behind the canvas. Scenes with an opaque fill hide it; scenes with a
transparent or alpha canvas are designed to sit on it. Every scene document
states which case applies in section 3 and section 7. If you drop a
transparent-canvas scene onto a light surface, it will look wrong even though
the geometry is identical.

## Runtime deviations

These scenes do not follow the default contract; their documents repeat the
detail.

| scene | deviation |
| --- | --- |
| CosmicAnomaly | canvas receives pointer events (root is not fully pointer-transparent); loads a remote HDR environment; uses OrbitControls and an UnrealBloom pass |
| MetaballOrbit | root carries a CSS radial-gradient backdrop; is the only scene with a `u_mouse` uniform fed by `mousemove` |
| FluidRipples | GL context created with `premultipliedAlpha: false`; simulation runs on the CPU and uploads a float texture each frame |
| AuroraWaves | the only scene with no DPR clamp; teardown goes through a class `destroy()` |
| SpectrumCascade | 2D context created with `alpha: true`; adds a `ResizeObserver` |
| DNAHelix, ParticleWaves | add a `ResizeObserver`; both are ported from CodePen originals |
| NeuralNoise, DNAHelix, RibbonFlow | WebGL context with `alpha: true` |

## Framework mapping

The host contract is framework-neutral: mount, size, loop, teardown. See
`porting.md` for the concrete Vue / React / vanilla equivalents and the
three.js-specific traps.
