# Detection: Auto-scrolling marquee

## Catalog route

The official catalog classifies this as a **source** rule. Animation/timer source is a candidate; actual duration, user controls, essentiality, and reading behavior require runtime review.

## Candidate signals

1. Locate CSS keyframes, scripted timers, autoplay/carousel behavior, and auto-updating content.
2. Observe whether movement starts automatically, lasts over five seconds, loops, or runs beside other content.
3. Test whether a clear pause/stop/hide control is available and works with keyboard/touch.
4. Distinguish moving content from in-place updates and assess the applicable criterion separately.
5. Check reduced-motion adaptation and screen-reader behavior.

## False-positive controls

- Do not flag a user-started animation solely because it moves.
- Do not assume live information makes automatic motion essential.
- Do not treat reduced-motion support as a substitute for required controls.
- A code-level animation match cannot establish readability or impact.

## Test disposition

Source fixtures can identify autoplay/loop behavior; runtime tests must verify duration, pause controls, update frequency, keyboard/touch, and reduced motion. Include a static list and a legitimate user-controlled carousel. Regex cannot confirm.