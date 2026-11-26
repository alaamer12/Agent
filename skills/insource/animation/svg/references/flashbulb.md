# Recipe: flashbulb — `/animation svg flashbulb`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `exposure` (monotonic slow darkroom fade-down). Fires an instant strobe peak (`10%`) followed by a realistic retinal afterimage dip (`brightness(0.72)` at `36%`) and recovery.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
  </defs>

  <style>
    .flash-logo { opacity: 0; animation: strobe-burst 1.2s cubic-bezier(0.22, 0.85, 0.3, 1) forwards; }
    @keyframes strobe-burst {
      0%   { filter: brightness(3.2) saturate(0); opacity: 0; }
      10%  { filter: brightness(3.0) saturate(0.1); opacity: 1; }
      36%  { filter: brightness(0.72) saturate(1.15); }
      66%  { filter: brightness(1.12) saturate(1.02); }
      100% { filter: brightness(1) saturate(1); opacity: 1; }
    }
    @media (prefers-reduced-motion: reduce) {
      .flash-logo { animation: none; opacity: 1; filter: none; }
    }
  </style>

  <g class="flash-logo">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- Pure CSS `filter: brightness() saturate()` shorthand — zero extra filter margins needed and 0.00% end drift.
- The dip below `1.0` (`0.72`) at `36%` is what distinguishes a strobe snap from a soft `exposure` fade.
