# Recipe: hexagon — `/animation svg hexagon`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `diamond` (4-sided 45° rhombus) and `iris` (circle). A 6-sided regular `<polygon>` inside `<clipPath>` scales up while unwinding 30° into flat-top alignment.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <clipPath id="..." clipPathUnits="userSpaceOnUse">
      <polygon class="hex-poly" points="360.0,55.0 255.0,236.9 45.0,236.9 -60.0,55.0 45.0,-126.9 255.0,-126.9"/>
    </clipPath>
  </defs>

  <style>
    .hex-poly {
      transform-box: view-box;
      transform-origin: 150px 55px;
      transform: scale(0) rotate(-30deg);
      animation: hex-open 1.25s cubic-bezier(0.22, 0.85, 0.28, 1) forwards;
    }
    @keyframes hex-open { to { transform: scale(1) rotate(0deg); } }
    @media (prefers-reduced-motion: reduce) {
      .hex-poly { animation: none; transform: none; }
    }
  </style>

  <g clip-path="url(#hex-clip)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Circumradius floor**: `R ≥ hypot(W/2, H/2) / cos(30°) + 20` (`≈ 205u` on 300×110; template uses `210u`). The inradius `R·cos(30°)` must clear every canvas corner so nothing stays clipped at `scale(1)`.
- **Unwind angle**: `rotate(-30deg) → rotate(0deg)` equals half a face step, giving a subtle mechanical bolt-lock feel without spinning wildly.
- Always pair `transform-box: view-box` with `transform-origin: (W/2)px (H/2)px`.
