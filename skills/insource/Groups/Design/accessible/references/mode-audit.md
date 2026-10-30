# Grading the mode you actually delivered

The person asked for Ultra. You produced something. Those are not the same statement, and the
gap between them is not something you get to assess by remembering what you intended.

**The rule this exists to enforce: nobody should have to ask for Ultra twice.** If a pass
labelled Ultra turns out to be a re-skin, the failure happened before delivery, and the only
thing that would have caught it is a grade computed from the diff rather than from the author's
own account.

---

## Why self-assessment fails here specifically

Every other judgement in this skill is about a single screen in front of you — you can look at
it. Mode is a claim about *the delta between two states*, and after 70 files the author's memory
of the starting state is exactly the thing that has been eroded. Worse, the work feels like Ultra
while you are doing it: rebuilding a palette across 70 pages is enormous effort, and effort is
not the axis the modes measure.

The failure looks like this, and it is easy to miss because every individual item is defensible:
every screen got a new palette, real token layer, better type, redistributed stats — and not one
route was renamed, no page was split, the navigation grouping is byte-identical to the input.
That is a very good Medium pass. Delivered as Ultra, it reads as a lie the moment the person opens
the app and finds the same twelve things under "Settings".

So the grade comes from measurement, and the measurement comes from a diff against the original —
never against your own earlier output.

---

## What each mode must demonstrably have changed

| | must be observable | must NOT be true |
|---|---|---|
| **Lite** | type scale and spacing differ from the input; raw colour reduced or bounded by tokens | nothing structural moved — that is the mode, not a shortfall |
| **Medium** | all of Lite, plus new shared components and new *projections* of existing data (callouts, stat strips, filters given their own region) | the data was only recoloured in place |
| **Ultra** | all of Medium, plus a rebuilt token ramp, a named elevation scale that is consumed, structurally different output (pages added, split, moved), **a re-derived navigation taxonomy**, **and the interaction layer carried through the pass** | the route names and grouping are the input's, or every form and dialog in the app is the input's with new classes |

The last one is the criterion most often skipped, because it is the only one that touches other
people's territory: routes mean permissions, deep links, bookmarks, docs. Which is exactly why it
needs a gate rather than judgement in the moment.

**"The nav file changed" is not the test.** An early version of the grader accepted that, and
passed a pass that restyled the sidebar and renamed nothing. The test is whether the *set of
declared paths* changed — renames, retirements, genuinely new routes. Same count and same names
means the taxonomy was inherited, however good the rest of it is.

---

## The interaction criterion, and why a boolean would not do

Every criterion above measures a surface someone *reads*. The last one measures the surfaces
someone *uses*: forms, dialogs, pickers, multi-step jobs. It exists because a pass cleared all of
the above — palette rebuilt, 16 routes re-derived, pages split, elevation system introduced — while
leaving the way a user creates a thing byte-for-byte identical, and the person had to say "that
looks like Medium" before anyone noticed.

It compares a **signature of the controls** (which controls exist, in what order, with what
identifying attributes) rather than the file's text, so repainting a dialog does not count as
redesigning it. Files are paired across the two trees *including renames*, because counting a page
that moved to a new path as a "new flow" is exactly how a re-skin would clear the bar.

**First attempt, and why it was wrong.** The criterion started as `redesigned > 0`. Run against that
same pass it reported 12 of 77 writing surfaces changed — and ticked green. A boolean on a population
of 77 is not a check; it is a formality. So the bar is not "some flow moved", it is **"you looked"**:
the pass must account for the surfaces it left alone, via

```bash
--flow-note "examined the create/edit dialogs on funds, prices and users; single-step forms whose
fields already match the decision order, so they were left apart from the palette"
```

The note prints into the report rather than being accepted silently. Triage and negligence look
identical in a diff and different in a sentence, which is the whole reason the sentence is required —
it is not a waiver, and there is no percentage threshold that would have been any better, because a
ratio gate would punish the correct decision to leave a sound flow alone.

Two useful properties of the numbers themselves: they are printed as a list of the untouched
surfaces, so a claim of flow work can be checked against names rather than believed; and the
criterion reports **NOT MEASURED** when the stack profile has no `interaction` block, rather than
passing on a count of zero surfaces — a rule that cannot match anything reporting a clean result is
the same bug in a new costume.

---

## Running it

```bash
node scripts/mode-audit.mjs --requested ultra \
     --before ../app-origin/src --after .          # two trees
node scripts/mode-audit.mjs --requested ultra --against <revision-before-the-pass>
```

Run it from the app's own directory when you can. Whole-repo mode works, but it reads every
project in the tree; scoped to the app, the numbers mean the app.

Two things the tool will tell you rather than quietly get wrong. If the two trees are
near-identical, it stops and says the baseline is too narrow — pointing at the last commit
instead of the state before the pass measures a diff of almost nothing and grades a complete
Ultra pass as Lite. And a checked-in copy of the original tree (`*-origin`, `*-before`, a
worktree) is skipped automatically, because otherwise every path the pass retired is still
declared in the copy and a 16-route re-architecture reads as "0 renamed".

