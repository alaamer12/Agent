# Match an existing animation

> Owns the recording→frames→tracks→curve pipeline and the measurement reading table; routing lives in `../SKILL.md`.

Recreate an animation from a recording or a reference so the result matches its feel. Applies to any command: a recorded micro interaction, a component animation, a transition.

## When this applies

The user supplies a screen recording, a GIF, a short video, a screenshot sequence, or says "make it feel like this". Run before classification so the measured values seed the options.

## Pipeline

1. **Extract frames.** `python scripts/match/extract_frames.py <video> --out frames/` (needs ffmpeg). Use the frame rate of the source; sample densely around the action.
2. **Track motion.** `python scripts/match/track_motion.py frames/` follows the region of interest and records position, scale and opacity over time (needs opencv-python and numpy).
3. **Fit curves.** `python scripts/match/fit_curves.py <tracks.json>` fits cubic-bezier or spring parameters to the tracked series (needs numpy and scipy). Try springs when there is overshoot or settling oscillation; cubic-bezier otherwise.
4. **Decide the structure.** Identify what animates, in what order (the synchronization form: see synchronization.md), the duration, the delays, and whether the reverse was shown.
5. **Emit code** in the project's stack, using the fitted values.

## Reading the measurements

| Observation | Meaning |
|---|---|
| Fast start, slow end | Ease-out family; check the steepness against the tokens |
| Overshoot then settle | Spring with bounce; estimate bounce from the overshoot ratio |
| Constant speed | Linear |
| Offsets between starts of siblings | Stagger value; check whether it is uniform |
| Opacity lags position | Staggered technique layers: fade starts after the move |
| Different durations per property | Separate timing per property, not one transition |

## Fitting curves

Compare the fitted curve against the nearest token; nearest token wins (see timing-and-tokens.md §Adopting tokens). Report the fitted values and the chosen token with the error. For a spring, report both perceptual (duration, bounce) and physical (stiffness, damping) forms.

## Emitting code

Produce the same output the chosen stack uses: CSS transition or keyframes, Web Animations options, the library's transition object, or native platform parameters. Include the reduced-motion variant and the reverse if the recording shows or implies it (requirements: see review-standards.md). Add a short handoff spec listing the measured values and what was inferred.

## Limits

Frame sampling limits precision: a 30fps recording resolves about 33ms. Compression artifacts blur edges. Record at the highest rate possible, with the screen recorder in a lossless mode if available. State the confidence in the report.

## Manual fallback

Without the scripts: step through the recording frame by frame in a player, note the start and end frame of each property (duration is frames divided by frame rate), estimate the curve by comparing the midpoint progress (if the element is more than 50% done at half the time, it is ease-out), and write the values by hand.
