# Recipe: staircase — `/animation svg staircase`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `louver` (columns widening horizontally) and `blinds` (horizontal slats growing downward). Columns grow vertically upward from `y = H + 5` on a staggered wave.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <mask id="..." maskUnits="userSpaceOnUse" x="-5" y="-5" width="310" height="120">
      <rect x="-5" y="-5" width="310" height="120" fill="#000"/>
      <rect x="0.0" y="115" width="30.5" height="0" fill="#fff"><animate attributeName="y" values="115;-5" dur="0.46s" begin="0.04s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/><animate attributeName="height" values="0;120" dur="0.46s" begin="0.04s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/></rect>
      <rect x="30.0" y="115" width="30.5" height="0" fill="#fff"><animate attributeName="y" values="115;-5" dur="0.46s" begin="0.11s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/><animate attributeName="height" values="0;120" dur="0.46s" begin="0.11s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/></rect>
      <rect x="60.0" y="115" width="30.5" height="0" fill="#fff"><animate attributeName="y" values="115;-5" dur="0.46s" begin="0.18s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/><animate attributeName="height" values="0;120" dur="0.46s" begin="0.18s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/></rect>
      <rect x="90.0" y="115" width="30.5" height="0" fill="#fff"><animate attributeName="y" values="115;-5" dur="0.46s" begin="0.26s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/><animate attributeName="height" values="0;120" dur="0.46s" begin="0.26s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/></rect>
      <rect x="120.0" y="115" width="30.5" height="0" fill="#fff"><animate attributeName="y" values="115;-5" dur="0.46s" begin="0.33s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/><animate attributeName="height" values="0;120" dur="0.46s" begin="0.33s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/></rect>
      <rect x="150.0" y="115" width="30.5" height="0" fill="#fff"><animate attributeName="y" values="115;-5" dur="0.46s" begin="0.40s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/><animate attributeName="height" values="0;120" dur="0.46s" begin="0.40s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/></rect>
      <rect x="180.0" y="115" width="30.5" height="0" fill="#fff"><animate attributeName="y" values="115;-5" dur="0.46s" begin="0.47s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/><animate attributeName="height" values="0;120" dur="0.46s" begin="0.47s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/></rect>
      <rect x="210.0" y="115" width="30.5" height="0" fill="#fff"><animate attributeName="y" values="115;-5" dur="0.46s" begin="0.55s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/><animate attributeName="height" values="0;120" dur="0.46s" begin="0.55s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/></rect>
      <rect x="240.0" y="115" width="30.5" height="0" fill="#fff"><animate attributeName="y" values="115;-5" dur="0.46s" begin="0.62s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/><animate attributeName="height" values="0;120" dur="0.46s" begin="0.62s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/></rect>
      <rect x="270.0" y="115" width="30.5" height="0" fill="#fff"><animate attributeName="y" values="115;-5" dur="0.46s" begin="0.69s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/><animate attributeName="height" values="0;120" dur="0.46s" begin="0.69s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/></rect>
    </mask>
    <style>
      @media (prefers-reduced-motion: reduce) { .logo { mask: none; } }
    </style>
  </defs>

  <g class="logo" mask="url(#stair-mask)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Column width `w = W / N ≥ 4·F`** (`N = 10`, `w = 30u` on 300×110) with `+0.5u` width overlap to eliminate vertical seams.
- Animate both `y` (`H+5 → -5`) and `height` (`0 → H+10`) simultaneously with matching spline and `begin` so each column grows smoothly from the floor upward. Reverse `i` for right-to-left RTL sweeps.
