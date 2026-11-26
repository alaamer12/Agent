# Recipe: rings — `/animation svg rings`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `iris` (one filled circle growing outward) and `ripple` (turbulence vertex displacement). Concentric stroked `<circle>` rings inside a `<mask>` radiate outward on staggered delays, each thickening its `stroke-width` until neighbouring bands fuse into solid white.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <mask id="..." maskUnits="userSpaceOnUse" x="-5" y="-5" width="310" height="120">
      <rect x="-5" y="-5" width="310" height="120" fill="#000"/>
      <circle cx="150" cy="55" r="0" fill="#fff"><animate attributeName="r" values="0;26" dur="0.45s" begin="0.00s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.2 0.8 0.3 1"/></circle>
      <circle cx="150" cy="55" r="22" fill="none" stroke="#fff" stroke-width="0"><animate attributeName="stroke-width" values="0;40" dur="0.62s" begin="0.08s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.85 0.35 1"/></circle>
      <circle cx="150" cy="55" r="54" fill="none" stroke="#fff" stroke-width="0"><animate attributeName="stroke-width" values="0;40" dur="0.62s" begin="0.22s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.85 0.35 1"/></circle>
      <circle cx="150" cy="55" r="86" fill="none" stroke="#fff" stroke-width="0"><animate attributeName="stroke-width" values="0;40" dur="0.62s" begin="0.36s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.85 0.35 1"/></circle>
      <circle cx="150" cy="55" r="118" fill="none" stroke="#fff" stroke-width="0"><animate attributeName="stroke-width" values="0;40" dur="0.62s" begin="0.50s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.85 0.35 1"/></circle>
      <circle cx="150" cy="55" r="150" fill="none" stroke="#fff" stroke-width="0"><animate attributeName="stroke-width" values="0;40" dur="0.62s" begin="0.64s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.85 0.35 1"/></circle>
    </mask>
    <style>
      @media (prefers-reduced-motion: reduce) { .logo { mask: none; } }
    </style>
  </defs>

  <g class="logo" mask="url(#rings-mask)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Fusion math**: space ring radii by `step = R_max / N` where `R_max = hypot(W/2, H/2)` (159.8u on 300×110, so `step = 32u` across 5 rings: `22, 54, 86, 118, 150`). Animate each ring's `stroke-width` from `0` to `step + 8` (`40u`) and a central solid dot from `r=0` to `r = r_0 + 4` (`26u`). Every band overlaps its neighbour by ≥4u — zero gaps at rest.
- **Never animate a `<pattern>` for this** (see `rejected-mechanics.md` on `halftone`); explicit concentric circles inside `<mask>` stagger cleanly and resolve features of any size.
- Stagger `begin = 0.08 + idx · 0.14s` scaled per foundations §5.
