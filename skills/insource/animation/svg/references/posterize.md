# Recipe: posterize — `/animation svg posterize`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `grain` (noise alpha threshold) and `engrave` (3-D diffuse lighting). Uses `feComponentTransfer` with equal-cardinality animated `tableValues` to step the artwork from stark 2-tone screenprint blocks through multi-tone bands into exact continuous colour.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <filter id="..." x="0%" y="0%" width="100%" height="100%" color-interpolation-filters="sRGB">
      <feComponentTransfer>
        <feFuncR type="table" tableValues="0 0 0 1 1 1">
          <animate attributeName="tableValues" dur="1.15s" fill="freeze" keyTimes="0;0.45;1"
                   values="0 0 0 1 1 1;0 0 0.45 0.55 1 1;0 0.2 0.4 0.6 0.8 1"/>
        </feFuncR>
        <feFuncG type="table" tableValues="0 0 0 1 1 1">
          <animate attributeName="tableValues" dur="1.15s" fill="freeze" keyTimes="0;0.45;1"
                   values="0 0 0 1 1 1;0 0 0.45 0.55 1 1;0 0.2 0.4 0.6 0.8 1"/>
        </feFuncG>
        <feFuncB type="table" tableValues="0 0 0 1 1 1">
          <animate attributeName="tableValues" dur="1.15s" fill="freeze" keyTimes="0;0.45;1"
                   values="0 0 0 1 1 1;0 0 0.45 0.55 1 1;0 0.2 0.4 0.6 0.8 1"/>
        </feFuncB>
      </feComponentTransfer>
    </filter>
  </defs>

  <style>
    .post-fx { opacity: 0; animation: post-fx-life 1.4s linear forwards; }
    .post-solid { opacity: 0; animation: post-land 0.35s linear 1.05s forwards; }
    @keyframes post-fx-life { 0% { opacity: 0; } 14% { opacity: 1; } 78% { opacity: 1; } 100% { opacity: 0; } }
    @keyframes post-land { to { opacity: 1; } }
    @media (prefers-reduced-motion: reduce) {
      .post-fx { animation: none; opacity: 0; filter: none; }
      .post-solid { animation: none; opacity: 1; }
    }
  </style>

  <g class="post-fx" filter="url(#post-steps)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
  <g class="post-solid">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Equal-cardinality `tableValues` only** (foundations §6). Every stop uses exactly 6 values: `"0 0 0 1 1 1"` (hard 2-tone) → `"0 0 0.45 0.55 1 1"` (3-tone risograph step) → `"0 0.2 0.4 0.6 0.8 1"` (exact linear identity). Mismatched stop lengths fail SMIL interpolation silently.
- **Crossfade to an unfiltered `.post-solid` layer at the end** (`1.05s–1.4s`) and fade `.post-fx` to `0` so exact hex colours land with 0.00% drift.
- Set `color-interpolation-filters="sRGB"` on `#post-steps` (foundations §6) so tonal quantization operates in perceptual sRGB rather than dark-crushed linearRGB.
