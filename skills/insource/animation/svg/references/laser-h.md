# Recipe: laser-h — `/animation svg laser-h`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

The twin horizontal counterpart to `scanner` (vertical back-and-forth pass). Two beams part upward and downward from `y = H/2`, drawing wireframe slightly ahead of the solid fill mask.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." fill-rule="evenodd"/>
    <path id="..." d="..." fill-rule="evenodd"/>
    <linearGradient id="..." x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#0494a4" stop-opacity="0"/>
      <stop offset="50%" stop-color="#0494a4" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#0494a4" stop-opacity="0"/>
    </linearGradient>
    <mask id="..." maskUnits="userSpaceOnUse" x="-5" y="-5" width="310" height="120">
      <rect x="-5" y="-5" width="310" height="120" fill="#000"/>
      <rect x="-5" y="55" width="310" height="0" fill="#fff">
        <animate attributeName="y" values="55;-5" dur="0.72s" begin="0.06s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.8 0.3 1"/>
        <animate attributeName="height" values="0;120" dur="0.72s" begin="0.06s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.8 0.3 1"/>
      </rect>
    </mask>
    <mask id="..." maskUnits="userSpaceOnUse" x="-5" y="-5" width="310" height="120">
      <rect x="-5" y="-5" width="310" height="120" fill="#000"/>
      <rect x="-5" y="55" width="310" height="0" fill="#fff">
        <animate attributeName="y" values="55;-5" dur="0.72s" begin="0.34s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.8 0.3 1"/>
        <animate attributeName="height" values="0;120" dur="0.72s" begin="0.34s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.8 0.3 1"/>
      </rect>
    </mask>
  </defs>

  <style>
    .lh-wire { animation: lh-wout 0.35s linear 0.92s forwards; }
    .lh-top { opacity: 0; animation: lh-up 0.88s cubic-bezier(0.25, 0.8, 0.3, 1) 0.06s forwards; }
    .lh-bot { opacity: 0; animation: lh-dn 0.88s cubic-bezier(0.25, 0.8, 0.3, 1) 0.06s forwards; }
    @keyframes lh-wout { to { opacity: 0; } }
    @keyframes lh-up { 0% { transform: translateY(0px); opacity: 0; } 12% { opacity: 1; } 85% { opacity: 1; } 100% { transform: translateY(-56px); opacity: 0; } }
    @keyframes lh-dn { 0% { transform: translateY(0px); opacity: 0; } 12% { opacity: 1; } 85% { opacity: 1; } 100% { transform: translateY(56px); opacity: 0; } }
    @media (prefers-reduced-motion: reduce) {
      .lh-wire { animation: none; opacity: 0; mask: none; }
      .lh-solid { mask: none; }
      .lh-top, .lh-bot { animation: none; opacity: 0; }
    }
  </style>

  <g class="lh-wire" mask="url(#lh-wire-mask)">
    <use href="#path-teal" fill="none" stroke="#0494a4" stroke-width="1"/>
    <use href="#path-navy" fill="none" stroke="#0494a4" stroke-width="1"/>
  </g>
  <g class="lh-solid" mask="url(#lh-solid-mask)">
    <use href="#path-teal" stroke="none" fill="#0494a4"/>
    <use href="#path-navy" stroke="none" fill="#040c24"/>
  </g>
  <rect class="lh-top" x="0" y="52" width="300" height="6" fill="url(#lh-beam)"/>
  <rect class="lh-bot" x="0" y="52" width="300" height="6" fill="url(#lh-beam)"/>
</svg>
```

## Notes

- **Bare `<path>` defs in `<defs>`** so `.lh-wire` `<use fill="none">` renders strictly as hairline strokes.
- Stagger `#lh-solid-mask` `begin` by `+0.28s` behind `#lh-wire-mask` so a visible wireframe frontier rides just ahead of the rising solid fills, then fade `.lh-wire` to `0`.
