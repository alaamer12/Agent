# Recipe: curtain — `/animation svg curtain`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `crt`, which opens a **horizontal** band from the vertical midpoint with scanlines, and from `iris`, which expands a circle radially. This parts two symmetrical vertical mask halves outward from the horizontal centreline behind a brief vertical seam glint.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <mask id="..." maskUnits="userSpaceOnUse" x="-5" y="-5" width="310" height="120">
      <rect x="-5" y="-5" width="310" height="120" fill="#000"/>
      <rect x="150" y="-5" width="0" height="120" fill="#fff">
        <animate attributeName="x" values="150;-5" dur="0.95s" begin="0.12s" fill="freeze"
                 calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/>
        <animate attributeName="width" values="0;156" dur="0.95s" begin="0.12s" fill="freeze"
                 calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/>
      </rect>
      <rect x="150" y="-5" width="0" height="120" fill="#fff">
        <animate attributeName="width" values="0;156" dur="0.95s" begin="0.12s" fill="freeze"
                 calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/>
      </rect>
    </mask>
  </defs>

  <style>
    .curtain-seam { opacity: 0; animation: seam-flash 0.55s linear 0.05s forwards; }
    @keyframes seam-flash { 0% { opacity: 0; } 18% { opacity: 0.9; } 100% { opacity: 0; } }
    @media (prefers-reduced-motion: reduce) {
      .logo { mask: none; }
      .curtain-seam { animation: none; opacity: 0; }
    }
  </style>

  <g class="logo" mask="url(#curtain-mask)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
  <rect class="curtain-seam" x="149.25" y="0" width="1.5" height="110" fill="#0494a4"/>
</svg>
```

## Notes

- **Overlap the two mask halves slightly past the edges** (`x: W/2 → -5`, `width: 0 → W/2 + 6`) so neither left/right edge nor the centre seam can leave a subpixel gap at fractional DPR.
- **Keep the seam glint in the primary brand colour** and place it *outside* the masked group so it flashes cleanly before the curtain parts. Width `max(1.5, W/200)`.
- **Accumulating mask**: both rects stay frozen at full width (`fill="freeze"`), leaving 0.00% end drift against the source.
- For vertical marks (H > W), rotate the mechanic 90° or route to `crt` instead.
