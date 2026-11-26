# Recipe: horizon — `/animation svg horizon`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

The vertical inverse of `crt` (which opens outward from center) and 90° counterpart to `curtain`. Two full-width bands converge from top and bottom onto the horizontal midline.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <mask id="..." maskUnits="userSpaceOnUse" x="-5" y="-5" width="310" height="120">
      <rect x="-5" y="-5" width="310" height="120" fill="#000"/>
      <rect x="-5" y="-5" width="310" height="0" fill="#fff">
        <animate attributeName="height" values="0;62" dur="0.92s" begin="0.06s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/>
      </rect>
      <rect x="-5" y="115" width="310" height="0" fill="#fff">
        <animate attributeName="y" values="115;53" dur="0.92s" begin="0.06s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/>
        <animate attributeName="height" values="0;62" dur="0.92s" begin="0.06s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.22 0.85 0.3 1"/>
      </rect>
    </mask>
  </defs>

  <style>
    .hor-line { opacity: 0; animation: hor-seal 0.55s linear 0.72s forwards; }
    @keyframes hor-seal { 0% { opacity: 0; } 25% { opacity: 0.9; } 100% { opacity: 0; } }
    @media (prefers-reduced-motion: reduce) {
      .logo { mask: none; }
      .hor-line { animation: none; opacity: 0; }
    }
  </style>

  <g class="logo" mask="url(#horizon-mask)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
  <rect class="hor-line" x="0" y="54.25" width="300" height="1.5" fill="#0494a4"/>
</svg>
```

## Notes

- **Center overlap**: animate top height `0 → H/2 + 7` and bottom `y: H+5 → H/2 - 2`, `height: 0 → H/2 + 7` so the horizontal seam closes solidly at any DPR.
- Delay the brand-colored equator glint (`.hor-line`) to fire right as the two halves meet (`0.72s`) and fade to 0.
