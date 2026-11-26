# Recipe: orbit — `/animation svg orbit`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `chroma` (RGB additive decomposition on a dark stage) and `assemble` (clipped rectangular tiles). Each original path layer enters along an opposing curved arc and locks into exact print-plate registration.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
  </defs>

  <style>
    .orb-0 { opacity: 0; animation: orb-arc-0 1.2s cubic-bezier(0.22, 0.85, 0.28, 1) forwards; }
    .orb-1 { opacity: 0; animation: orb-arc-1 1.2s cubic-bezier(0.22, 0.85, 0.28, 1) 0.06s forwards; }
    @keyframes orb-arc-0 {
      0%   { transform: translate(-14px, 10px); opacity: 0; }
      28%  { opacity: 1; }
      58%  { transform: translate(3px, -4px); }
      100% { transform: translate(0px, 0px); opacity: 1; }
    }
    @keyframes orb-arc-1 {
      0%   { transform: translate(12px, -8px); opacity: 0; }
      28%  { opacity: 1; }
      58%  { transform: translate(-2.5px, 3px); }
      100% { transform: translate(0px, 0px); opacity: 1; }
    }
    @media (prefers-reduced-motion: reduce) {
      .orb-0, .orb-1 { animation: none; opacity: 1; transform: none; }
    }
  </style>

  <g class="orb-0"><use href="#path-teal"/></g>
  <g class="orb-1"><use href="#path-navy"/></g>
</svg>
```

## Notes

- **Scales to the source's actual path count** (foundations §4): assign each `<path>` layer an alternating initial offset `(±dx, ∓dy)` with `dx ≈ 0.045·W`, `dy ≈ 0.08·H`, plus a perpendicular mid-keyframe (`58%`) so the motion curves instead of sliding linearly.
- **Single-path logos**: if the source SVG has only one `<path>`, split into two vertical or horizontal `<clipPath>` halves (like `zipper`) so two layers still converge cleanly.
- Keep mid-arc overshoot strictly within edge clearance (`≤ 3px` on 300×110) and land every layer at `translate(0, 0)`.
