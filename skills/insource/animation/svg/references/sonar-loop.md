# Recipe: sonar-loop — `/animation svg sonar-loop`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Infinite ambient loop. Distinct from `rings` (one-shot mask reveal) and `stamp` (one-shot impact recoil). Two `<ellipse>` pings staggered by half a period (`1.5s`) radiate cleanly behind the stationary logo.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
  </defs>

  <style>
    .sonar-r1, .sonar-r2 {
      transform-box: view-box;
      transform-origin: 150px 55px;
      opacity: 0;
    }
    .sonar-r1 { animation: sonar-ping 3.0s cubic-bezier(0.15, 0.8, 0.3, 1) infinite; }
    .sonar-r2 { animation: sonar-ping 3.0s cubic-bezier(0.15, 0.8, 0.3, 1) 1.5s infinite; }
    @keyframes sonar-ping {
      0%   { transform: scale(0.42); opacity: 0.65; }
      100% { transform: scale(1.0); opacity: 0; }
    }
    @media (prefers-reduced-motion: reduce) {
      .sonar-r1, .sonar-r2 { animation: none; opacity: 0; }
    }
  </style>

  <ellipse class="sonar-r1" cx="150" cy="55" rx="146" ry="51" fill="none" stroke="#0494a4" stroke-width="1.5"/>
  <ellipse class="sonar-r2" cx="150" cy="55" rx="146" ry="51" fill="none" stroke="#0494a4" stroke-width="1.5"/>
  <g>
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Size ellipses to `(W/2 - 4, H/2 - 4)`** so at `scale(1.0)` the outer stroke never gets clipped by the viewport edge.
- Use `<ellipse>` (or `<circle>` on square icons) — never `<path>` — and draw them *before* the logo `<g>` so pings emerge from behind.
