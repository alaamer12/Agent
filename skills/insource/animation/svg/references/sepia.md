# Recipe: sepia — `/animation svg sepia`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `colorize` (hard/soft grayscale spatial wipe) and `exposure` (brightness flash). Pure CSS `sepia(1) → sepia(0)` chromatic warmth transition across the whole artwork.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
  </defs>

  <style>
    .sepia-logo { opacity: 0; animation: sepia-warm 1.45s cubic-bezier(0.25, 0.8, 0.3, 1) forwards; }
    @keyframes sepia-warm {
      0%   { filter: sepia(1) contrast(0.85) brightness(1.12); opacity: 0; }
      24%  { filter: sepia(1) contrast(0.92) brightness(1.06); opacity: 1; }
      100% { filter: sepia(0) contrast(1) brightness(1); opacity: 1; }
    }
    @media (prefers-reduced-motion: reduce) {
      .sepia-logo { animation: none; opacity: 1; filter: none; }
    }
  </style>

  <g class="sepia-logo">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Zero filter-region overhead**: CSS `sepia()`, `contrast()`, and `brightness()` never expand pixel bounds, so edge clearance is untouched.
- Slight initial `brightness(1.12) contrast(0.85)` prevents dark navy fills from looking muddy under sepia before landing at exact `1 / 1 / 0`.
