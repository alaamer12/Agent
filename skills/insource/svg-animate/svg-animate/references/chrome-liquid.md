# Recipe: chrome-liquid — `/svg-animate liquid`

The signature treatment. Three layered phases in this exact order:

1. Chrome gradient outline draws itself along every path
2. True colors rise bottom-to-top like liquid filling a mold (SMIL mask)
3. Soft diagonal sheen sweeps across the finished logo

Derived from an 1800×1800 reference. Numbers below are that reference's;
scale them per the SKILL.md scaling table.

## Template (hero scale, W=H=1800, two paths)

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1800" viewBox="0 0 1800 1800" version="1.1">
  <defs>
    <linearGradient id="chrome-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%"  stop-color="#e0e0e0" />
      <stop offset="20%" stop-color="#ffffff" />
      <stop offset="45%" stop-color="#909090" />
      <stop offset="50%" stop-color="#505050" />
      <stop offset="55%" stop-color="#909090" />
      <stop offset="80%" stop-color="#ffffff" />
      <stop offset="100%" stop-color="#e0e0e0" />
    </linearGradient>

    <!-- white mask rect slides up over the shape -->
    <mask id="liquid-mask">
      <rect x="0" y="1800" width="1800" height="1800" fill="white">
        <animate attributeName="y" from="1800" to="0" dur="3s" begin="1s"
                 fill="freeze" calcMode="spline" keySplines="0.42 0 0.58 1" />
      </rect>
    </mask>

    <linearGradient id="sheen-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%"   stop-color="white" stop-opacity="0" />
      <stop offset="50%"  stop-color="white" stop-opacity="0.6" />
      <stop offset="100%" stop-color="white" stop-opacity="0" />
    </linearGradient>

    <!-- One def per original path. fill-rule (and every render-relevant
         attribute) MUST live here — the original reference omitted it and
         letterform holes filled in solid. Do not repeat that mistake. -->
    <path id="path-white" d="..." fill-rule="evenodd" />
    <path id="path-blue"  d="..." fill-rule="evenodd" />
  </defs>

  <style>
    .chrome-stroke {
      fill: none;
      stroke: url(#chrome-grad);
      stroke-width: 4;
      stroke-linecap: round;
      stroke-linejoin: round;
      opacity: 0.6;
      filter: drop-shadow(0 0 2px rgba(255,255,255,0.3));
      stroke-dasharray: 10000;
      stroke-dashoffset: 10000;
      animation: draw-stroke 4s ease-out forwards;
    }
    .liquid-fill {
      mask: url(#liquid-mask);
      filter: drop-shadow(0 4px 6px rgba(0,0,0,0.5));
      opacity: 0;
      animation: fade-in-fill 0.5s linear 1s forwards;
    }
    .fill-white { fill: #fafbfb; }
    .fill-blue  { fill: #4a7bf9; }
    .sheen-layer {
      fill: url(#sheen-grad);
      mix-blend-mode: overlay;
      transform: translateX(-3600px) skewX(-20deg);
      animation: sheen-sweep 5s ease-in-out infinite;
      animation-delay: 3s; /* wait for the fill to finish */
    }
    @keyframes draw-stroke { to { stroke-dashoffset: 0; } }
    @keyframes fade-in-fill { to { opacity: 1; } }
    @keyframes sheen-sweep {
      0%   { transform: translateX(-3600px) skewX(-20deg); }
      30%  { transform: translateX(3600px) skewX(-20deg); }
      100% { transform: translateX(3600px) skewX(-20deg); }
    }
  </style>

  <!-- 1. chrome outline -->
  <use href="#path-white" class="chrome-stroke" />
  <use href="#path-blue"  class="chrome-stroke" />

  <!-- 2. liquid rising fill in true colors -->
  <use href="#path-white" class="liquid-fill fill-white" />
  <use href="#path-blue"  class="liquid-fill fill-blue" />

  <!-- 3. sheen, clipped to the union of all shapes -->
  <g clip-path="url(#clip-all)">
    <defs>
      <clipPath id="clip-all">
        <use href="#path-white" />
        <use href="#path-blue" />
      </clipPath>
    </defs>
    <rect class="sheen-layer" width="3600" height="1800" />
  </g>
</svg>
```

## Notes

- **Dash values**: `stroke-dasharray/-offset` must be ≥ the target's longest
  subpath (get it from `extract_paths.py --lengths`). The reference's 10000
  covered its ~3000-unit contours; do not copy it blindly to a much smaller
  or larger logo.
- **Sheen geometry**: rect width = 2×W; translateX runs from −2W to +2W (the
  reference used ±4000/width 4000 for W=1800 — same proportions).
- **Optional dark stage**: the reference sits on a dark radial backdrop:
  `.bg { fill: radial-gradient(circle at center, #2b323b 0%, #000000 100%); }`
  on a full-size rect. Add only if the user wants a dark presentation —
  keep the source's background (usually none) otherwise.
- **`<use>` inherits `fill-rule`** from the referenced def — which is exactly
  why the rule must live on the def, not (only) on the `<use>`.
- SMIL `<animate>` inside `<mask>` drives the liquid rise; CSS drives the
  rest. Both run in all modern browsers; no JS needed.
- Fill colors always come from the ORIGINAL file — `.fill-white`/`.fill-blue`
  are role names from the reference logo; rename to match the actual colors
  (e.g. `.fill-teal`).
