# Recipe: exposure — `/animation svg exposure`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `focus` (blur sharpness) and `grain` (noise alpha dissolve). Uses CSS `brightness()` and `contrast()` filters to mimic a darkroom shutter flash settling from overexposed highlights into crisp exact tonal lock.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
  </defs>

  <style>
    .exp-logo { opacity: 0; animation: exp-develop 1.3s cubic-bezier(0.22, 0.8, 0.3, 1) forwards; }
    @keyframes exp-develop {
      0%   { filter: brightness(2.8) contrast(0.35); opacity: 0; }
      18%  { filter: brightness(2.4) contrast(0.45); opacity: 1; }
      62%  { filter: brightness(1.28) contrast(0.88); }
      100% { filter: brightness(1) contrast(1); opacity: 1; }
    }
    @media (prefers-reduced-motion: reduce) {
      .exp-logo { animation: none; opacity: 1; filter: none; }
    }
  </style>

  <g class="exp-logo">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Pure CSS filter shorthand — no `<filter>` element needed.** `brightness()` and `contrast()` interpolate smoothly in Chromium and require zero extra filter region padding because they never expand pixels beyond the geometry.
- **Peak values**: `brightness(2.8) contrast(0.35)` washes midtones and darks into a soft photographic flare without collapsing the silhouette; adjust down to `brightness(2.0)` if the source logo is already pastel/near-white on a light stage.
- Lands at `brightness(1) contrast(1)` with `opacity: 1`, producing exact source colours and zero filled counters.
