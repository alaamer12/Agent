# Recipe: solarize — `/animation svg solarize`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `posterize` (stair-step quantization) and `polarity` (spatial difference band). Uses a V-shaped folded `feComponentTransfer` transfer curve that unfolds smoothly to linear identity.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <filter id="..." x="0%" y="0%" width="100%" height="100%" color-interpolation-filters="sRGB">
      <feComponentTransfer>
        <feFuncR type="table" tableValues="0.9 0.2 0.85 0.35 1">
          <animate attributeName="tableValues" dur="1.2s" fill="freeze" keyTimes="0;0.5;1"
                   values="0.9 0.2 0.85 0.35 1;0.45 0.35 0.65 0.65 1;0 0.25 0.5 0.75 1"/>
        </feFuncR>
        <feFuncG type="table" tableValues="0.9 0.2 0.85 0.35 1">
          <animate attributeName="tableValues" dur="1.2s" fill="freeze" keyTimes="0;0.5;1"
                   values="0.9 0.2 0.85 0.35 1;0.45 0.35 0.65 0.65 1;0 0.25 0.5 0.75 1"/>
        </feFuncG>
        <feFuncB type="table" tableValues="0.9 0.2 0.85 0.35 1">
          <animate attributeName="tableValues" dur="1.2s" fill="freeze" keyTimes="0;0.5;1"
                   values="0.9 0.2 0.85 0.35 1;0.45 0.35 0.65 0.65 1;0 0.25 0.5 0.75 1"/>
        </feFuncB>
      </feComponentTransfer>
    </filter>
  </defs>

  <style>
    .sol-fx { opacity: 0; animation: sol-out 1.45s linear forwards; }
    .sol-solid { opacity: 0; animation: sol-in 0.4s linear 1.05s forwards; }
    @keyframes sol-out { 0% { opacity: 0; } 16% { opacity: 1; } 75% { opacity: 1; } 100% { opacity: 0; } }
    @keyframes sol-in { to { opacity: 1; } }
    @media (prefers-reduced-motion: reduce) {
      .sol-fx { animation: none; opacity: 0; filter: none; }
      .sol-solid { animation: none; opacity: 1; }
    }
  </style>

  <g class="sol-fx" filter="url(#solar-fx)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
  <g class="sol-solid">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Equal-cardinality 5-stop `tableValues`** across every SMIL stop (`0.9 0.2 0.85 0.35 1` → `0.45 0.35 0.65 0.65 1` → `0 0.25 0.5 0.75 1`) so Chromium interpolates cleanly without silent failure.
- Set `color-interpolation-filters="sRGB"` and crossfade onto unfiltered `.sol-solid` at `1.05s`.
