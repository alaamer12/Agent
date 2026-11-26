# Recipe: wave-h — `/animation svg wave-h`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `ripple` (isotropic water turbulence). Stretches `feTurbulence` into long horizontal striations (`baseFrequency="0.008 0.085"`) so the artwork wavers like desert heat mirage.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <filter id="..." x="-12%" y="-5%" width="124%" height="110%" color-interpolation-filters="sRGB">
      <feTurbulence type="fractalNoise" baseFrequency="0.008 0.085" numOctaves="1" seed="..." result="hnoise">
        <animate attributeName="baseFrequency" values="0.008 0.085;0.006 0.055;0.004 0.025" dur="1.5s" fill="freeze"
                 keyTimes="0;0.5;1"/>
      </feTurbulence>
      <feDisplacementMap in="SourceGraphic" in2="hnoise" xChannelSelector="R" yChannelSelector="R" scale="5">
        <animate attributeName="scale" values="5;3;0" dur="1.5s" fill="freeze"
                 calcMode="spline" keyTimes="0;0.45;1" keySplines="0.3 0 0.4 1;0.3 0 0.2 1"/>
      </feDisplacementMap>
    </filter>
    <style>
      .logo { opacity: 0; animation: wh-in 1.5s linear forwards; }
      @keyframes wh-in { 0% { opacity: 0; } 16% { opacity: 1; } 100% { opacity: 1; } }
      @media (prefers-reduced-motion: reduce) { .logo { animation: none; opacity: 1; filter: none; } }
    </style>
  </defs>

  <g class="logo" filter="url(#waveh-fx)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Equal-cardinality 2-value `baseFrequency` stops** (`"0.008 0.085;0.006 0.055;0.004 0.025"`) — mixing 1-value and 2-value stops kills SMIL interpolation silently (foundations §6).
- Always set `color-interpolation-filters="sRGB"` and settle `scale` to exact `0` (`values="5;3;0"`).
