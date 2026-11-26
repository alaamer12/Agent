# Recipe: crosshair — `/animation svg crosshair`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `curtain` (single vertical split) and `crt` (single horizontal band). Both axes open together after a brief centre-target sighting flash.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <mask id="..." maskUnits="userSpaceOnUse" x="-5" y="-5" width="310" height="120">
      <rect x="-5" y="-5" width="310" height="120" fill="#000"/>
      <rect x="148" y="-5" width="4" height="120" fill="#fff">
        <animate attributeName="x" values="148;148;-5" dur="1.15s" fill="freeze" keyTimes="0;0.32;1" calcMode="spline" keySplines="0.4 0 0.6 1;0.22 0.85 0.3 1"/>
        <animate attributeName="width" values="0;6;310" dur="1.15s" fill="freeze" keyTimes="0;0.32;1" calcMode="spline" keySplines="0.4 0 0.6 1;0.22 0.85 0.3 1"/>
      </rect>
      <rect x="-5" y="53" width="310" height="4" fill="#fff">
        <animate attributeName="y" values="55;53;-5" dur="1.15s" fill="freeze" keyTimes="0;0.32;1" calcMode="spline" keySplines="0.4 0 0.6 1;0.22 0.85 0.3 1"/>
        <animate attributeName="height" values="0;4;120" dur="1.15s" fill="freeze" keyTimes="0;0.32;1" calcMode="spline" keySplines="0.4 0 0.6 1;0.22 0.85 0.3 1"/>
      </rect>
    </mask>
  </defs>

  <style>
    .cross-sight { opacity: 0; animation: sight-flash 0.65s linear forwards; }
    @keyframes sight-flash { 0% { opacity: 0; } 25% { opacity: 0.9; } 100% { opacity: 0; } }
    @media (prefers-reduced-motion: reduce) {
      .logo { mask: none; }
      .cross-sight { animation: none; opacity: 0; }
    }
  </style>

  <g class="logo" mask="url(#cross-mask)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
  <g class="cross-sight">
    <rect x="149.25" y="0" width="1.5" height="110" fill="#0494a4"/>
    <rect x="0" y="54.25" width="300" height="1.5" fill="#0494a4"/>
  </g>
</svg>
```

## Notes

- **Two-phase SMIL `keyTimes="0;0.32;1"`**: hold the white mask bars narrow (`6u` / `4u`) during the first 32% so the plus-sign silhouette reads clearly, then expand both to full `W+10` / `H+10`.
- Keep the brand-colored sighting lines outside the mask so they flash cleanly at `t = 0` and fade to 0 before the bars open.
