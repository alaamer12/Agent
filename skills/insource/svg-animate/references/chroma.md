# Recipe: chroma — `/svg-animate chroma`

Chromatic aberration: the artwork splits into three single-channel ghosts that
slide apart horizontally, then converge and sum back to the exact brand colour
before a solid layer lands. One-shot. Needs a dark stage.

Different from `chrome-liquid`'s sheen, which lays a gradient *over* a finished
logo. Here the artwork itself is decomposed and reassembled.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="path-teal" d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="path-navy" d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
  </defs>

  <style>
    .ch { mix-blend-mode: screen; }
    .split-r { animation: chroma-r   1.26s cubic-bezier(0.3, 0.9, 0.3, 1) forwards,
                          chroma-out 0.54s linear 1.26s forwards; }
    .split-b { animation: chroma-b   1.26s cubic-bezier(0.3, 0.9, 0.3, 1) forwards,
                          chroma-out 0.54s linear 1.26s forwards; }
    .fade  { animation: chroma-out 0.54s linear 1.26s forwards; }
    .solid { opacity: 0; animation: chroma-land 0.54s linear 1.26s forwards; }
    @keyframes chroma-r   { from { transform: translateX(-3px); } to { transform: translateX(0); } }
    @keyframes chroma-b   { from { transform: translateX(3px); }  to { transform: translateX(0); } }
    @keyframes chroma-out { to { opacity: 0; } }
    @keyframes chroma-land{ to { opacity: 1; } }
    @media (prefers-reduced-motion: reduce) {
      .ch { animation: none; opacity: 0; }
      .split-r, .split-b { animation: none; transform: none; }
      .solid { animation: none; opacity: 1; }
    }
  </style>

  <g style="isolation: isolate">
    <rect width="300" height="110" fill="#0a0a12"/>
    <use href="#path-teal" class="ch split-r" fill="rgb(4,0,0)"/>
    <use href="#path-teal" class="ch fade"    fill="rgb(0,148,0)"/>
    <use href="#path-teal" class="ch split-b" fill="rgb(0,0,164)"/>
    <use href="#path-navy" class="ch split-r" fill="rgb(4,0,0)"/>
    <use href="#path-navy" class="ch fade"    fill="rgb(0,12,0)"/>
    <use href="#path-navy" class="ch split-b" fill="rgb(0,0,36)"/>
    <use href="#path-teal" class="solid"/>
    <use href="#path-navy" class="solid"/>
  </g>
</svg>
```

## Notes

- **Channel ghosts must carry ONE channel each, and it must be the path's real
  value.** Per-channel screen is `1-(1-a)(1-b)(1-c)`; with two channels at 0
  that returns the live channel exactly, so three aligned ghosts sum back to
  the brand colour with no fudge. The probe confirmed it visually: the overlapped
  ring came out the same teal as the source.
- **`screen` on a dark stage, not `multiply` on a light one.** Both were built
  and measured. `multiply` with three arbitrary dark ghosts summed to mud — it
  only reconstructs a colour if you work in true subtractive inks. `screen`
  with single channels is exact, so it wins.
- **The `animation` shorthand collision is a real trap.** Declaring the fade
  on `.ch` and the split on `.split-r` means the later shorthand *replaces* the
  animation list entirely — the ghosts never faded, and two stacked
  anti-aliased copies of the same path left 1px slivers inside the counters.
  Each split rule must list both animations itself.
- **Why the ghosts fade out at all:** the solid layer alone is pixel-exact
  (end drift 0.00%); ghosts left stacked underneath it are not (0.51% drift,
  counters flagged). Land the solid, remove the scaffolding.
- **Navy ghosts are dim by physics.** `#040c24` is `rgb(4,12,36)` — three
  near-zero channels on a near-black stage. The wordmark reads as a faint
  silhouette until the solid lands at 70%. That is the intended look; if the
  user wants the split visible on dark artwork, boost the ghost channels and
  accept that the converged moment is no longer colour-exact.
- **`isolation: isolate` goes on the group that CONTAINS the backdrop rect**,
  with the rect as its first child. Isolate a group without the rect and the
  ghosts blend against transparency instead of the stage.
- Offset ±3px, horizontal only — this logo has ~3px of clearance per edge, so
  a vertical split would clip.
- **Verified in Chromium 153 only.**
