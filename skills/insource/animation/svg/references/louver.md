# Recipe: louver — `/animation svg louver`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

The vertical counterpart to `blinds` (which grows horizontal slats in Y) and distinct from `mosaic` (a 2-D opacity grid). Vertical architectural columns across X each widen from `0` to full column width on a staggered wave.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <mask id="..." maskUnits="userSpaceOnUse" x="-5" y="-5" width="310" height="120">
      <rect x="-5" y="-5" width="310" height="120" fill="#000"/>
      <rect x="0.00" y="-5" width="0" height="120" fill="#fff"><animate attributeName="width" values="0;25.60" dur="0.28s" begin="0.05s" fill="freeze"/></rect>
      <rect x="25.00" y="-5" width="0" height="120" fill="#fff"><animate attributeName="width" values="0;25.60" dur="0.28s" begin="0.11s" fill="freeze"/></rect>
      <rect x="50.00" y="-5" width="0" height="120" fill="#fff"><animate attributeName="width" values="0;25.60" dur="0.28s" begin="0.17s" fill="freeze"/></rect>
      <rect x="75.00" y="-5" width="0" height="120" fill="#fff"><animate attributeName="width" values="0;25.60" dur="0.28s" begin="0.24s" fill="freeze"/></rect>
      <rect x="100.00" y="-5" width="0" height="120" fill="#fff"><animate attributeName="width" values="0;25.60" dur="0.28s" begin="0.30s" fill="freeze"/></rect>
      <rect x="125.00" y="-5" width="0" height="120" fill="#fff"><animate attributeName="width" values="0;25.60" dur="0.28s" begin="0.36s" fill="freeze"/></rect>
      <rect x="150.00" y="-5" width="0" height="120" fill="#fff"><animate attributeName="width" values="0;25.60" dur="0.28s" begin="0.42s" fill="freeze"/></rect>
      <rect x="175.00" y="-5" width="0" height="120" fill="#fff"><animate attributeName="width" values="0;25.60" dur="0.28s" begin="0.48s" fill="freeze"/></rect>
      <rect x="200.00" y="-5" width="0" height="120" fill="#fff"><animate attributeName="width" values="0;25.60" dur="0.28s" begin="0.54s" fill="freeze"/></rect>
      <rect x="225.00" y="-5" width="0" height="120" fill="#fff"><animate attributeName="width" values="0;25.60" dur="0.28s" begin="0.61s" fill="freeze"/></rect>
      <rect x="250.00" y="-5" width="0" height="120" fill="#fff"><animate attributeName="width" values="0;25.60" dur="0.28s" begin="0.67s" fill="freeze"/></rect>
      <rect x="275.00" y="-5" width="0" height="120" fill="#fff"><animate attributeName="width" values="0;25.60" dur="0.28s" begin="0.73s" fill="freeze"/></rect>
    </mask>
    <style>
      @media (prefers-reduced-motion: reduce) { .logo { mask: none; } }
    </style>
  </defs>

  <g class="logo" mask="url(#louver-mask)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Column width `w = W / N`, clamped so `w ≥ 4·F`** (foundations §5). At `N = 12` on a 300px canvas (`w = 25u`), each slat is >5× the 4.84px smallest feature, keeping narrow strokes intact.
- **Add +0.6u overlap to final width** (`values="0;25.60"`) so fractional browser zoom never exposes a 1px vertical hairline seam between adjacent slats.
- **Generate the rects programmatically** with literal `begin` values (`0.05 + 0.68 · i/(N-1)`). Swap `i` for `(N-1-i)` to sweep right-to-left on Arabic/RTL logos.
