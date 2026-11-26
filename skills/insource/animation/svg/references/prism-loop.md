# Recipe: prism-loop — `/animation svg prism-loop`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

The calm infinite counterpart to one-shot `prism` and the iridescent twin of `shimmer`. Keeps original brand colors dominant while a low-opacity skewed spectrum glides periodically inside an isolated group.

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
      <stop offset="22%" stop-color="#ff9500" stop-opacity="0.34"/>
      <stop offset="50%" stop-color="#34c759" stop-opacity="0.36"/>
      <stop offset="78%" stop-color="#5856d6" stop-opacity="0.34"/>
      <stop offset="100%" stop-color="#af52de" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <style>
    .pl-bar {
      mix-blend-mode: screen;
      transform: translateX(-110px) skewX(-20deg);
      animation: pl-drift 4.4s cubic-bezier(0.4, 0, 0.2, 1) infinite;
    }
    @keyframes pl-drift {
      0%   { transform: translateX(-110px) skewX(-20deg); }
      38%  { transform: translateX(350px) skewX(-20deg); }
      100% { transform: translateX(350px) skewX(-20deg); }
    }
    @media (prefers-reduced-motion: reduce) {
      .pl-bar { animation: none; opacity: 0; }
    }
  </style>

  <g style="isolation: isolate">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
    <g clip-path="url(#ploop-logo)">
      <rect class="pl-bar" x="0" y="-10" width="90" height="130" fill="url(#ploop-grad)"/>
    </g>
  </g>
</svg>
```

## Notes

- **Wrap in `style="isolation: isolate"`** so `mix-blend-mode: screen` blends strictly with the logo artwork and never washes out against light pages.
- Keep peak gradient stop opacity restrained (`0.34–0.36`) with a 62% idle dwell so the mark stays sophisticated.
