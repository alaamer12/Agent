# Review standards

> **Connections** (paths are relative to `references/`)
> - Read when: phase 6 of every build, reviewing a spec before showing it, or reviewing existing animation.
> - Skip when: you are only answering a vocabulary or naming question.
> - Read next: `debugging.md` (when findings are symptoms); `performance-and-accessibility.md` (for property and device rules).

How to review animation, whether it is a proposed option, existing code, or code just built. Default to flagging. Approval is earned, not assumed. A transition that merely works but feels sluggish, lands from the wrong origin, fires too often, or drops frames is a regression.

## Contents
- Modes
- What the script covers
- The ten standards
- Remedy hierarchy
- Findings table
- Verdict
- Things only a human can judge
- Fix loop

## Modes

| Mode | Input | Used for |
|---|---|---|
| Spec | A prototype spec before the user sees it | Weed out weak options early |
| Existing | Animation already in the target | Decide between improving and redesigning |
| Built | Files you just changed | Step 6 of every run |

In Existing and Built modes run `python scripts/audit_motion.py <paths>` first. In Spec mode run `scripts/validate_spec.py` and apply standards 1 to 8 by reading the spec.

## What the script covers

`audit_motion.py` flags the mechanical violations: unbounded transitions, layout-property animation, ease-in, scale from zero, ungated hover, missing reduced-motion handling, parent-variable drag, durations above the tier cap, legacy motion package imports, and unmeasured dash arrays. It lists `file:line`, the standard, and the remedy. It does not judge origin, personality, hierarchy or feel; those are yours. It never edits files.

## The ten standards

Each ends with what to flag on sight.

1. **Justified motion.** Every animation names a valid purpose from the gate. Flag: "looks cool" on anything seen often.
2. **Frequency-appropriate.** Match animation to how often it is seen. Keyboard focus and repeated actions respond immediately. Flag: animation that delays focus, task completion, or a keyboard-initiated or very frequent action.
3. **Responsive easing.** Entering and exiting use ease-out or a strong custom curve; built-in curves are too weak for deliberate motion. Flag: ease-in on UI.
4. **Within the tier's duration.** Routine UI stays under 300ms, scaled by distance. Flag: a duration over its tier cap with no stated reason.
5. **Origin and physical correctness.** Popovers, dropdowns and tooltips scale from their trigger; modals stay centered. Entrances start at 0.9 to 0.97 scale plus opacity. Flag: center origin on an anchored surface, scale from zero, pure fade with no starting transform on a surface that deserves one.
6. **Interruptible.** Anything triggered rapidly or by gesture retargets from its current state. Flag: restarting keyframes on toasts, toggles, or drag.
7. **Compositor-friendly properties.** Animate transform and opacity (bounded filter acceptable). Flag: width, height, margin, padding, top, left; `transition: all`; a parent CSS variable driving child transforms; shorthand animation props on motion that runs while the page is busy.
8. **Accessible.** Reduced motion has a defined gentler variant (keep opacity and color, drop movement); hover animation is gated to devices that hover; keyboard and touch complete the same task. Flag: spatial motion with no reduced-motion variant, ungated hover motion.
9. **Asymmetric enter and exit.** Deliberate actions (a press, a hold, a destructive confirm) animate slower; system responses snap; exits are quieter and faster than entrances. Flag: symmetric timing on a press-and-release or hold; a missing exit or reverse.
10. **Cohesive.** Motion matches the component's personality and the rest of the product; paired elements share easing and duration; a crossfade that shows two states gets a small blur bridge; groups that should stagger do. When unsure whether motion feels right, deleting it is often the best move. Flag: mismatched personality, mixed clocks in one group, everything-at-once where an offset belongs.

## Remedy hierarchy

Prefer earlier fixes over later ones:

1. Delete the animation (no purpose, too frequent, keyboard-triggered).
2. Reduce it: shorter, smaller transform, fewer properties.
3. Fix the easing.
4. Fix the origin and physicality.
5. Make it interruptible.
6. Move it to compositor-friendly properties.
7. Make timing asymmetric.
8. Polish: blur bridge, stagger, entry from a starting style, spring for alive elements.
9. Accessibility and cohesion: reduced-motion variant, hover gate, personality match.

## Findings table

Always a table, one row per issue:

| Before | After | Why |
|---|---|---|
| `transition: all 300ms` | `transition: transform 200ms var(--ease-out)` | Name the properties; `all` animates unintended ones off the compositor |
| `transform: scale(0)` | `transform: scale(0.95); opacity: 0` | Nothing appears from nothing |
| center origin on popover | origin at the trigger | Popovers grow from what opened them |

## Verdict

Group remaining commentary by impact tier, highest first, omitting empty tiers: feel-breaking regressions; missed simplifications; performance; interruptibility and timing; origin, physicality and cohesion; accessibility. Close with a decision citing `file:line`:

- **Block**: a feel-breaking regression, animation on a keyboard or very frequent action, scale from zero or ease-in on UI, a layout animation with an easy compositor fix, or a missing reverse for a transition.
- **Approve**: none of the above, durations and easing within bounds, interruption handled, reduced motion defined.

## Things only a human can judge

Say so plainly and give the check: feel and timing under real load, gesture behavior on a real device, subtle origin errors. Check in slow motion (2 to 10 times slower or a quarter-speed animation inspector), frame by frame for coordinated properties, on a real device for gestures, and again with fresh eyes later.

## Fix loop

1. Run the audit script and the standards review.
2. Fix findings from the top of the remedy hierarchy down.
3. Re-run the script on the same files.
4. Stop when the script is clean or each remaining finding has a one-line justification, then write the verdict.
