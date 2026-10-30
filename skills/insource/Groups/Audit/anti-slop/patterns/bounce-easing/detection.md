# Detection: Bounce or elastic easing

## Catalog route

The official catalog classifies this as a **source** rule. Easing/animation settings identify candidates; actual motion and context determine whether it is overused or disruptive.

## Candidate signals

1. Locate spring/elastic/back/overshoot curves and repeated animation keyframes.
2. Record affected element, trigger, amplitude, rebounds, duration, and repetition frequency.
3. Observe whether motion communicates a state or delays/competes with the task.
4. Test keyboard/pointer interaction and reduced-motion behavior.

## False-positive controls

- Do not flag all springs or playful easing by name.
- Do not equate a small one-time bounce with prolonged automatic motion.
- Distinguish WCAG Level AAA interaction-triggered animation from automatic-motion controls.

## Test disposition

Source fixtures can find overshoot curves as candidates. Runtime tests should compare restrained one-time feedback, repeated high-amplitude routine motion, and an expressive hero use, including reduced-motion behavior. Regex cannot confirm impact.