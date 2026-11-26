# Recipe: spring — `/animation svg spring`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `drop` (vertical squash/stretch anchored at floor) and `elastic-entrance` (infinite rotation loop). Pure centered horizontal `scaleX` harmonic oscillation.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
  </defs>

  <style>
    .spring-logo {
      transform-box: view-box;
      transform-origin: 150px 55px;
      opacity: 0;
      animation: coil-spring 1.1s cubic-bezier(0.22, 0.85, 0.28, 1) forwards;
    }
    @keyframes coil-spring {
      0%   { transform: scaleX(0.18); opacity: 0; }
      22%  { opacity: 1; }
      52%  { transform: scaleX(1.024); }
      72%  { transform: scaleX(0.986); }
      88%  { transform: scaleX(1.008); }
      100% { transform: scaleX(1); opacity: 1; }
    }
    @media (prefers-reduced-motion: reduce) {
      .spring-logo { animation: none; opacity: 1; transform: none; }
    }
  </style>

  <g class="spring-logo">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Clamp overshoot strictly to the horizontal clearance ceiling**: `scaleX(1.024)` at peak (`52%`), then `0.986 → 1.008 → 1.0` on 300×110 (`x_max ≈ 296`).
- Anchored at `(W/2)px (H/2)px` with `transform-box: view-box`.
