# Recipe: colorize — `/animation svg colorize`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `focus` (sharpness blur) and `engrave` (3-D embossed lighting). Artwork fades in crisp in architectural grayscale (`feColorMatrix type='saturate' values='0'`), then a soft-edged horizontal mask wipes true brand colour left-to-right while the monochrome base dissolves cleanly.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <filter id="..." x="0%" y="0%" width="100%" height="100%" color-interpolation-filters="sRGB">
      <feColorMatrix type="saturate" values="0"/>
    </filter>
    <linearGradient id="..." x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#fff"/>
      <stop offset="82%" stop-color="#fff"/>
      <stop offset="100%" stop-color="#000"/>
    </linearGradient>
    <mask id="..." maskUnits="userSpaceOnUse" x="-5" y="-5" width="310" height="120">
      <rect x="-5" y="-5" width="310" height="120" fill="#000"/>
      <rect x="-420" y="-5" width="420" height="120" fill="url(#colorize-edge)">
        <animate attributeName="x" values="-420;-5" dur="1.25s" begin="0.22s" fill="freeze"
                 calcMode="spline" keyTimes="0;1" keySplines="0.25 0.8 0.3 1"/>
      </rect>
    </mask>
  </defs>

  <style>
    .mono-base { opacity: 0; animation: mono-life 1.5s linear forwards; }
    @keyframes mono-life { 0% { opacity: 0; } 18% { opacity: 0.72; } 82% { opacity: 0.72; } 100% { opacity: 0; } }
    @media (prefers-reduced-motion: reduce) {
      .mono-base { animation: none; opacity: 0; filter: none; }
      .color-top { mask: none; }
    }
  </style>

  <g class="mono-base" filter="url(#mono-gray)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
  <g class="color-top" mask="url(#colorize-mask)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Dismiss the grayscale base (`opacity: 0`) at landing.** Leaving a filtered copy underneath the solid layer risks subpixel edge fringing; fading `.mono-base` out as the wipe completes guarantees 0.00% end drift.
- **Soft-edge mask travel**: make the gradient mask rect wider than the canvas (`width = 1.4·W`) with the fade feather in its leading 18%, animating `x` from `-1.4·W` to `-5` so the full white body covers `0..W` completely at `fill="freeze"`.
- **`color-interpolation-filters="sRGB"`** on `#mono-gray` (foundations §6). Works on both light and dark stages.
