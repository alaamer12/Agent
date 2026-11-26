# Recipe: tunnel — `/animation svg tunnel`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

The rectilinear architectural counterpart to `rings`. A central rounded pill plus 5 concentric stroked `<rect rx>` frames expand outward on staggered delays until neighbouring bands merge.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <mask id="..." maskUnits="userSpaceOnUse" x="-5" y="-5" width="310" height="120">
      <rect x="-5" y="-5" width="310" height="120" fill="#000"/>
      <rect x="132" y="45" width="36" height="20" rx="8" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.35s" begin="0.00s" fill="freeze"/></rect>
      <rect x="105.0" y="35.5" width="90.0" height="39.0" rx="12" fill="none" stroke="#fff" stroke-width="0"><animate attributeName="stroke-width" values="0;36" dur="0.55s" begin="0.08s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/></rect>
      <rect x="78.0" y="26.0" width="144.0" height="58.0" rx="12" fill="none" stroke="#fff" stroke-width="0"><animate attributeName="stroke-width" values="0;36" dur="0.55s" begin="0.21s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/></rect>
      <rect x="51.0" y="16.5" width="198.0" height="77.0" rx="12" fill="none" stroke="#fff" stroke-width="0"><animate attributeName="stroke-width" values="0;36" dur="0.55s" begin="0.34s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/></rect>
      <rect x="24.0" y="7.0" width="252.0" height="96.0" rx="12" fill="none" stroke="#fff" stroke-width="0"><animate attributeName="stroke-width" values="0;36" dur="0.55s" begin="0.47s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/></rect>
      <rect x="-3.0" y="-2.5" width="306.0" height="115.0" rx="12" fill="none" stroke="#fff" stroke-width="0"><animate attributeName="stroke-width" values="0;36" dur="0.55s" begin="0.60s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/></rect>
    </mask>
    <style>
      @media (prefers-reduced-motion: reduce) { .logo { mask: none; } }
    </style>
  </defs>

  <g class="logo" mask="url(#tunnel-mask)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Overlap math**: step box width by `ΔW ≈ W/5.5` (`54u`) and height by `ΔH ≈ H/5.8` (`19u`), then animate `stroke-width` from `0` to `max(ΔW/2, ΔH/2) + 9` (`36u`) so every ring overlaps its neighbour completely with zero unlit gaps at rest.
