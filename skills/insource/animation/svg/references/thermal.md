# Recipe: thermal — `/animation svg thermal`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `prism` (moving rainbow band) and `posterize` (quantized tone steps). Desaturates artwork luminance and maps it through false-color `feComponentTransfer` R/G/B tables.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <filter id="..." x="0%" y="0%" width="100%" height="100%" color-interpolation-filters="sRGB">
      <feColorMatrix type="saturate" values="0" result="lum"/>
      <feComponentTransfer in="lum">
        <feFuncR type="table" tableValues="0.22 0.85 1 1"/>
        <feFuncG type="table" tableValues="0.04 0.18 0.72 0.98"/>
        <feFuncB type="table" tableValues="0.48 0.25 0.05 0.3"/>
      </feComponentTransfer>
    </filter>
  </defs>

  <style>
    .therm-heat { opacity: 0; animation: therm-cool 1.55s linear forwards; }
    .therm-solid { opacity: 0; animation: therm-land 0.55s ease-out 0.95s forwards; }
    @keyframes therm-cool { 0% { opacity: 0; } 20% { opacity: 1; } 68% { opacity: 1; } 100% { opacity: 0; } }
    @keyframes therm-land { to { opacity: 1; } }
    @media (prefers-reduced-motion: reduce) {
      .therm-heat { animation: none; opacity: 0; filter: none; }
      .therm-solid { animation: none; opacity: 1; }
    }
  </style>

  <g class="therm-heat" filter="url(#thermal-fx)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
  <g class="therm-solid">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **`color-interpolation-filters="sRGB"` mandatory** on `#thermal-fx` (foundations §6).
- Crossfade `.therm-heat` out to `opacity: 0` while `.therm-solid` fades in (`0.95s–1.5s`) so the resting frame carries exact verbatim brand hexes with 0.00% drift.
