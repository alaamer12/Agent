# Pulsing status dot

**ID:** `pulsing-dot`  
**Catalog section:** Motion  
**Official modality:** Source

## Definition and empirical evidence

This pattern is a small status marker with recurring motion (such as a growing/fading ring or changing opacity) used to call attention to a state like live activity or connection. Motion should add useful, time-relevant information, not imply urgency by default.

## Underlying principle and potential harm

Status indicators communicate state/severity; combine cues such as color, shape, symbol, and label rather than relying only on color. A perpetual pulse for routine status may repeatedly distract, make unrelated states appear urgent, or compete with the task.

WCAG has distinct provisions for automatically moving/blinking content over five seconds and for rapidly flashing content. A smooth slow pulse is not automatically a flash, but those criteria require actual effect/timing evaluation. Reduced-motion preferences can signal a need for less non-essential animation.

## Recognition signals

- The dot pulses indefinitely even when the state is routine or unchanged.
- Many unrelated status indicators pulse simultaneously or with the same attention level.
- The pulse’s state meaning is unclear or conveyed by color/motion alone.
- Repeating keyframes/animation iterations and scale/opacity changes are source clues; judge actual rendered motion.
- Dynamic status changes need appropriate programmatic exposure without forcing focus movement.

## Causes to investigate

Possible causes include motion added as generic “live/modern” decoration; every status receiving equal attention; a pulse used where a static cue suffices; or animation not tied to the actual lifecycle of the state.

## Exceptions and false positives

- Live streaming, recording, or connection activity may merit a pulse when the distinction matters.
- A brief change cue can signal a newly active state without indefinite animation.
- A steady icon/label can retain meaning for reduced-motion users.
- A pulse may be purposeful; static indicators can still be ambiguous.
- Flash-frequency and pause/stop/hide requirements are separate; do not treat “under three flashes/sec” as blanket safety for perpetual motion.

## Correction guidance

Confirm the represented state and why motion helps. Replace unnecessary pulses with a static cue. If motion is useful, tie it to the real active state, consider limiting it after a state transition, and provide a reduced-motion alternative that preserves meaning. Pair color with text/symbol and expose dynamic status programmatically without stealing focus. Test rendered animation against applicable WCAG motion/flashing criteria.

## Independent research references

- [Carbon Design System — Status indicators](https://carbondesignsystem.com/patterns/status-indicator-pattern) — status/severity roles, attention levels, and multiple cues.
- [W3C WAI WCAG 2.2 Pause, Stop, Hide](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html) — long-running moving/blinking content and user-control conditions.
- [W3C WAI WCAG 2.2 Quick Reference](https://www.w3.org/WAI/WCAG22/quickref/) — flash criteria and motion-animation criterion level/boundaries.
- [MDN — Media queries for accessibility](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Media_queries/Using_for_accessibility) — `prefers-reduced-motion` adaptations.
- [W3C WAI WCAG 2.2 Status Messages](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html) — dynamic status updates available to assistive technology without focus change.