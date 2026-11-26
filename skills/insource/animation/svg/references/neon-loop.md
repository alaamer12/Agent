# Recipe: neon-loop — `/animation svg neon-loop`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

The ambient infinite counterpart to one-shot `neon` flicker-on. Keeps fills steadily lit over `#0a0a12` with `sRGB` soft halo and realistic brief opacity dips twice per cycle.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <filter id="..." x="-20%" y="-25%" width="140%" height="150%" color-interpolation-filters="sRGB">
      <feGaussianBlur stdDeviation="2.2" result="halo"/>
      <feMerge>
        <feMergeNode in="halo"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <style>
    .nl-tube { animation: tube-hum 4.8s linear infinite; }
    @keyframes tube-hum {
      0%, 44%, 48%, 52%, 88%, 92%, 100% { opacity: 1; }
      46% { opacity: 0.62; }
      50% { opacity: 0.82; }
      90% { opacity: 0.45; }
    }
    @media (prefers-reduced-motion: reduce) {
      .nl-tube { animation: none; opacity: 1; }
    }
  </style>

  <rect width="300" height="110" fill="#0a0a12"/>
  <g class="nl-tube" filter="url(#nloop-glow)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- Set `color-interpolation-filters="sRGB"` on `#nloop-glow` and clamp `stdDeviation ≤ min(F/2, W/120)` (`2.2` on 300×110).
- Keep the logo at `opacity: 1` for >85% of the cycle so the blinks read as authentic neon ballast flutter rather than a strobe.
