# Recipe: spark — `/svg-animate spark`

A bright spark travels the width of the logo and the artwork stays lit behind
it, so the reveal reads as something being welded into existence. One-shot.

The skill's first use of **`<animateMotion>`**.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="path-teal" d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="path-navy" d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <radialGradient id="spark-head">
      <stop offset="0%" stop-color="#fff"/><stop offset="45%" stop-color="#fff"/><stop offset="100%" stop-color="#000"/>
    </radialGradient>
    <mask id="spark-mask" maskUnits="userSpaceOnUse" x="-5" y="-5" width="310" height="120">
      <rect x="0" y="0" width="0" height="110" fill="#fff">
        <animate attributeName="width" values="0;300" dur="1.6s" fill="freeze"
                 calcMode="spline" keyTimes="0;1" keySplines="0.25 0 0.35 1"/>
      </rect>
      <circle r="26" fill="url(#spark-head)">
        <animateMotion path="M 0,55 L 300,55" dur="1.6s" fill="freeze"
                       calcMode="spline" keyTimes="0;1" keySplines="0.25 0 0.35 1"/>
      </circle>
    </mask>
  </defs>

  <style>
    .spark-dot { opacity: 0; animation: spark-lamp 1.6s linear forwards; }
    @keyframes spark-lamp { 0% {opacity:0} 6% {opacity:1} 94% {opacity:1} 100% {opacity:0} }
    @media (prefers-reduced-motion: reduce) { .logo { mask: none; } .spark-dot { animation: none; opacity: 0; } }
  </style>

  <g class="logo" mask="url(#spark-mask)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
  <g class="spark-dot">
    <circle r="3" fill="#ffffff" stroke="#0494a4" stroke-width="1.5">
      <animateMotion path="M 0,55 L 300,55" dur="1.6s" fill="freeze"
                     calcMode="spline" keyTimes="0;1" keySplines="0.25 0 0.35 1"/>
    </circle>
  </g>
</svg>
```

## Notes

- **`animateMotion` on its own is not a reveal.** The first build was a masked
  spotlight following a motion path and nothing else: it animated correctly and
  ended with **1% of the artwork visible**, because a moving light has no
  memory. The reveal must *accumulate* — here a growing mask rect — and the
  motion path is the flourish riding its leading edge.
- **Repeat the identical `path`, `dur`, `calcMode` and `keySplines` on every
  `animateMotion`.** The mask bulge and the visible dot are two separate
  elements; matching parameters is the only thing keeping them in step. Any
  drift shows as the spark detaching from the edge it is supposed to be drawing.
- Mask contents are white, as always; the soft head is a `radialGradient` of
  white to black, which is what makes the leading edge round rather than a hard
  cut.
- The dot fades out at 100% so the resting frame is the logo alone.
- Spark size ≈ r/6 of the mask bulge; the bulge radius ≈ H/4.
- **Verified in Chromium 153 only.**
