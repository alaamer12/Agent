# Recipe: pixel-step — `/animation svg pixel-step`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `mosaic` (90 smoothly fading wave tiles) and `checker` (2-beat chessboard). Uses instant discrete `<set attributeName="opacity" to="1"/>` snaps ordered radially outward along a spiral.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <mask id="..." maskUnits="userSpaceOnUse" x="-5" y="-5" width="310" height="120">
      <rect x="-5" y="-5" width="310" height="120" fill="#000"/>
      <rect x="150.0" y="37.0" width="38.0" height="37.5" fill="#fff" opacity="0"><set attributeName="opacity" to="1" begin="0.040s"/></rect>
      <rect x="112.5" y="37.0" width="38.0" height="37.5" fill="#fff" opacity="0"><set attributeName="opacity" to="1" begin="0.085s"/></rect>
      <rect x="187.5" y="37.0" width="38.0" height="37.5" fill="#fff" opacity="0"><set attributeName="opacity" to="1" begin="0.130s"/></rect>
      <rect x="112.5" y="0.0" width="38.0" height="37.5" fill="#fff" opacity="0"><set attributeName="opacity" to="1" begin="0.175s"/></rect>
      <rect x="75.0" y="37.0" width="38.0" height="37.5" fill="#fff" opacity="0"><set attributeName="opacity" to="1" begin="0.220s"/></rect>
      <rect x="75.0" y="0.0" width="38.0" height="37.5" fill="#fff" opacity="0"><set attributeName="opacity" to="1" begin="0.265s"/></rect>
      <rect x="150.0" y="0.0" width="38.0" height="37.5" fill="#fff" opacity="0"><set attributeName="opacity" to="1" begin="0.310s"/></rect>
      <rect x="225.0" y="37.0" width="38.0" height="37.5" fill="#fff" opacity="0"><set attributeName="opacity" to="1" begin="0.355s"/></rect>
      <rect x="187.5" y="0.0" width="38.0" height="37.5" fill="#fff" opacity="0"><set attributeName="opacity" to="1" begin="0.400s"/></rect>
      <rect x="37.5" y="0.0" width="38.0" height="37.5" fill="#fff" opacity="0"><set attributeName="opacity" to="1" begin="0.445s"/></rect>
      <rect x="150.0" y="74.0" width="38.0" height="37.5" fill="#fff" opacity="0"><set attributeName="opacity" to="1" begin="0.490s"/></rect>
      <rect x="187.5" y="74.0" width="38.0" height="37.5" fill="#fff" opacity="0"><set attributeName="opacity" to="1" begin="0.535s"/></rect>
      <rect x="112.5" y="74.0" width="38.0" height="37.5" fill="#fff" opacity="0"><set attributeName="opacity" to="1" begin="0.580s"/></rect>
      <rect x="37.5" y="37.0" width="38.0" height="37.5" fill="#fff" opacity="0"><set attributeName="opacity" to="1" begin="0.625s"/></rect>
      <rect x="262.5" y="37.0" width="38.0" height="37.5" fill="#fff" opacity="0"><set attributeName="opacity" to="1" begin="0.670s"/></rect>
      <rect x="225.0" y="0.0" width="38.0" height="37.5" fill="#fff" opacity="0"><set attributeName="opacity" to="1" begin="0.715s"/></rect>
      <rect x="0.0" y="0.0" width="38.0" height="37.5" fill="#fff" opacity="0"><set attributeName="opacity" to="1" begin="0.760s"/></rect>
      <rect x="75.0" y="74.0" width="38.0" height="37.5" fill="#fff" opacity="0"><set attributeName="opacity" to="1" begin="0.805s"/></rect>
      <rect x="225.0" y="74.0" width="38.0" height="37.5" fill="#fff" opacity="0"><set attributeName="opacity" to="1" begin="0.850s"/></rect>
      <rect x="0.0" y="37.0" width="38.0" height="37.5" fill="#fff" opacity="0"><set attributeName="opacity" to="1" begin="0.895s"/></rect>
      <rect x="262.5" y="0.0" width="38.0" height="37.5" fill="#fff" opacity="0"><set attributeName="opacity" to="1" begin="0.940s"/></rect>
      <rect x="37.5" y="74.0" width="38.0" height="37.5" fill="#fff" opacity="0"><set attributeName="opacity" to="1" begin="0.985s"/></rect>
      <rect x="262.5" y="74.0" width="38.0" height="37.5" fill="#fff" opacity="0"><set attributeName="opacity" to="1" begin="1.030s"/></rect>
      <rect x="0.0" y="74.0" width="38.0" height="37.5" fill="#fff" opacity="0"><set attributeName="opacity" to="1" begin="1.075s"/></rect>
    </mask>
    <style>
      @media (prefers-reduced-motion: reduce) { .logo { mask: none; } }
    </style>
  </defs>

  <g class="logo" mask="url(#pstep-mask)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Compute spiral sort key programmatically**: `0.72·dist_norm + 0.28·angle_norm` produces an organic unwinding center-out pop sequence.
- Block size `37.5 × 37u` (`> 7·F`), with `+0.5u` overlap on width/height so zero hairline gaps appear when complete.
