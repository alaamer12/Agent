# Recipe: spotlight — `/animation svg spotlight`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `lantern` (one spotlight sweeping left-to-right). Three soft radial `<circle>` masks converge from top-left, top-right, and bottom-center before expanding to unite.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <radialGradient id="...">
      <stop offset="0%" stop-color="#fff"/>
      <stop offset="65%" stop-color="#fff"/>
      <stop offset="100%" stop-color="#000"/>
    </radialGradient>
    <mask id="..." maskUnits="userSpaceOnUse" x="-5" y="-5" width="310" height="120">
      <rect x="-5" y="-5" width="310" height="120" fill="#000"/>
      <circle cx="30" cy="20" r="35" fill="url(#spot-grad)">
        <animate attributeName="cx" values="25;120;150" dur="1.45s" fill="freeze" keyTimes="0;0.6;1" calcMode="spline" keySplines="0.3 0 0.35 1;0.3 0 0.2 1"/>
        <animate attributeName="cy" values="18;50;55" dur="1.45s" fill="freeze" keyTimes="0;0.6;1" calcMode="spline" keySplines="0.3 0 0.35 1;0.3 0 0.2 1"/>
        <animate attributeName="r" values="26;52;270" dur="1.45s" fill="freeze" keyTimes="0;0.6;1" calcMode="spline" keySplines="0.4 0 0.6 1;0.25 0 0.2 1"/>
      </circle>
      <circle cx="275" cy="20" r="35" fill="url(#spot-grad)">
        <animate attributeName="cx" values="275;180;150" dur="1.45s" fill="freeze" keyTimes="0;0.6;1" calcMode="spline" keySplines="0.3 0 0.35 1;0.3 0 0.2 1"/>
        <animate attributeName="cy" values="18;50;55" dur="1.45s" fill="freeze" keyTimes="0;0.6;1" calcMode="spline" keySplines="0.3 0 0.35 1;0.3 0 0.2 1"/>
        <animate attributeName="r" values="26;52;270" dur="1.45s" fill="freeze" keyTimes="0;0.6;1" calcMode="spline" keySplines="0.4 0 0.6 1;0.25 0 0.2 1"/>
      </circle>
      <circle cx="150" cy="100" r="30" fill="url(#spot-grad)">
        <animate attributeName="cy" values="102;64;55" dur="1.45s" fill="freeze" keyTimes="0;0.6;1" calcMode="spline" keySplines="0.3 0 0.35 1;0.3 0 0.2 1"/>
        <animate attributeName="r" values="22;48;270" dur="1.45s" fill="freeze" keyTimes="0;0.6;1" calcMode="spline" keySplines="0.4 0 0.6 1;0.25 0 0.2 1"/>
      </circle>
    </mask>
    <style>
      @media (prefers-reduced-motion: reduce) { .logo { mask: none; } }
    </style>
  </defs>

  <g class="logo" mask="url(#spot-mask)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Two-phase radius growth (`keyTimes="0;0.6;1"`)**: keep each lamp tight (`r = 22–52`) while travelling inward so three distinct pools read clearly, then bloom past `1.6 × hypot(W/2, H/2)` (`270u`) so the 65% white stop clears every edge with 0.00% drift.
- Explicit black base rect inside `<mask>` keeps unlit regions hidden.
