# Recipe: vignette — `/animation svg vignette`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `iris` (hard circular clip) and `lantern` (moving off-center gradient). A stationary centered `radialGradient` inside `<mask>` expands smoothly with feathered edges.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <radialGradient id="..." cx="0.5" cy="0.5" r="0.15">
      <stop offset="0%" stop-color="#fff"/>
      <stop offset="55%" stop-color="#fff"/>
      <stop offset="100%" stop-color="#000"/>
      <animate attributeName="r" values="0.12;0.55;2.2" dur="1.4s" fill="freeze"
               keyTimes="0;0.55;1" calcMode="spline" keySplines="0.3 0 0.4 1;0.3 0 0.2 1"/>
    </radialGradient>
    <mask id="..." maskUnits="userSpaceOnUse" x="-5" y="-5" width="310" height="120">
      <rect x="-5" y="-5" width="310" height="120" fill="url(#vig-grad)"/>
    </mask>
    <style>
      @media (prefers-reduced-motion: reduce) { .logo { mask: none; } }
    </style>
  </defs>

  <g class="logo" mask="url(#vig-mask)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Final radius floor `r ≥ 2.0`** (`2.2` here in `objectBoundingBox` units) so the `55%` solid-white stop passes well beyond every corner (`0.55 × 2.2 = 1.21 > 0.71`), guaranteeing 0.00% edge dimming at rest.
- Two-stage spline (`keyTimes="0;0.55;1"`) holds the moody halo mid-flight before opening fully.
