# Recipe: etch — `/animation svg etch`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `engrave` (3-D diffuse lighting relief) and `crt` (horizontal black scanlines). Uses a rotated `45°` dual-color crosshatch `<pattern>` clipped strictly to the logo silhouette.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <clipPath id="...">
      <use href="#path-teal"/>
      <use href="#path-navy"/>
    </clipPath>
    <pattern id="..." width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <rect width="8" height="1.4" fill="#040c24"/>
      <rect width="1.4" height="8" fill="#0494a4" fill-opacity="0.7"/>
    </pattern>
    <mask id="..." maskUnits="userSpaceOnUse" x="-5" y="-5" width="310" height="120">
      <rect x="-5" y="-5" width="310" height="120" fill="#000"/>
      <rect x="-5" y="-5" width="0" height="120" fill="#fff">
        <animate attributeName="width" values="0;310" dur="0.95s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.8 0.3 1"/>
      </rect>
    </mask>
  </defs>

  <style>
    .etch-proof { opacity: 0.85; animation: etch-out 0.65s linear 0.95s forwards; }
    .etch-solid { opacity: 0; animation: etch-in 0.65s ease-out 0.95s forwards; }
    @keyframes etch-out { to { opacity: 0; } }
    @keyframes etch-in { to { opacity: 1; } }
    @media (prefers-reduced-motion: reduce) {
      .etch-wrap { mask: none; }
      .etch-proof { animation: none; opacity: 0; }
      .etch-solid { animation: none; opacity: 1; }
    }
  </style>

  <g class="etch-wrap" mask="url(#etch-wipe)">
    <g clip-path="url(#etch-logo)">
      <rect class="etch-proof" width="300" height="110" fill="url(#etch-hatch)"/>
    </g>
  </g>
  <g class="etch-solid">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Transparent pattern base**: paint only the two intersecting `1.4u` hairline `<rect>` strokes inside `#etch-hatch` so letterform counters stay completely clean.
- Clip `#etch-hatch` to `url(#etch-logo)` and fade `.etch-proof` to `opacity: 0` as `.etch-solid` fades in (`0.95s–1.6s`).
