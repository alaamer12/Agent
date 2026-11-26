# Recipe: marquee — `/animation svg marquee`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Infinite ambient loop. Distinct from `comet` (single long glowing spark with dim fills) and `loading-loop` (never fills). Keeps full-strength solid fills underneath while a crisp short-period dash marches seamlessly around every subpath.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." fill-rule="evenodd"/>
    <path id="..." d="..." fill-rule="evenodd"/>
  </defs>

  <style>
    .mq-dash {
      fill: none;
      stroke: #ffffff;
      stroke-opacity: 0.75;
      stroke-width: 1;
      stroke-dasharray: 8 6;
      animation: mq-march 1.2s linear infinite;
    }
    @keyframes mq-march {
      from { stroke-dashoffset: 14; }
      to   { stroke-dashoffset: 0; }
    }
    @media (prefers-reduced-motion: reduce) {
      .mq-dash { animation: none; opacity: 0; }
    }
  </style>

  <g>
    <use href="#path-teal" stroke="none" fill="#0494a4"/>
    <use href="#path-navy" stroke="none" fill="#040c24"/>
  </g>
  <g class="mq-dash">
    <use href="#path-teal" fill="none"/>
    <use href="#path-navy" fill="none"/>
  </g>
</svg>
```

## Notes

- **Seamless wrap rule**: set `@keyframes` `stroke-dashoffset` from `dash + gap` (`8 + 6 = 14`) down to `0` with `linear infinite` so the cycle wraps with zero jump.
- Use bare `<path>` defs in `<defs>` so the solid `<use>` carries verbatim original fills while `.mq-dash` `<use fill="none">` draws only the marching outline.
