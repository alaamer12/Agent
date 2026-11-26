# Recipe: wave-v — `/animation svg wave-v`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

The 90° anisotropic counterpart to `wave-h` and distinct from `ripple`. High X frequency + low Y frequency (`baseFrequency="0.075 0.008"`) mimics looking through reeded architectural glass.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <filter id="..." x="-5%" y="-12%" width="110%" height="124%" color-interpolation-filters="sRGB">
      <feTurbulence type="fractalNoise" baseFrequency="0.075 0.008" numOctaves="1" seed="..." result="vnoise">
        <animate attributeName="baseFrequency" values="0.075 0.008;0.045 0.006;0.02 0.004" dur="1.5s" fill="freeze"
                 keyTimes="0;0.5;1"/>
      </feTurbulence>
      <feDisplacementMap in="SourceGraphic" in2="vnoise" xChannelSelector="G" yChannelSelector="G" scale="4.5">
        <animate attributeName="scale" values="4.5;2.8;0" dur="1.5s" fill="freeze"
                 calcMode="spline" keyTimes="0;0.45;1" keySplines="0.3 0 0.4 1;0.3 0 0.2 1"/>
      </feDisplacementMap>
    </filter>
    <style>
      .logo { opacity: 0; animation: wv-in 1.5s linear forwards; }
      @keyframes wv-in { 0% { opacity: 0; } 16% { opacity: 1; } 100% { opacity: 1; } }
      @media (prefers-reduced-motion: reduce) { .logo { animation: none; opacity: 1; filter: none; } }
    </style>
  </defs>

  <g class="logo" filter="url(#wavev-fx)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- Keep all `baseFrequency` SMIL stops strictly 2-valued (`"0.075 0.008;0.045 0.006;0.02 0.004"`).
- Set `x="-5%" y="-12%" width="110%" height="124%"` with `color-interpolation-filters="sRGB"` and land `scale` at `0`.
