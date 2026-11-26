# Recipe: chevron — `/animation svg chevron`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `polarity` (difference-blend inversion band) and `blinds` (horizontal slats). An arrowhead `<polygon>` sweeps left-to-right inside a `<mask>` and trails a solid white tail behind its point so the reveal accumulates cleanly.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <mask id="..." maskUnits="userSpaceOnUse" x="-5" y="-5" width="310" height="120">
      <rect x="-5" y="-5" width="310" height="120" fill="#000"/>
      <polygon class="chev-shape" points="-420,-5 -55,-5 0,55 -55,115 -420,115" fill="#fff"/>
    </mask>
  </defs>

  <style>
    .chev-shape {
      transform: translateX(0px);
      animation: chev-sweep 1.1s cubic-bezier(0.25, 0.85, 0.3, 1) forwards;
    }
    @keyframes chev-sweep {
      from { transform: translateX(0px); }
      to   { transform: translateX(370px); }
    }
    @media (prefers-reduced-motion: reduce) {
      .logo { mask: none; }
      .chev-shape { animation: none; transform: translateX(370px); }
    }
  </style>

  <g class="logo" mask="url(#chevron-mask)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Tail length must exceed `W + tip_depth`** (`tip_depth ≈ H/2`). If the polygon is only a hollow chevron band, the artwork disappears behind it — violating foundations §6 ("A reveal must accumulate").
- **Tip geometry**: nose at `(0, H/2)`, shoulders at `(-H/2, -5)` and `(-H/2, H+5)`, tail extending to `-(W + H + 10)`. Translate across `W + H/2 + 15` so the shoulders clear `x = W` completely.
- **RTL wordmarks**: flip the tip to point left and translate right-to-left (`from translateX(0)` to `translateX(-(W + H/2 + 15))`) so the spearhead follows reading direction.
