# Recipe: chisel — `/animation svg chisel`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `engrave` (which rotates `azimuth` horizontally around the logo). Here `azimuth` stays fixed at `270°` while `elevation` climbs from stark grazing shadows (`12°`) to overhead flat light (`78°`).

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <filter id="..." x="-10%" y="-10%" width="120%" height="120%" color-interpolation-filters="sRGB">
      <feGaussianBlur in="SourceAlpha" stdDeviation="1.8" result="edge"/>
      <feDiffuseLighting in="edge" surfaceScale="3.5" diffuseConstant="1.15" lighting-color="#ffffff" result="carved">
        <feDistantLight azimuth="270" elevation="12">
          <animate attributeName="elevation" values="12;42;78" dur="1.65s" fill="freeze"
                   calcMode="spline" keyTimes="0;0.55;1" keySplines="0.35 0 0.55 1;0.3 0 0.2 1"/>
        </feDistantLight>
      </feDiffuseLighting>
      <feComposite in="carved" in2="SourceAlpha" operator="in"/>
    </filter>
  </defs>

  <style>
    .chisel-stone { animation: stone-out 0.65s linear 1.0s forwards; }
    .chisel-solid { opacity: 0; animation: stone-in 0.65s linear 1.0s forwards; }
    @keyframes stone-out { to { opacity: 0; } }
    @keyframes stone-in { to { opacity: 1; } }
    @media (prefers-reduced-motion: reduce) {
      .chisel-stone { animation: none; opacity: 0; filter: none; }
      .chisel-solid { animation: none; opacity: 1; }
    }
  </style>

  <g class="chisel-stone" filter="url(#chisel-fx)">
    <use href="#path-teal" fill="#7c8798"/>
    <use href="#path-navy" fill="#7c8798"/>
  </g>
  <g class="chisel-solid">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- Keep `stdDeviation` ≤ `F/2` (`1.8` on 300×110) so thin strokes carve crisply without merging counters.
- Fade `.chisel-stone` out to `opacity: 0` alongside `.chisel-solid` fading in (`1.0s–1.65s`) to eliminate blurred-alpha edge drift.
