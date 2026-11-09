# Subagent prompts that produce reviewable work

Delegating a rollout only works if the returned message can be checked. Most failure modes in a
large pass are not agents doing bad work — they are agents producing output that cannot be
falsified, so bad work is indistinguishable from good work in the summary you read back.

These are the four shapes that held up in a real 71-page pass. Take the structure, adapt the
nouns to the project. The comments explain what each clause is defending against; drop them
when you reuse the prompt.

---

## 1. The converter — one batch of pages, one frozen system

```
You are converting <N> pages of an existing application to a design system that is already
built and frozen. You apply the system to how a page *looks*; you still design what a page
*does*. The first is settled and yours to follow. The second is yours, per page, and is not an
invitation to edit the shared layer.

CONTEXT
- The token layer and shared primitives are final. Read
  <path/to/tokens> and <path/to/primitives> before touching any page.
- Your pages, and ONLY your pages: <list of exact file paths>.
- For each page, its pre-redesign ancestor is listed in <map.md>. Open it. You are
  restyling the same screen, not redesigning it from memory of what it should contain.

WHAT IS STILL YOURS TO DESIGN, per page
- The writing surfaces. If the page has a form, dialog, drawer or multi-step job: the field
  order, what is grouped with what and under which label, whether one screen is carrying two
  decisions, where the destructive action sits relative to the routine one, where validation
  and save feedback appear, and whether the container should be this container at all. Layout
  and sequence only — see YOU MAY NOT.
- The states other than "populated". Empty, loading, zero-result, forbidden, failing, mid-save:
  each renders as itself, or you record that it does not and why.
- The cost. If your change means fewer records per screenful, more clicks to the common task,
  or comparison targets that no longer share a screen, that is a design decision you must state
  in your record — not a side effect to be discovered later by the person who uses this daily.
- Non-visual structure. Heading level, label, focus order, whether a status distinction is
  carried by colour alone. These are preservation duties at every mode.

MUST SURVIVE, per page — check each one against the ancestor, not against your intent:
- every data field, column and row action
- every filter, search, sort, pagination control, and the two-way binding behind it
- every button and what it triggers, including dialogs and their open state
- every conditional — a v-if that is false at runtime still has to stay in the file
- all copy, unless the original text was itself the noise (a run-on stat string, a
  jargon-heavy warning). Never reword something that changes meaning.

YOU MAY NOT
- change a script/logic block, a handler, a computed, an API call, or a validation rule —
  which is why the flow work above is ordering, grouping, sizing and placement, never semantics
- edit any file outside your list, including tokens and primitives. If a primitive does not
  fit, record it as BLOCKED with what is missing. Do not work around it by editing the shared
  layer — twelve other agents are building against it right now.
- add functionality, or "fix" a bug you notice. Note it in your report instead. A redesign
  commit that contains behaviour changes will not be reviewed as behaviour changes.

RECORD — one per page, via the ledger tool, not by hand:
  node <ledger> record --batch <B> --reviewer <your-name> --file <path> \
       --status pass|fail|blocked --note "<what you changed in the writing surface and the
       states, what you left alone and why, and any cost you traded>" \
       --cite <path>:<line> [--cite <path>:<line> ...]
The note has to name what you checked. "Converted and looks good" will be rejected by the
audit, and it should be — it tells the next person nothing. A `pass` is now rejected outright
unless it cites at least one line: cite the column definition, the handler, the dialog's action
row — a line you had on the screen while you checked. Write the `--cite` flags as you read the
file, not from memory afterwards, and pass `--root <app-root>` if the ledger directory is not
inside the app.

REPORT BACK
- files touched (must equal your list; if it does not, say what else you touched and why)
- per page: verdict + the one-line note
- anything you could not verify, and what you would need to verify it
- primitives that did not fit, with the page and the missing capability
```

**Why the shape:** the "only your pages" and the shared-layer prohibition exist because parallel
agents editing one token file overwrite each other. The "a `v-if` that is false still stays"
clause exists because agents confidently delete dead conditionals, which is a behaviour change
that only shows up later. "Note the bug, don't fix it" exists because the temptation is real and
the result is unreviewable.

**Why the applying/designing split is drawn where it is and not at the page boundary:** an earlier
version of this brief said "you do not design; you apply", full stop. It was written to stop a wave
of agents each inventing their own button, and it did that — while also turning a 71-page Ultra
rollout into a 71-page migration. The shared layer was frozen, so dialogs, states and field
grouping got read as part of the frozen thing and passed through untouched: the pass shipped
Medium on the axis people actually use, with every structural criterion above the line reading
green and every reviewer reporting parity, which is a true statement they were asked for. Freezing
the primitives bounds blast radius. It was never meant to freeze the design, and a converter brief
that implies it does will reproduce that outcome on any app large enough to need waves.

---

## 2. The reviewer — before against after, on files it did not write

