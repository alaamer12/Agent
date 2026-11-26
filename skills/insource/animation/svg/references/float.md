# Recipe: float — `/animation svg float`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Infinite ambient loop. Distinct from `pulse` (scale/glow) and `pendulum` (one-shot damped swing). Weightless sinusoidal micro-levitation with a subtle counter-tilt for calm hero marks.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
  </defs>

  <style>
    .float-logo {
      transform-box: view-box;
      transform-origin: 150px 55px;
      animation: zero-g 3.6s ease-in-out infinite;
    }
    @keyframes zero-g {
      0%   { transform: translateY(0px) rotate(0deg); }
      25%  { transform: translateY(-1.8px) rotate(-0.35deg); }
      50%  { transform: translateY(0px) rotate(0deg); }
      75%  { transform: translateY(1.6px) rotate(0.35deg); }
      100% { transform: translateY(0px) rotate(0deg); }
    }
    @media (prefers-reduced-motion: reduce) {
      .float-logo { animation: none; transform: none; }
    }
  </style>

  <g class="float-logo">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Derive vertical travel directly from edge clearance** (foundations §5). On 300×110 (`y_min ≈ 4`, `y_max ≈ 108`), downward travel has only `2px` of margin — clamp amplitude to `-1.8px / +1.6px` and tilt to `±0.35deg`. On logos with generous padding (`≥ 10%`), travel can scale up to `±0.025·H` and `±1.0deg`.
- Keep easing `ease-in-out` across a symmetric 4-quarter cycle (`0% → 25% → 50% → 75% → 100%`) so turnarounds feel weightless rather than bouncy.
- Duration `3.6s` at small scale; scale per foundations §5 loop row.
