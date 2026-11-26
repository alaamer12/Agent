# Recipe: slash — `/animation svg slash`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `curtain` (vertical centre split) and `chevron` (single directional wedge). Two complementary diagonal half-planes slide in from opposite corners inside a `<mask>` and meet flush along the main diagonal.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <mask id="..." maskUnits="userSpaceOnUse" x="-5" y="-5" width="310" height="120">
      <rect x="-5" y="-5" width="310" height="120" fill="#000"/>
      <polygon class="slash-a" points="-10,-10 315,-10 -10,120" fill="#fff"/>
      <polygon class="slash-b" points="315,-12 315,120 -12,120" fill="#fff"/>
    </mask>
  </defs>

  <style>
    .slash-a {
      transform: translate(-310px, -115px);
      animation: slash-in-a 1.0s cubic-bezier(0.22, 0.85, 0.28, 1) forwards;
    }
    .slash-b {
      transform: translate(310px, 115px);
      animation: slash-in-b 1.0s cubic-bezier(0.22, 0.85, 0.28, 1) forwards;
    }
    @keyframes slash-in-a { to { transform: translate(0px, 0px); } }
    @keyframes slash-in-b { to { transform: translate(0px, 0px); } }
    @media (prefers-reduced-motion: reduce) {
      .logo { mask: none; }
      .slash-a, .slash-b { animation: none; transform: none; }
    }
  </style>

  <g class="logo" mask="url(#slash-mask)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Overlap the shared diagonal seam by ≥ 2u** (e.g., upper triangle `(W+15, -10) → (-10, H+10)` and lower triangle `(W+15, -12) → (-12, H+10)`). Exact mathematical abutment produces an antialiased hairline seam on fractional zoom.
- **Start offsets**: `(-W - 10, -H - 5)` and `(+W + 10, +H + 5)` guarantee both triangles begin fully outside the mask region before sliding in.
- Both halves land at `translate(0, 0)` with `fill="#fff"`, leaving 100% of the mask solid white and 0.00% end drift.
