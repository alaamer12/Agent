# Recipe: xray — `/animation svg xray`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `polarity` (difference-blend travelling band) and `scanner` (wireframe laser pass). Applies an inverted cyan `feColorMatrix` across the full artwork before a mask wipes true colors over it.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <filter id="..." x="0%" y="0%" width="100%" height="100%" color-interpolation-filters="sRGB">
      <feColorMatrix type="matrix"
        values="-0.6 0 0 0 0.72
                0 -0.7 0 0 0.92
                0 0 -0.7 0 0.98
                0 0 0 1 0"/>
    </filter>
    <mask id="..." maskUnits="userSpaceOnUse" x="-5" y="-5" width="310" height="120">
      <rect x="-5" y="-5" width="310" height="120" fill="#000"/>
      <rect x="-5" y="-5" width="0" height="120" fill="#fff">
        <animate attributeName="width" values="0;310" dur="1.05s" begin="0.45s" fill="freeze"
                 calcMode="spline" keyTimes="0;1" keySplines="0.25 0.8 0.3 1"/>
      </rect>
    </mask>
  </defs>

  <style>
    .xray-neg { opacity: 0; animation: xray-life 1.55s linear forwards; }
    @keyframes xray-life { 0% { opacity: 0; } 16% { opacity: 0.9; } 82% { opacity: 0.9; } 100% { opacity: 0; } }
    @media (prefers-reduced-motion: reduce) {
      .xray-neg { animation: none; opacity: 0; filter: none; }
      .xray-pos { mask: none; }
    }
  </style>

  <g class="xray-neg" filter="url(#xray-fx)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
  <g class="xray-pos" mask="url(#xray-solid-mask)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- Set `color-interpolation-filters="sRGB"` on `#xray-fx` and fade `.xray-neg` to `opacity: 0` by `1.55s` as `#xray-solid-mask` finishes covering `0..W`.
- Works cleanly on both light and dark stages because the negative matrix maps near-black strokes to luminous cyan.
