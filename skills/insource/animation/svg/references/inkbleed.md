# Recipe: inkbleed — `/animation svg inkbleed`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `grain` (`baseFrequency="0.9"` fine analog static). Uses low-frequency 3-octave fractal noise (`baseFrequency="0.055"`) with contrast-boosted alpha so broad organic pools spread across the mark.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <filter id="..." x="0%" y="0%" width="100%" height="100%" color-interpolation-filters="sRGB">
      <feTurbulence type="fractalNoise" baseFrequency="0.055" numOctaves="3" seed="..." result="cloud"/>
      <feColorMatrix in="cloud" type="matrix" result="cloud-a"
        values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  1.4 0 0 0 -0.2"/>
      <feComponentTransfer in="cloud-a" result="ink-mask">
        <feFuncA type="table" tableValues="0 0">
          <animate attributeName="tableValues" values="0 0;0 0.6;0 1;1 1" dur="1.65s" fill="freeze"
                   keyTimes="0;0.38;0.74;1"/>
        </feFuncA>
      </feComponentTransfer>
      <feComposite in="SourceGraphic" in2="ink-mask" operator="in"/>
    </filter>
    <style>
      @media (prefers-reduced-motion: reduce) { .logo { filter: none; } }
    </style>
  </defs>

  <g class="logo" filter="url(#ink-bloom)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **`baseFrequency ≈ 16 / W`** (`0.055` at W=300) creates macro watercolor blooms spanning multiple strokes instead of fine sand grain.
- Must close `tableValues` on `"1 1"` (just like `grain`) so the noise mask switches off completely at `fill="freeze"`. Always set `color-interpolation-filters="sRGB"`.
