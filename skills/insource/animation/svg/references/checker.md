# Recipe: checker — `/animation svg checker`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `mosaic` (jittered directional wave across 90 tiles). Here tiles split strictly into two rhythmic beats by `(row + col) % 2`.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <mask id="..." maskUnits="userSpaceOnUse" x="-5" y="-5" width="310" height="120">
      <rect x="-5" y="-5" width="310" height="120" fill="#000"/>
      <rect x="0.0" y="0.0" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.06s" fill="freeze"/></rect>
      <rect x="30.0" y="0.0" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.44s" fill="freeze"/></rect>
      <rect x="60.0" y="0.0" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.06s" fill="freeze"/></rect>
      <rect x="90.0" y="0.0" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.44s" fill="freeze"/></rect>
      <rect x="120.0" y="0.0" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.06s" fill="freeze"/></rect>
      <rect x="150.0" y="0.0" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.44s" fill="freeze"/></rect>
      <rect x="180.0" y="0.0" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.06s" fill="freeze"/></rect>
      <rect x="210.0" y="0.0" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.44s" fill="freeze"/></rect>
      <rect x="240.0" y="0.0" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.06s" fill="freeze"/></rect>
      <rect x="270.0" y="0.0" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.44s" fill="freeze"/></rect>
      <rect x="0.0" y="27.5" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.44s" fill="freeze"/></rect>
      <rect x="30.0" y="27.5" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.06s" fill="freeze"/></rect>
      <rect x="60.0" y="27.5" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.44s" fill="freeze"/></rect>
      <rect x="90.0" y="27.5" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.06s" fill="freeze"/></rect>
      <rect x="120.0" y="27.5" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.44s" fill="freeze"/></rect>
      <rect x="150.0" y="27.5" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.06s" fill="freeze"/></rect>
      <rect x="180.0" y="27.5" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.44s" fill="freeze"/></rect>
      <rect x="210.0" y="27.5" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.06s" fill="freeze"/></rect>
      <rect x="240.0" y="27.5" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.44s" fill="freeze"/></rect>
      <rect x="270.0" y="27.5" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.06s" fill="freeze"/></rect>
      <rect x="0.0" y="55.0" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.06s" fill="freeze"/></rect>
      <rect x="30.0" y="55.0" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.44s" fill="freeze"/></rect>
      <rect x="60.0" y="55.0" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.06s" fill="freeze"/></rect>
      <rect x="90.0" y="55.0" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.44s" fill="freeze"/></rect>
      <rect x="120.0" y="55.0" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.06s" fill="freeze"/></rect>
      <rect x="150.0" y="55.0" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.44s" fill="freeze"/></rect>
      <rect x="180.0" y="55.0" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.06s" fill="freeze"/></rect>
      <rect x="210.0" y="55.0" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.44s" fill="freeze"/></rect>
      <rect x="240.0" y="55.0" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.06s" fill="freeze"/></rect>
      <rect x="270.0" y="55.0" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.44s" fill="freeze"/></rect>
      <rect x="0.0" y="82.5" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.44s" fill="freeze"/></rect>
      <rect x="30.0" y="82.5" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.06s" fill="freeze"/></rect>
      <rect x="60.0" y="82.5" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.44s" fill="freeze"/></rect>
      <rect x="90.0" y="82.5" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.06s" fill="freeze"/></rect>
      <rect x="120.0" y="82.5" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.44s" fill="freeze"/></rect>
      <rect x="150.0" y="82.5" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.06s" fill="freeze"/></rect>
      <rect x="180.0" y="82.5" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.44s" fill="freeze"/></rect>
      <rect x="210.0" y="82.5" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.06s" fill="freeze"/></rect>
      <rect x="240.0" y="82.5" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.44s" fill="freeze"/></rect>
      <rect x="270.0" y="82.5" width="30.4" height="27.9" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.38s" begin="0.06s" fill="freeze"/></rect>
    </mask>
    <style>
      @media (prefers-reduced-motion: reduce) { .logo { mask: none; } }
    </style>
  </defs>

  <g class="logo" mask="url(#checker-mask)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Cell size clamped to `≥ 4·F`** (30×27.5u on 300×110, 40 tiles total). Add `+0.4u` width/height overlap so fractional zoom never shows a hairline grid between parity sets.
- **Two-beat rhythm**: set even `begin="0.06s"` and odd `begin="0.44s"` with `dur="0.38s"` so beat two lands just as beat one settles.
- Every mask tile is explicit `fill="#fff"` over a black base rect (foundations §6).
