# Recipe: prism — `/animation svg prism`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `chroma` (spatial RGB ghost split requiring a dark stage) and `polarity` (difference inversion). A skewed spectral rainbow band sweeps across a `feColorMatrix type='hueRotate'` pass inside an isolated group, then crossfades to the exact unfiltered brand artwork.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <clipPath id="...">
      <use href="#path-teal"/>
      <use href="#path-navy"/>
    </clipPath>
    <linearGradient id="..." x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#ff3b30" stop-opacity="0"/>
      <stop offset="18%" stop-color="#ff3b30" stop-opacity="0.85"/>
      <stop offset="36%" stop-color="#ffcc00" stop-opacity="0.9"/>
      <stop offset="52%" stop-color="#34c759" stop-opacity="0.85"/>
      <stop offset="68%" stop-color="#00c7be" stop-opacity="0.9"/>
      <stop offset="84%" stop-color="#5856d6" stop-opacity="0.85"/>
      <stop offset="100%" stop-color="#af52de" stop-opacity="0"/>
    </linearGradient>
    <filter id="..." x="0%" y="0%" width="100%" height="100%" color-interpolation-filters="sRGB">
      <feColorMatrix type="hueRotate" values="0">
        <animate attributeName="values" values="0;180;360" dur="1.5s" fill="freeze" keyTimes="0;0.5;1"/>
      </feColorMatrix>
    </filter>
    <mask id="..." maskUnits="userSpaceOnUse" x="-5" y="-5" width="310" height="120">
      <rect x="-5" y="-5" width="310" height="120" fill="#000"/>
      <rect x="-5" y="-5" width="0" height="120" fill="#fff">
        <animate attributeName="width" values="0;310" dur="1.35s" fill="freeze"
                 calcMode="spline" keyTimes="0;1" keySplines="0.3 0 0.35 1"/>
      </rect>
    </mask>
  </defs>

  <style>
    .prism-hue-layer { animation: prism-hue-out 0.35s linear 1.15s forwards; }
    .prism-solid { opacity: 0; animation: prism-solid-in 0.35s linear 1.15s forwards; }
    .prism-band {
      mix-blend-mode: screen;
      transform: translateX(-110px) skewX(-18deg);
      animation: prism-sweep 1.45s cubic-bezier(0.3, 0, 0.35, 1) forwards;
    }
    @keyframes prism-hue-out { to { opacity: 0; } }
    @keyframes prism-solid-in { to { opacity: 1; } }
    @keyframes prism-sweep {
      from { transform: translateX(-110px) skewX(-18deg); }
      to   { transform: translateX(350px) skewX(-18deg); }
    }
    @media (prefers-reduced-motion: reduce) {
      .prism-wrap { mask: none; }
      .prism-hue-layer { animation: none; opacity: 0; filter: none; }
      .prism-solid { animation: none; opacity: 1; }
      .prism-band { animation: none; opacity: 0; }
    }
  </style>

  <g style="isolation: isolate">
    <g class="prism-wrap" mask="url(#prism-reveal)">
      <g class="prism-hue-layer" filter="url(#prism-hue)">
        <use href="#path-teal"/>
        <use href="#path-navy"/>
      </g>
      <g class="prism-solid">
        <use href="#path-teal"/>
        <use href="#path-navy"/>
      </g>
    </g>
    <g clip-path="url(#prism-logo)">
      <rect class="prism-band" x="0" y="-10" width="95" height="130" fill="url(#prism-grad)"/>
    </g>
  </g>
</svg>
```

## Notes

- **Always set `style="isolation: isolate"` on the outer `<g>`** so `mix-blend-mode: screen` on `.prism-band` blends strictly against the logo artwork and never bleaches against a white page background.
- **Always set `color-interpolation-filters="sRGB"`** on `#prism-hue` (foundations §6), and crossfade `.prism-hue-layer` out to `opacity: 0` over `.prism-solid` so the final frame is pixel-exact with zero filter rounding drift.
- **Clip the rainbow band to the logo union (`clip-path="url(#prism-logo)"`)** so colour never bleeds into letterform counters or surrounding transparent canvas.
- Works cleanly on both light and dark stages.