It prints a table of criteria, each with the numbers it measured, and a verdict: the mode the
work actually reached. Exit code is non-zero when the delivered mode is below what was asked.

Two things it deliberately will not do:

- **It will not certify the taxonomy criterion on a restyled nav.** If nothing was renamed, it
  fails, and the only way through is either doing the move or passing `--ia-note` with a real
  reason the grouping was left alone — a note under twenty characters does not clear it, and the
  exception is printed into the report so it is visible rather than buried.
- **It will not tell you the result is good, or even that the work was worth doing.** Taste is not
  measurable, and neither is value: a pass can clear every bar here by moving paint and renaming
  things well. A green grade still owes you `accessible-audit.mjs`, a screenshot you actually looked
  at, the mode checklist answered item by item against what you saw — and one sentence no script can
  produce: **what a user can get done better than before.** If that sentence comes out as a list of
  colours, radii and renamed headings, the honest report says that, and calls the pass the mode it
  reached.

---

## What to do when the grade comes back low

Three honest options, in this order of preference:

1. **Do the missing move.** Usually this is the structural one, and it is the one the person
   asked for when they said Ultra.
2. **Deliver it under the mode it reached**, and say plainly which criterion is unmet and why.
   "This is a Medium outcome on the structural axis because the app's routes are wired into a
   permissions system I could not safely re-path in the time" is a complete answer.
3. **Ask**, if the missing move is large and irreversible — a route rename across a permission
   chain is a decision, not a detail.

What is not an option: shipping a Medium result labelled Ultra. The person will find it, and
"make it Ultra" arriving a second time, from them, is the failure this whole file is about.

---

## Where this belongs in the pass

Not at the end as a formality. The grade is cheap to compute and expensive to discover late:

- **Before starting**, run it with `--requested <mode>` against a dry-run diff of one converted
  page. If a pilot page already reads as Lite, the plan is wrong, not the page.
- **Before delivering**, run it over the whole change and put the printed table into the report
  verbatim — including the criteria that failed.
- **After any later edit** to the shared layer, run it again. A primitive change can quietly
  collapse a structural criterion back down.

---

### Grade the mode you delivered — before delivering, not after being told

**Nobody should have to ask for Ultra twice.** A pass can feel enormous while it is happening — 70 pages re-tokened, a real palette, better type — and still be a Medium outcome, because the modes are separated by *what changed structurally*, not by how much work it was. The author is the least reliable judge of that gap: after dozens of files, the memory of the starting state is what has eroded, and effort reads convincingly. So the grade comes out of a diff against the original, never out of recollection:

```
node scripts/mode-audit.mjs --requested <mode> --profile <stack-profile> --before <original tree> --after <current tree>
```

`--profile` is not optional in practice. The scripts hold no framework assumptions of their own — the colour patterns, token syntax, route-declaration shape, writing-surface markers and file extensions all come from a stack profile in `assets/stack-profiles/` (`base`, `vue-tailwind`, `react-tailwind`, `plain-css`). None of those is your project's; derive one with the six greps in `references/stack-profiles.md` and keep it in the repo. Without a matching profile the measures it cannot take are reported **NOT MEASURED** and the criteria read as failed — which is the honest outcome, because a hardcoded rule that matches nothing on an unfamiliar stack reports a clean zero instead, and a zero looks exactly like a pass.

It reports, per criterion, the numbers it measured, and a verdict: the mode the work actually reached. Exit code is non-zero when that is below what was asked for. Run it **before delivery** and put the printed table in the report verbatim, including whatever failed. Run it again after any later change to the shared layer, since a primitive edit can quietly collapse a structural criterion back down.

What it holds the line on, and why each one is a separate criterion: **Lite** must move type and spacing and bound raw colour; **Medium** must additionally redistribute — new shared components and genuinely new *projections* of existing data, not the same facts recoloured in place; **Ultra** must additionally rebuild the token ramp, introduce a named elevation scale that is actually consumed, produce structurally different output (pages added, split, moved), **and re-derive the navigation taxonomy**. That last one is skipped most often because it is the only one that reaches into other people's territory — routes mean permissions, bookmarks and docs — and it is exactly the one a person notices, by finding the same twelve things still filed under "Settings".

**"The nav file was edited" does not count.** The test is whether the *set of declared paths* changed: renames, retirements, genuinely new routes. Same count, same names means the taxonomy was inherited, however good the rest of the pass is. The legitimate exception is a written one — `--ia-note` with a real reason the grouping was left alone, which prints into the report rather than being buried.

When the grade comes back low: do the missing move; or deliver it under the mode it reached and name the unmet criterion out loud; or, if the missing move is large and hard to reverse, ask. Shipping a Medium result labelled Ultra is the one outcome that is not on that list. Full rubric and reasoning: `references/mode-audit.md`.


