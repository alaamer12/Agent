# Recipe: lantern — `/svg-animate lantern`

A soft round light enters at one side and wanders across the logo, leaving the
artwork revealed in its wake; at the end it blooms to cover everything.
One-shot; ends pixel-exact.

Distinct from `spark` (hard accumulating edge plus a travelling dot) and from
`iris` (a single circle growing from the centre). Here the reveal is one
**moving gradient field** whose radius also changes.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="path-teal" d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="path-navy" d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <radialGradient id="lantern-grad" cx="0.04" cy="0.5" r="0.3">
      <stop offset="0%" stop-color="#fff"/><stop offset="50%" stop-color="#fff"/><stop offset="100%" stop-color="#000"/>
      <animate attributeName="cx" values="0.04;0.95;1.0" dur="1.5s" fill="freeze"
               keyTimes="0;0.72;1" calcMode="spline" keySplines="0.35 0 0.3 1;0.4 0 0.6 1"/>
      <animate attributeName="r" values="0.3;0.36;2.4" dur="1.5s" fill="freeze"
               keyTimes="0;0.72;1" calcMode="spline" keySplines="0.4 0 0.6 1;0.3 0 0.2 1"/>
    </radialGradient>
    <mask id="lantern-mask" maskUnits="userSpaceOnUse" x="-5" y="-5" width="310" height="120">
      <rect x="-5" y="-5" width="310" height="120" fill="url(#lantern-grad)"/>
    </mask>
    <style>
      @media (prefers-reduced-motion: reduce) { .logo { mask: none; } }
    </style>
  </defs>

  <g class="logo" mask="url(#lantern-mask)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Two phases, and the order is the whole design.** `r` must *stay tight while
  `cx` travels*, then bloom in the last ~28%. An earlier build grew the radius
  on a single front-loaded spline and the canvas saturated to white almost
  immediately: measured **one distinct frame**, a reveal nobody could see.
- **`r` must end past twice the farthest normalized corner**, or the resting
  frame is dim. With `cx` parked at 1.0 the left edge sits at normalized
  distance 1.0; the 50% white stop is at `0.5·r`, so `r ≥ 2.0` is the floor.
  `r = 1.55` measured 5.68% end drift — the logo permanently faded on one side.
- Gradient units are `objectBoundingBox` by default, so on a 310 × 120 mask the
  "circle" is an ellipse stretched 2.6:1. That is what makes the light read as
  a sweep across a wide logo rather than a round spotlight; set
  `gradientUnits="userSpaceOnUse"` if you genuinely want a circle.
- Stops at 0% / 50% / 100% give a firm core with a feathered rim. Pull the 50%
  toward 30% for a tighter lamp, toward 70% for a haze.
- Mask contents white, as always — a mask keys on luminance.
- If the user wants the light to *linger* rather than finish, drop the second
  phase and loop `cx` — but that is an idle treatment, not a reveal.
- **Verified in Chromium 153 only.**
