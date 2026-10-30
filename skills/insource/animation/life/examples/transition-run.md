# Example: a transition run

Command: `life transition Wizard.tsx`

**0 Understand.** Scope is the change between wizard steps.

**1 Survey and classify.** Step graph: 1 to 2 to 3 to 4, back from each, and a progress marker allowing a jump to any completed step. Persisting elements: header, progress markers. Replaced: step content. The forward and reverse table is filled before any design:

| Move | Forward | Reverse |
|---|---|---|
| 1 to 2, 2 to 3, 3 to 4 | Content out left, next in from right, domino header then fields | Out right, previous in from left, shorter |
| Jump 1 to 4 | One transition in the forward direction | Jump 4 to 2 plays one backward transition |

Classification: `scope=transition · interaction=non-interactive (button) / interactive (swipe) · sync=domino · direction=forward+reverse`.

**2 Gate.** Taken a few times per session, occasional: animate, tier rare.

**3 Style.** User picks creative.

**4 Options.** Two options in `transition-spec.json`: A hand-off glide (domino) and B progress thread (linked marker and content). The validator rejects any transition option without a designed reverse. The user picks A with B's marker thread as a remix.

**5 Build.** Direction derived from the step index difference, with layout-aware sign flipping for right-to-left. Transitions retarget on rapid next and back; skipping steps plays a single transition; navigation never waits on the animation.

**6 Review.** Audit script clean; standards review checks the reverse exists and is shorter; flagged for a human: rapid back-and-forth on a real device.

**7 Report.** Includes the forward and reverse table with final values.
