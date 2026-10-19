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
built and frozen. You do not design; you apply.

CONTEXT
- The token layer and shared primitives are final. Read
  <path/to/tokens> and <path/to/primitives> before touching any page.
- Your pages, and ONLY your pages: <list of exact file paths>.
- For each page, its pre-redesign ancestor is listed in <map.md>. Open it. You are
  restyling the same screen, not redesigning it from memory of what it should contain.

MUST SURVIVE, per page — check each one against the ancestor, not against your intent:
- every data field, column and row action
- every filter, search, sort, pagination control, and the two-way binding behind it
- every button and what it triggers, including dialogs and their open state
- every conditional — a v-if that is false at runtime still has to stay in the file
- all copy, unless the original text was itself the noise (a run-on stat string, a
  jargon-heavy warning). Never reword something that changes meaning.

YOU MAY NOT
- change a script/logic block, a handler, a computed, an API call, or a validation rule
- edit any file outside your list, including tokens and primitives. If a primitive does not
  fit, record it as BLOCKED with what is missing. Do not work around it by editing the shared
  layer — twelve other agents are building against it right now.
- add functionality, or "fix" a bug you notice. Note it in your report instead. A redesign
  commit that contains behaviour changes will not be reviewed as behaviour changes.

RECORD — one per page, via the ledger tool, not by hand:
  node <ledger> record --batch <B> --reviewer <your-name> --file <path> \
       --status pass|fail|blocked --note "<what you verified, specifically>"
The note has to name what you checked. "Converted and looks good" will be rejected by the
audit, and it should be — it tells the next person nothing.

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

Record one verdict per file with the ledger tool. The note must be different for every file —
if you wrote the same sentence twice, you did not read one of them, and the audit will find it.
```

**Why the shape:** the enumerated list is the actual defect catalogue from a real pass; generic
"check nothing broke" prompts produce a wall of `pass`. Telling it what is *not* a failure is
equally load-bearing, or every restyled page comes back as a defect and the signal is lost. The
last line is a direct response to one reviewer emitting the same note for eight unrelated files.

---

## 3. The recheck — after the repair, by someone new

```
These pages failed review and have been repaired. Re-review them. You did not write the fix
and you did not write the original review.

For each: read the ancestor, read the current file, and decide whether the original finding is
actually resolved — not whether the reviewer was answered. A reply that explains why the
behaviour is intentional is not the same as the behaviour being restored.

Record a NEW ledger entry with --batch recheck. Do not edit the earlier record: the history of
what failed and what fixed it is the part anyone needs later.
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
- Walk both builds over the SAME route list. Diff render, console and the figures on screen.
- Report in three parts: regressions (ours), pre-existing (found, not caused, not fixed), and
  not tested.

Be explicit about every tool result you did not trust and why. A clean console against a dead
server is the failure that has already happened here once.
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
