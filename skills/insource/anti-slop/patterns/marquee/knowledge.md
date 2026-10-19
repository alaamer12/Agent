# Auto-scrolling marquee

**ID:** `marquee`  
**Catalog section:** Motion  
**Official modality:** Source

## Definition and empirical evidence

A marquee is a strip of content that moves automatically across the page. WCAG 2.2 SC 2.2.2 requires a mechanism to pause, stop, or hide automatically moving/blinking/scrolling information when it lasts over five seconds alongside other content, unless movement is essential. Automatically updating information has a separate branch with its own control/update-frequency requirements; it has no five-second allowance.

## Underlying principle and potential harm

Movement should serve a user need, and users should control when/how they read. Fast or continuous marquees can make text difficult to read, pass before it is understood, distract from nearby content, and create problems for some assistive-technology users.

## Recognition signals

- Content starts moving without request, loops, lasts over five seconds, or changes while being read.
- Full messages cannot be read comfortably at the actual speed.
- Pause/stop/hide controls are absent, unclear, keyboard-inaccessible, or do not work on touch.
- Distinguish continuous motion from content that updates in place; source CSS animations/timers/live-update logic are clues, not conclusions.

## Causes to investigate

Possible causes include fitting announcements into a narrow space; copying a ticker motif into non-live content; prioritizing movement over reading; or treating content as decorative and omitting controls.

## Exceptions and false positives

- A ticker can convey genuinely time-sensitive information, but “live” does not automatically make movement essential.
- User-started/manual browsing differs from continuous automatic movement.
- The moving-content branch’s conditions include auto-start, more than five seconds, and presentation alongside other content; outside them, motion may still be hard to use.
- A short one-time transition or essential motion may have a legitimate role; assess behavior and controls.

## Correction guidance

Prefer a static list, manually advanced carousel, or in-place updates when continuous motion adds no necessary information. If automatic movement remains, provide clear accessible controls where required; give readers time, stop rotation on keyboard focus/pointer hover where suitable, and respect reduced-motion settings. Reduced-motion support does not replace a required pause/stop/hide control. Test runtime behavior with keyboard, touch, and assistive technology.

## Independent research references

- [W3C WAI WCAG 2.2 Pause, Stop, Hide](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html) — movement and auto-update conditions, essentiality, and user-control requirements.
- [W3C WAI-ARIA APG — Auto-rotating carousel](https://www.w3.org/WAI/ARIA/apg/patterns/carousel/examples/carousel-1-prev-next) — start/stop, focus/hover pause, sufficient reading time, and reduced-motion behavior.
- [MDN `prefers-reduced-motion`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/%40media/prefers-reduced-motion) — detecting the user preference to minimize non-essential motion.