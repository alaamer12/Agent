# Recipe: glitch — `/animation svg glitch`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `crt` (vertical opening scanline band) and `chroma` (smooth RGB channel separation on a dark stage). Five horizontal clipped slices snap through stepped (`steps(1, end)`) micro-offsets before locking cleanly into exact registration.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="0" y="0" width="300" height="22.25"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="0" y="22" width="300" height="22.25"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="0" y="44" width="300" height="22.25"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="0" y="66" width="300" height="22.25"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="0" y="88" width="300" height="22"/></clipPath>
  </defs>

  <style>
    .gl0 { clip-path: url(#gl-0); opacity: 0; animation: gl-snap-0 1.05s steps(1, end) forwards; }
    @keyframes gl-snap-0 {
      0%   { transform: translateX(3.2px); opacity: 0; }
      12%  { transform: translateX(3.2px); opacity: 0.9; }
      28%  { transform: translateX(-2.6px); opacity: 1; }
      46%  { transform: translateX(1.8px); opacity: 0.85; }
      64%  { transform: translateX(-1.0px); opacity: 1; }
      80%  { transform: translateX(0px); opacity: 1; }
      100% { transform: translateX(0px); opacity: 1; }
    }
    .gl1 { clip-path: url(#gl-1); opacity: 0; animation: gl-snap-1 1.05s steps(1, end) forwards; }
    @keyframes gl-snap-1 {
      0%   { transform: translateX(-3.0px); opacity: 0; }
      12%  { transform: translateX(-3.0px); opacity: 0.9; }
      28%  { transform: translateX(2.8px); opacity: 1; }
      46%  { transform: translateX(-1.6px); opacity: 0.85; }
      64%  { transform: translateX(0.8px); opacity: 1; }
      80%  { transform: translateX(0px); opacity: 1; }
      100% { transform: translateX(0px); opacity: 1; }
    }
    .gl2 { clip-path: url(#gl-2); opacity: 0; animation: gl-snap-2 1.05s steps(1, end) forwards; }
    @keyframes gl-snap-2 {
      0%   { transform: translateX(3.4px); opacity: 0; }
      12%  { transform: translateX(3.4px); opacity: 0.9; }
      28%  { transform: translateX(-3.2px); opacity: 1; }
      46%  { transform: translateX(2.0px); opacity: 0.85; }
      64%  { transform: translateX(-1.2px); opacity: 1; }
      80%  { transform: translateX(0px); opacity: 1; }
      100% { transform: translateX(0px); opacity: 1; }
    }
    .gl3 { clip-path: url(#gl-3); opacity: 0; animation: gl-snap-3 1.05s steps(1, end) forwards; }
    @keyframes gl-snap-3 {
      0%   { transform: translateX(-2.8px); opacity: 0; }
      12%  { transform: translateX(-2.8px); opacity: 0.9; }
      28%  { transform: translateX(2.4px); opacity: 1; }
      46%  { transform: translateX(-1.4px); opacity: 0.85; }
      64%  { transform: translateX(0.6px); opacity: 1; }
      80%  { transform: translateX(0px); opacity: 1; }
      100% { transform: translateX(0px); opacity: 1; }
    }
    .gl4 { clip-path: url(#gl-4); opacity: 0; animation: gl-snap-4 1.05s steps(1, end) forwards; }
    @keyframes gl-snap-4 {
      0%   { transform: translateX(2.6px); opacity: 0; }
      12%  { transform: translateX(2.6px); opacity: 0.9; }
      28%  { transform: translateX(-2.0px); opacity: 1; }
      46%  { transform: translateX(1.2px); opacity: 0.85; }
      64%  { transform: translateX(-0.6px); opacity: 1; }
      80%  { transform: translateX(0px); opacity: 1; }
      100% { transform: translateX(0px); opacity: 1; }
    }
    @media (prefers-reduced-motion: reduce) {
      .gl0, .gl1, .gl2, .gl3, .gl4 { animation: none; opacity: 1; transform: none; }
    }
  </style>

  <g class="gl0"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="gl1"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="gl2"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="gl3"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="gl4"><use href="#path-teal"/><use href="#path-navy"/></g>
</svg>
```

## Notes

- **Clamp horizontal slice offsets to edge clearance** (foundations §5). On 300×110 (`x_min ≈ 3.8`, `x_max ≈ 295.8`), cap peak displacement at `±0.012·W` (`±3.4px`) so slices jitter visibly without getting sheared off by the SVG viewport.
- **`steps(1, end)` is the effect.** Replacing it with linear or cubic-bezier turns this into `zipper`.
- Add `+0.25u` vertical overlap on interior `<clipPath>` bands so resting horizontal seams never appear at fractional zoom, and end every slice at `translateX(0px); opacity: 1` by 80% so the lock feels decisive.
