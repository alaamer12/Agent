# Example: a component run

Command: `animate component Dialog.tsx`

**0 Understand.** Clear request, no vague wording. Scope is the whole dialog.

**1 Survey.** The dialog already animates: center-origin scale from 0, 450ms, ease-in, no exit. The Reviewer runs in Existing mode first and reports: scale from zero, ease-in, over the tier cap, missing exit. Classification: `scope=component · interaction=non-interactive · sync=instant (surface and overlay) · direction=enter/exit`.

**2 Gate.** A modal is occasional. Purpose: spatial consistency and preventing a jarring change. Outcome: animate, tier routine.

**3 Style.** Recommended traditional with correct craft: occasional functional surface. User agrees.

**5 Build** (traditional style: spec stated in two lines, no prototype).
- Overlay: opacity, 200ms enter curve. Dialog: opacity plus scale from 0.96, 240ms, same curve; exit 160ms with a small downward 4px offset. Origin: center (modal, not anchored).
- Children static: the container moves, so the contents do not stagger.
- Interruption: closing mid-open reverses from the current state using transitions.
- Focus moves into the dialog immediately; it does not wait for the animation.

**6 Review.** Audit script clean after replacing `scale(0)` and `ease-in`. The standards review confirms paired easing, exit present, reduced motion keeps opacity and drops scale. Verdict: Approve.

**7 Report** with exact values and one follow-up: "the same tokens suit the Drawer and Popover components".
