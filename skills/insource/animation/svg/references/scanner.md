# Recipe: scanner — `/animation svg scanner`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `spark` (a point dot tracing a motion path) and `lantern` (a soft wandering spotlight). A vertical glowing laser bar sweeps right to reveal a hairline wireframe pass, then reverses left to lock the solid true-colour fills in its wake.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." fill-rule="evenodd"/>
    <path id="..." d="..." fill-rule="evenodd"/>
    <linearGradient id="..." x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0494a4" stop-opacity="0"/>
      <stop offset="50%" stop-color="#0494a4" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#0494a4" stop-opacity="0"/>
    </linearGradient>
    <mask id="..." maskUnits="userSpaceOnUse" x="-5" y="-5" width="310" height="120">
      <rect x="-5" y="-5" width="310" height="120" fill="#000"/>
      <rect x="0" y="-5" width="0" height="120" fill="#fff">
        <animate attributeName="width" values="0;305" dur="0.82s" begin="0.06s" fill="freeze"
                 calcMode="spline" keyTimes="0;1" keySplines="0.3 0 0.4 1"/>
      </rect>
    </mask>
    <mask id="..." maskUnits="userSpaceOnUse" x="-5" y="-5" width="310" height="120">
      <rect x="-5" y="-5" width="310" height="120" fill="#000"/>
      <rect x="305" y="-5" width="0" height="120" fill="#fff">
        <animate attributeName="x" values="305;-5" dur="0.82s" begin="0.92s" fill="freeze"
                 calcMode="spline" keyTimes="0;1" keySplines="0.3 0 0.4 1"/>
        <animate attributeName="width" values="0;310" dur="0.82s" begin="0.92s" fill="freeze"
                 calcMode="spline" keyTimes="0;1" keySplines="0.3 0 0.4 1"/>
      </rect>
    </mask>
  </defs>

  <style>
    .scan-wire-wrap { animation: wire-dismiss 0.35s linear 1.48s forwards; }
    .scan-beam { opacity: 0; animation: beam-move 1.8s linear forwards; }
    @keyframes wire-dismiss { to { opacity: 0; } }
    @keyframes beam-move {
      0%   { transform: translateX(-8px); opacity: 0; }
      5%   { opacity: 1; }
      49%  { transform: translateX(298px); opacity: 1; }
      52%  { transform: translateX(298px); opacity: 0.9; }
      95%  { transform: translateX(-8px); opacity: 1; }
      100% { transform: translateX(-8px); opacity: 0; }
    }
    @media (prefers-reduced-motion: reduce) {
      .scan-wire-wrap { animation: none; opacity: 0; mask: none; }
      .scan-solid-wrap { mask: none; }
      .scan-beam { animation: none; opacity: 0; }
    }
  </style>

  <g class="scan-wire-wrap" mask="url(#scan-wire-mask)">
    <use href="#path-teal" fill="none" stroke="#0494a4" stroke-width="1"/>
    <use href="#path-navy" fill="none" stroke="#0494a4" stroke-width="1"/>
  </g>
  <g class="scan-solid-wrap" mask="url(#scan-solid-mask)">
    <use href="#path-teal" stroke="none" fill="#0494a4"/>
    <use href="#path-navy" stroke="none" fill="#040c24"/>
  </g>
  <rect class="scan-beam" x="0" y="0" width="10" height="110" fill="url(#scan-beam-grad)"/>
</svg>
```

## Notes

- **Bare `<path>` defs in `<defs>`** (carry `d` and `fill-rule` only, omitting `fill`/`stroke`), exactly like `blueprint` and `chrome-liquid`, so the wireframe `<use>` renders strictly as a stroke while the solid `<use>` carries the original fills.
- **Synchronize the two masks to the beam**: Pass 1 (`0.06s–0.88s`) grows `#scan-wire-mask` left-to-right; Pass 2 (`0.92s–1.74s`) grows `#scan-solid-mask` right-to-left (`x: W+5 → -5`, `width: 0 → W+10`), while `.scan-wire-wrap` fades to `0` behind the return sweep so no stroke halo remains at rest.
- Beam width `≈ max(6, W/30)` in the primary brand colour with 0→0.95→0 horizontal gradient stops so it reads cleanly on both light and dark stages.
