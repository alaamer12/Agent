# Recipe: breathe-opacity — `/animation svg breathe-opacity`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Infinite ambient loop. Distinct from `pulse` (scale + blur halo) and `float` (vertical movement). Zero transform and zero blur — ideal for ultra-tight viewBoxes where even 1px of motion risks clipping.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
  </defs>

  <style>
    .bo-logo { animation: calm-lum 4.0s ease-in-out infinite; }
    @keyframes calm-lum {
      0%, 100% { opacity: 1; filter: brightness(1); }
      50%      { opacity: 0.78; filter: brightness(1.12); }
    }
    @media (prefers-reduced-motion: reduce) {
      .bo-logo { animation: none; opacity: 1; filter: none; }
    }
  </style>

  <g class="bo-logo">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- Keep opacity floor ≥ `0.75` (`0.78` here) paired with a gentle `brightness(1.12)` lift at `50%` so the logo stays authoritative while breathing gently.
- Safe on any viewBox, any aspect ratio, and both light and dark stages.
