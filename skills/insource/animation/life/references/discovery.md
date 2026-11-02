# Discovery

> Owns the opportunity posture, the seams catalog, script usage, the report format and grouping; routing lives in `../SKILL.md`.

Find where a target should animate, and reject the rest. Read-only: it proposes with exact values and implements nothing until the user picks.

## Posture

The defining trait is restraint. An opportunity finder that suggests motion everywhere produces sluggish, over-animated interfaces. Expect to reject most candidates. A short list of high-conviction opportunities beats a long wishlist, and "this interface needs little motion" is a valid result.

## When it runs

- The target is a directory, a page with many parts, a route tree, or the whole project.
- The user says they do not know what to animate, or the interface "feels dead" or flat.
- It also applies to a single file whenever the user asks "what could be animated here?".

It runs automatically for broad targets. It never edits files.

## Procedure

1. **Recon.** Identify the stack, animation library, existing tokens (suggestions extend them, they do not start a parallel set), and the product personality. A dense dashboard earns fewer and subtler suggestions than a playful consumer app. Build a rough frequency map of the surfaces.
2. **Sweep** every seam below. A seam is done when it has yielded candidates with file and line evidence or has been explicitly cleared.
3. **Gate** every candidate through all four gate questions in order. Record each answer.
4. **Report** survivors and rejections in the format below. Cap survivors at 5 to 7 for an app, fewer for a single view.
5. **Wait** for the user's pick.

## Seams to sweep

| Seam | What it looks like | Typical signal |
|---|---|---|
| Feedback gap | Pressable element with no press or hover response | Click handlers on elements with no active state or transition |
| Teleporting state | Content that appears, vanishes or swaps with no bridge | Conditional renders, display toggles, accordions with no transition |
| Missing spatial story | Surface unconnected to what opened it | Popovers and menus with no origin; exit path differs from entry path |
| Group entrance | Occasionally seen list or grid pops in whole | List rendering on first-load surfaces |
| Gesture seam | Draggable or swipeable thing snaps with no physics | Drag handlers with no spring, velocity, or boundary friction |
| Flat delight moment | Rare high-emotion state rendered flat | First-run, empty, success, completion components |
| Unlinked relatives | Related elements that react independently | Hover or selection on one item with related items visibly static (linked) |
| Unordered group | Several related animations that start arbitrarily | Parts of one flow with no designed order (domino) |
| Missing reverse | A forward move with no designed way back | Steps, tabs, routes, open/close pairs where only one direction animates |

## Using the script

```bash
python scripts/find_candidates.py <dir> [--max 15] [--format json|text]
```

It prints, per seam, candidate locations with a snippet, plus an inventory of animation that already exists. Candidates are leads, not findings: every one must still pass the gate. If the script cannot run, use the search patterns above with the agent's own file search and sample files by name (success, empty, onboarding, toast, modal, dialog, drawer, tabs, wizard, stepper, route).

## Report format

### Part 1: opportunities

| # | Location | Today | Purpose | Frequency | Proposed command | Suggested direction |
|---|---|---|---|---|---|---|
| 1 | `path:line` | what happens now | named purpose | tier from gate | micro, component or transition | one line with exact values or the creative idea |

Every suggested direction carries exact values (properties, durations, easing) drawn from the tokens (see timing-and-tokens.md), never approximations. Hover suggestions mention the pointer gate; every suggestion mentions its reduced-motion behavior.

### Part 2: rejected candidates (required)

List two to five places considered and deliberately not suggested, each with the gate question that killed it (verdict rules: see gate.md). This section is what separates discovery from a wishlist.

### Part 3: verdict

One short paragraph: how much animation this interface needs, whether it is already close, and which single suggestion has the highest leverage.

## Broad targets

For a whole project, group by area (navigation, forms, overlays, lists, onboarding) and present one area at a time. Do not dump a project-wide list. Order areas by leverage. After each pick, run the normal phases (gate to report) for that pick with the proposed command.

## Handoff

When the user picks, resume per run-procedure.md §Resuming after a pick; record unpicked survivors as follow-ups in the final report.
