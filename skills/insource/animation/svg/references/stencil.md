# Recipe: stencil — `/animation svg stencil`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `blinds` (11 crisp hard-edged slats) and `colorize` (one continuous full-height wipe). Three overlapping soft-feathered horizontal bands sweep left-to-right in succession like real stencil spray passes.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <linearGradient id="..." x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#fff"/>
      <stop offset="78%" stop-color="#fff"/>
      <stop offset="100%" stop-color="#000"/>
    </linearGradient>
    <mask id="..." maskUnits="userSpaceOnUse" x="-5" y="-5" width="310" height="120">
      <rect x="-5" y="-5" width="310" height="120" fill="#000"/>
      <rect x="-360" y="-8" width="360" height="44" fill="url(#spray-grad)">
        <animate attributeName="x" values="-360;-5" dur="0.52s" begin="0.04s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.2 0.8 0.3 1"/>
      </rect>
      <rect x="-360" y="32" width="360" height="46" fill="url(#spray-grad)">
        <animate attributeName="x" values="-360;-5" dur="0.52s" begin="0.34s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.2 0.8 0.3 1"/>
      </rect>
      <rect x="-360" y="74" width="360" height="44" fill="url(#spray-grad)">
        <animate attributeName="x" values="-360;-5" dur="0.52s" begin="0.64s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.2 0.8 0.3 1"/>
      </rect>
    </mask>
    <style>
      @media (prefers-reduced-motion: reduce) { .logo { mask: none; } }
    </style>
  </defs>

  <g class="logo" mask="url(#stencil-mask)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Overlap vertical band edges by ≥ 4u** (`y=-8 h=44`, `y=32 h=46`, `y=74 h=44`) so zero horizontal seams can survive between passes.
- Each mask rect width exceeds `W + feather` (`360u`) and finishes at `x = -5`, leaving the mask 100% solid white.
