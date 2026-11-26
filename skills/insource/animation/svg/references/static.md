# Recipe: static — `/animation svg static`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `grain` (calm fine film dissolve with no movement) and `glitch` (sliced horizontal bands). Pairs anisotropic horizontal snow noise (`baseFrequency="0.12 0.85"`) with stepped horizontal tracking lock.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <filter id="..." x="-5%" y="0%" width="110%" height="100%" color-interpolation-filters="sRGB">
      <feTurbulence type="fractalNoise" baseFrequency="0.12 0.85" numOctaves="1" seed="..." result="rf"/>
      <feColorMatrix in="rf" type="matrix" result="rf-a"
        values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  1 0 0 0 0"/>
      <feComponentTransfer in="rf-a" result="rf-gate">
        <feFuncA type="table" tableValues="0 0.25">
          <animate attributeName="tableValues" values="0 0.25;0.1 0.85;0.4 1;1 1" dur="1.15s" fill="freeze"
                   keyTimes="0;0.35;0.72;1"/>
        </feFuncA>
      </feComponentTransfer>
      <feComposite in="SourceGraphic" in2="rf-gate" operator="in"/>
    </filter>
  </defs>

  <style>
    .rf-wrap { animation: rf-track 0.9s steps(1, end) forwards; }
    @keyframes rf-track {
      0%   { transform: translateX(3px); }
      18%  { transform: translateX(-2.5px); }
      36%  { transform: translateX(2px); }
      54%  { transform: translateX(-1.5px); }
      72%  { transform: translateX(0.8px); }
      88%  { transform: translateX(0px); }
      100% { transform: translateX(0px); }
    }
    @media (prefers-reduced-motion: reduce) {
      .rf-wrap { animation: none; transform: none; filter: none; }
    }
  </style>

  <g class="rf-wrap" filter="url(#rf-static)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- Cap tracking jitter to `±3px` (inside horizontal edge clearance on 300×110) using `steps(1, end)`.
- End `tableValues` on `"1 1"` and `translateX(0px)` so both filter and transform leave 0.00% drift at rest.
