# Recipe: grain — `/svg-animate grain`

The logo resolves out of film grain: a noise field is thresholded upward until
nothing is masked away, so the artwork appears through growing speckle.
One-shot; ends pixel-exact.

Distinct from `ripple`, which *warps* geometry with the same noise source. Here
noise decides **visibility**, never position.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="path-teal" d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="path-navy" d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <filter id="grain-in" x="0%" y="0%" width="100%" height="100%" color-interpolation-filters="sRGB">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="11" result="noise"/>
      <feColorMatrix in="noise" type="matrix" result="noise-a"
        values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  1 0 0 0 0"/>
      <feComponentTransfer in="noise-a" result="threshold">
        <feFuncA type="table" tableValues="0 0">
          <animate attributeName="tableValues" values="0 0;0 0.55;0 1;1 1" dur="1.5s" fill="freeze"
                   keyTimes="0;0.35;0.7;1"/>
        </feFuncA>
      </feComponentTransfer>
      <feComposite in="SourceGraphic" in2="threshold" operator="in"/>
    </filter>
    <style>
      @media (prefers-reduced-motion: reduce) { .logo { filter: none; } }
    </style>
  </defs>

  <g class="logo" filter="url(#grain-in)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **`tableValues` is animatable, and it is the whole effect.** The two numbers
  are the output alpha at input 0 and input 1, so `"0 0"` hides everything,
  `"0 1"` is the identity (everything shows), and `"1 1"` forces everything
  opaque. Ending on `"1 1"` is what makes the resting frame exact — measured
  0.08% drift, 0 of 111 counters filled.
- **The last stop matters more than the middle ones.** `"0 0;0 1"` alone leaves
  the noise still gating the artwork at the end; you must close with `"1 1"` to
  switch the mask off entirely.
- `feColorMatrix` copies the noise's **red channel into alpha** and zeroes RGB,
  because `feComposite operator="in"` gates on the second input's alpha. That
  matrix row (`1 0 0 0 0` in the alpha line) is the non-obvious line in this
  recipe.
- `baseFrequency` sets the grain size: ≈0.9 is fine film grain; below ~0.2 the
  "grain" becomes big blotches and reads as a dissolve, which is `mosaic`'s
  territory. Keep `numOctaves` at 2 — more costs real time at this size for no
  visible gain.
- Filter region is `100%` here on purpose: this filter never expands the
  artwork, so unlike the glow and displacement styles it wants no margin.
- `seed` is a style choice; fix it for reproducible frame comparisons.
- **Verified in Chromium 153 only.**
