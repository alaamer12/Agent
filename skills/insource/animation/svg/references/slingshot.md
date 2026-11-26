# Recipe: slingshot — `/animation svg slingshot`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `sprint` (italic `skewX` brake) and `drop` (vertical squash). Uses horizontal anticipation pullback + damped `translateX` / `scaleX` elastic settling.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
  </defs>

  <style>
    .sling-logo {
      transform-box: view-box;
      transform-origin: 150px 55px;
      opacity: 0;
      animation: sling-snap 1.15s cubic-bezier(0.22, 0.82, 0.28, 1) forwards;
    }
    @keyframes sling-snap {
      0%   { transform: translateX(32px) scaleX(0.95); opacity: 0; }
      24%  { transform: translateX(3.5px) scaleX(0.975); opacity: 1; }
      46%  { transform: translateX(-3.2px) scaleX(1.022); }
      70%  { transform: translateX(1.4px) scaleX(0.992); }
      88%  { transform: translateX(-0.5px) scaleX(1.004); }
      100% { transform: translateX(0px) scaleX(1); opacity: 1; }
    }
    @media (prefers-reduced-motion: reduce) {
      .sling-logo { animation: none; opacity: 1; transform: none; }
    }
  </style>

  <g class="sling-logo">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Strict clearance clamping** (foundations §5): cap peak `scaleX` at `1.022` and post-entrance overshoot at `±3.5px` on 300×110 so outer letterforms never touch the viewport clip edge.
- Keep `opacity` ramping from `0 → 1` during the initial `32px → 3.5px` glide so the entry edge feels smooth rather than cropped.