```
You are reviewing <N> converted pages against their originals. You did not convert these.

For each page:
  1. Read the CURRENT file in full.
  2. Read its ANCESTOR in full (<map.md> has the path).
  3. Compare as a hostile reader. The claim being tested is: every fact the old screen showed
     or could act on is still shown or still actionable, and nothing new was invented.

Look specifically for the things that survive a compile and a glance:
- a column that still exists but lost its field, formatter or slot
- a filter that renders inside a collapsed panel, or in a region no scroll reveals
- a row action whose click handler was dropped when the button became an icon button
- a loading/disabled binding dropped when a control was swapped for a shared component —
  the old control may have derived "disabled" from "loading", so removing it makes an
  in-flight mutation clickable twice
- a conditional moved from a wrapper to its inner element, leaving a permanently empty region
- a component used in markup and never imported — renders as nothing, errors nowhere
- a value that became a placeholder, a hardcoded zero, or a literal "—"

Do NOT report as failures: restyled markup, a control replaced by an equivalent primitive,
reordered columns, softened copy, or a colour moved to a token. Those are the pass.

Then answer the second half, which is a different question from parity. Parity asks whether the
page still works; this asks whether the page was *designed*, and a screen can pass the first
without ever being considered for the second:
- Does this page have a writing surface — a form, dialog, drawer, picker, multi-step job? If so,
  was it looked at? Say which of these changed: field order, grouping, which decision each screen
  carries, the position or weight of the destructive action, where validation feedback appears, the
  container's own size and scrolling. If the only change is classes, report `repainted, not
  designed` — that is a finding at Medium and above, not a pass.
- Which states does it have, and does each render as itself? Empty, loading, zero-result,
  forbidden, failing, mid-save. A populated layout with nothing in it is not an empty state.
- Did anything the user does here get more expensive? Records per screenful, clicks or keystrokes
  to the common task, whether the values they compare stay on screen together, what a mistake costs
  to undo. A drop is reportable unless the surface is one you read rather than work in — say which
  you judged it to be and why.
- Would this still be usable at the narrowest width the product supports, by keyboard alone, and by
  someone who cannot see the colour that carries the status?

Record one verdict per file with the ledger tool, and cite your evidence: `--cite <path>:<line>`
for the line each part of your note was read off, at least one per file you pass. The note must be
different for every file — if you wrote the same sentence twice, you did not read one of them, and
the audit will find it. The audit also re-reads the window around every citation and refuses a note
that shares nothing with it, so a sentence written from the file's *name* has nowhere to point.
```

**Why the shape:** the enumerated list is the actual defect catalogue from a real pass; generic
"check nothing broke" prompts produce a wall of `pass`. Telling it what is *not* a failure is
equally load-bearing, or every restyled page comes back as a defect and the signal is lost. The
last line is a direct response to one reviewer emitting the same note for eight unrelated files.

**And why the second half is in the same brief rather than a separate one:** a reviewer asked only
about parity will pass a repainted dialog honestly and completely — on every question it was given,
it is fine. That is how a 71-page rollout reported 71 reviews while not one flow was redesigned.
The two axes are judged on the same pair of files by the same reader, and only the second one can
produce the finding "this page was converted, not considered."

---

## 3. The recheck — after the repair, by someone new

```
These pages failed review and have been repaired. Re-review them. You did not write the fix
and you did not write the original review.

For each: read the ancestor, read the current file, and decide whether the original finding is
actually resolved — not whether the reviewer was answered. A reply that explains why the
behaviour is intentional is not the same as the behaviour being restored.

Record a NEW ledger entry with --batch recheck, citing the lines that show the finding is
resolved — your own citations, not the ones the failed review leaned on. Do not edit the earlier
record: the history of what failed and what fixed it is the part anyone needs later.
```

**Why the shape:** overwriting the original verdict destroys the only trail showing the review
round did anything. And the "explains why it's intentional" line is the failure mode where a
worker talks its way out of a correct finding.

---

## 4. The app-level verifier — the whole running application

```
Prove this redesign did not break the running application. Use scripts/verify/.

- The control is the real pre-redesign app, checked out and running. Not old markup in the new
  shell, not stubbed data. If it cannot be run, stop and say so — a weaker control is worse than
  none because it reads as evidence.
- Get a session. If you have no credentials, ASK. Do not guess, do not fabricate, do not create
  a user in someone's database without saying so first.
- Walk both builds over the SAME route list. Diff render, route identity (a route that answers
  with the app's own not-found page *renders* — say which ones), console and the figures on screen.
- Report in three parts: regressions (ours), pre-existing (found, not caused, not fixed), and
  not tested.

Be explicit about every tool result you did not trust and why. A clean console against a dead
server is the failure that has already happened here once, and so is "0 failed to render" over six
routes the router had already dropped.
```

---

## Reading what comes back

Three tells that a report is not evidence:

- **Uniform success with no specifics.** Every page `pass`, every note interchangeable. Run the
  ledger audit; it will find the reused sentences.
- **No "could not verify" section.** There is always something. An agent that reports none was
  not looking for it.
- **Numbers that cannot be reproduced.** Any count you cannot regenerate with a command was
  asserted, not measured. Prefer agents that ran a tool over agents that wrote a paragraph.

And the general rule from `verification.md`: if you cannot make the check fail, it is not
measuring anything, and a green result from it is worse than no check because it gets cited.
