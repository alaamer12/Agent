# Decorative blinking cursor

**ID:** `blinking-cursor`  
**Catalog section:** Motion  
**Official modality:** Browser

## Definition and empirical evidence

The catalog flags an animated cursor beside ordinary text when it can imply that the text is editable or terminal output. A blinking caret in a focused editable element is different: it marks where typed/deleted text will go. A blinking cursor is not a problem by appearance alone; identify what it communicates.

## Underlying principle and potential harm

Animation should reflect a real, current function/state. A decorative cursor may distract from copy or falsely suggest editability, typing, or a need for input. WCAG has distinct criteria for automatically blinking information that persists alongside content and for rapidly flashing content; ordinary blinking is not automatically a hazardous flash.

## Recognition signals

- A cursor blinks beside static text with no editable field or terminal behavior.
- It continues indefinitely, even when no typing/activity is occurring.
- A genuine input caret appears only while its editable element is focused and tracks the insertion point.
- Repeating CSS/JS animation, pseudo-elements, or simulated cursor code are clues; verify rendered behavior and reduced-motion preference.

## Causes to investigate

Possible causes include a terminal/typewriter motif added for atmosphere; prototype animation left in static copy; or a native input treatment copied into a non-editable context.

## Exceptions and false positives

- A native caret in a focused input/editor is functional feedback.
- A truthful active-typing indicator can communicate a live state if it stops when activity ends.
- A real editor/terminal cursor should remain tied to actual input behavior.
- A still image or brief animation may look similar; assess actual movement, function, and user interaction.

## Correction guidance

Remove a purely decorative cursor beside static copy or use a non-animated style that does not imply editability. If animation communicates a real state, keep it accurate and limited to that state and provide reduced-motion adaptation for non-essential motion. Preserve native caret feedback for real inputs. Test continuous authored blinking under Pause/Stop/Hide conditions and assess rapid flashing separately; do not infer WCAG failure from appearance alone.

## Independent research references

- [Impeccable Slop catalog](https://impeccable.style/slop) — fake cursor beside static text versus real typing context.
- [MDN `caret-color`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/caret-color) — insertion caret role and focus behavior.
- [W3C WAI WCAG 2.2 Pause, Stop, Hide](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html) — duration/parallel-content conditions for blinking information.
- [W3C WAI WCAG 2.2 flashing](https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html) — separate flash frequency/luminance criteria.
- [MDN `prefers-reduced-motion`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/%40media/prefers-reduced-motion) — user preference for reducing non-essential motion.