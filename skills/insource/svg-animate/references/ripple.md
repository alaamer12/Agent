# Recipe: ripple — `/svg-animate ripple`

The logo settles out of water: fractal noise displaces its actual geometry and
the warp relaxes until the edges go crisp. One-shot. The only style here that
touches the shape's vertices instead of painting over it.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="path-teal" d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="path-navy" d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <filter id="ripple-warp" x="-15%" y="-15%" width="130%" height="130%" color-interpolation-filters="sRGB">
      <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="1" seed="7" result="noise">
        <animate attributeName="baseFrequency" values="0.02;0.014;0.005" dur="1.6s" fill="freeze"
                 calcMode="spline" keyTimes="0;0.4;1" keySplines="0.3 0 0.4 1;0.4 0 0.2 1"/>
      </feTurbulence>
      <feDisplacementMap in="SourceGraphic" in2="noise" xChannelSelector="R" yChannelSelector="G" scale="5">
        <animate attributeName="scale" values="5;3.5;0" dur="1.6s" fill="freeze"
                 calcMode="spline" keyTimes="0;0.4;1" keySplines="0.3 0 0.4 1;0.4 0 0.2 1"/>
      </feDisplacementMap>
    </filter>
    <style>
      .logo { opacity: 0; animation: ripple-in 1.6s linear forwards; }
      @keyframes ripple-in { 0% { opacity: 0; } 14% { opacity: 1; } 100% { opacity: 1; } }
      /* The warp is SMIL and cannot be paused from CSS, but the filter
         property outranks the filter attribute — switching it off here
         lands the logo undistorted. */
      @media (prefers-reduced-motion: reduce) {
        .logo { animation: none; opacity: 1; filter: none; }
      }
    </style>
  </defs>

  <g class="logo" filter="url(#ripple-warp)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **`color-interpolation-filters="sRGB"` is required, not decorative.** The
  default is `linearRGB`, which for a displacement map produces a systematic
  global offset and dulls the colours. None of the older glow recipes set it —
  new work should.
- **`scale` is the amplitude.** The safety clamp is ~F/2 (2.4px on the test
  logo, whose thinnest feature is 4.84px), but landing *on* the clamp makes the
  effect nearly invisible. The build deliberately peaks at 5 and holds 3.5
  through the first 40%: mid-flight, 12 of 111 sampled counter pixels get
  inked by the warp, and all 111 are clean at the end (drift 0.08%) because
  `scale` lands on exactly 0. Distortion is recoverable by construction — that
  is what makes it safe to push.
- **Hold, then settle.** A two-stop `values="5;0"` front-loads the decay, so by
  35% of the beat the warp is already gone and the whole effect reads as a
  fade-in. Three stops with `keyTimes="0;0.4;1"` keep it visible.
- **`baseFrequency` ≈ 1/(H/2.2)** puts one noise cell across roughly half the
  logo height. Much higher and the edge turns to static; much lower and the
  whole shape just slides.
- **Animate the filter's attributes with SMIL — CSS cannot touch them.**
  `stdDeviation`, `baseFrequency`, `radius` and `scale` are all animatable, but
  only as attributes. Number-*list* values (`baseFrequency`, `stdDeviation`)
  only interpolate between same-cardinality stops: `"0.02;0.005"` is fine,
  `"0.02;0.014 0.005"` is not.
- **`seed` is a style choice.** Fix it for a reproducible frame-by-frame
  comparison; change it to vary the water.
- Do **not** try to sweep a band of distortion across the logo — that needs a
  moving mask, which is `chrome-liquid`'s mechanic. This style warps the whole
  shape at once.
- Filter region must clear the amplitude: `scale` 5 needs ~10u of room, and
  region percentages are relative to the element's **bbox**, not the canvas.
  Applied to the wrapper `<g>` (bbox ≈ canvas) `-15%/130%` is enough; applied
  per-path it is not.
- **Verified in Chromium 153 only.**
