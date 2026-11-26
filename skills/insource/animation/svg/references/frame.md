# Recipe: frame — `/animation svg frame`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

The spatial inverse of `iris` and `curtain`: reveal starts along the outer viewport edges and closes inward toward the center.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <mask id="..." maskUnits="userSpaceOnUse" x="-5" y="-5" width="310" height="120">
      <rect x="-5" y="-5" width="310" height="120" fill="#000"/>
      <rect x="-5" y="-5" width="310" height="0" fill="#fff">
        <animate attributeName="height" values="0;62" dur="1.05s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.8 0.3 1"/>
      </rect>
      <rect x="-5" y="115" width="310" height="0" fill="#fff">
        <animate attributeName="y" values="115;53" dur="1.05s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.8 0.3 1"/>
        <animate attributeName="height" values="0;62" dur="1.05s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.8 0.3 1"/>
      </rect>
      <rect x="-5" y="-5" width="0" height="120" fill="#fff">
        <animate attributeName="width" values="0;158" dur="1.05s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.8 0.3 1"/>
      </rect>
      <rect x="305" y="-5" width="0" height="120" fill="#fff">
        <animate attributeName="x" values="305;147" dur="1.05s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.8 0.3 1"/>
        <animate attributeName="width" values="0;158" dur="1.05s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.8 0.3 1"/>
      </rect>
    </mask>
    <style>
      @media (prefers-reduced-motion: reduce) { .logo { mask: none; } }
    </style>
  </defs>

  <g class="logo" mask="url(#frame-mask)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Overlap at center**: top/bottom rects expand to `H/2 + 7` (`62u`), left/right rects expand to `W/2 + 8` (`158u`), guaranteeing solid white overlap at the midpoint with zero seam.
- Black base rect inside `<mask>` is mandatory so the interior starts hidden.
