# Bounce or elastic easing

**ID:** `bounce-easing`  
**Catalog section:** Motion  
**Official modality:** Source

## Definition and empirical evidence

Bounce/elastic easing overshoots a target and rebounds/oscillates before settling. It is expressive in some design systems; evaluate role, frequency, and amount rather than treating bounce as universally wrong.

## Underlying principle and potential harm

Motion can communicate state/feedback and add delight, but irrelevant or repeated animation can distract. A large, long, frequent rebound may pull attention from a task, make routine feedback noisy, or make a control feel unpredictable. These are contextual risks, not inevitable effects of the easing curve.

Interaction-triggered motion may affect users with vestibular sensitivity; WCAG’s animation-from-interactions requirement is Level AAA. This differs from the separate pause/stop/hide rule for prolonged automatic movement.

## Recognition signals

- The element overshoots, rebounds multiple times, settles slowly, or repeats on routine/frequent actions.
- Motion does not explain a state change and competes with the task.
- Keyboard focus/control state is unclear or access to the resulting state is delayed.
- Spring/overshoot curves and keyframes are source clues; inspect rendered amplitude, duration, and frequency.

## Causes to investigate

Possible causes include a playful spring preset applied to every control; bounce added to make routine feedback noticeable; high amplitude/low damping; or expressive hero motion reused in utilitarian workflows.

## Exceptions and false positives

- Playful/expressive contexts may use a restrained bounce for hero moments or key interactions.
- A short user-triggered rebound can express a physical metaphor or meaningful state change.
- A spring setting may render imperceptibly; a small bounce repeated often may still be distracting.
- An easing name alone cannot establish effect or impact.

## Correction guidance

Keep bounce where it expresses character or clarifies an important focused interaction. For routine/frequent actions, reduce amplitude/duration or use conventional easing; remove repeated oscillation without informational value. Make state changes understandable without motion and provide reduced-motion adaptation. Test actual triggers, keyboard/pointer use, and whether motion delays access.

## Independent research references

- [Material Design 3 — Motion system](https://m3.material.io/styles/motion/overview/how-it-works) — expressive overshoot/bounce versus minimal-bounce utilitarian motion.
- [Fluent 2 — Motion](https://fluent2.microsoft.design/motion) — functional/natural/consistent motion, short durations, and no-motion setting.
- [Nielsen Norman Group — Animation and motion in UX](https://www.nngroup.com/articles/animation-purpose-ux) — state feedback, attention, and distraction risks.
- [W3C WAI WCAG 2.2 animation from interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html) — Level AAA non-essential interaction-triggered motion criterion.