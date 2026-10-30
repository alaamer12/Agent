# What the interface is for

The skill's headline — calm, scannable, professional — describes a *means*. Calm is not the job.
A screen that is serene and slow is worse than a busy one that is fast, and nothing in the moves,
the ceilings, or the mode grade would notice, because they all measure how the surface looks rather
than what it lets someone do. This is the half of the diagnosis that a page-at-a-time method
structurally cannot see: every instrument here takes one rendered screen as input. A screen is a
still frame; a job is a sequence, spread over time, done by one particular person, on one
particular device, in one particular state.

## Three obligations, not one

Every pass owes all three, and an honest report says where each landed:

1. **Understood quickly.** The original goal: hierarchy, encoding, noise, the numbered failures.
2. **Done with less cost and fewer errors.** Time, clicks, keystrokes, scrolling, eye travel, what
   must be held in memory between steps, what a mistake costs to undo.
3. **By the people who actually use it, the way they actually use it.** Different bodies, input
   methods, widths, competence levels and moments — including the first one and the bad ones.

Obligation 1 is bounded by the ceilings in `comfort-ceilings.md`. Obligation 2 is bounded by the
floors in that same file. Obligation 3 is largely a preservation duty: the pass may not *remove*
what someone relies on, and must not silently assume one way of using the thing.

None of the three is derived from a product category. They are derived from evidence, and the
evidence is in front of you.

## Derive the job from evidence — do not classify the product

The tempting move is a taxonomy: "this is an ERP, therefore dense; this is a SaaS, therefore
friendly." Resist it for two reasons. Product categories are weak predictors of what a specific
screen is for — an ERP has analytical screens where thinking slowly is the whole point, and a
marketing dashboard has a table someone keys 400 rows into. And an enumeration invites filling:
the boxes get completed, coverage gets reported, nothing gets looked at. That is how a rollout of
71 pages ends up with 65 untouched dialogs and a green grade.

So there are no categories here. There are questions, answered **from the input's own evidence**,
in prose, differently for every surface — and two screens in the same product are allowed, and
expected, to get different answers.

**What is the unit of work here?** A record to inspect, a row to enter, a decision to make, a
document to produce, a thing to find. Read it off the surface: what the fields are, what the
buttons do, what the columns carry, what the route names claim, what the permission entries imply.
The app already states what jobs it believes it has; you are not inventing a persona.

**What does that work cost right now?** Countable from structure, without a stopwatch: controls
between opening the screen and finishing the common task; rows visible per screenful at the size
you are proposing; whether the values someone compares are ever visible at the same time; how much
must be remembered between step and step; what a mistake costs to undo.

**Who does it, and how?** Keyboard-first or pointer-first; hours at a stretch or forty seconds
between meetings; expert or first-timer. Then the harder version of the same question: what is this
screen like with a screen reader, with a keyboard only, at 200% zoom, on a phone held at arm's
length, with a thumb instead of a mouse, without colour discrimination, with a shaky hand, in the
one bad moment when the thing has already gone wrong?

**What states does the work pass through?** First time and hundredth. Empty, loading, partial,
zero-result, forbidden, failing, mid-save. Which does the input render distinctly, and which renders
as *the same thing* — usually the populated layout with nothing in it, which reads as a designed
emptiness rather than an absent state.

**What would a person notice if this went wrong?** Not "would the audit score drop" — the sentence
a user says on the day they use it. For an entry grid: "I have to scroll more to see the same
rows." For a landing page: "I don't know what this is." For an editor: "what I typed no longer
looks like what gets published." **If you cannot name one, you have not diagnosed this surface
yet**, and any judgement about its density, scale, or split is a guess wearing a rationale.

### Where the evidence comes from

| question | evidence in the input |
|---|---|
| unit of work | field sets and their groupings; action labels; column lists; route and permission names; what the empty states assume |
| cost of the work | control counts; row heights against typical viewport; how many clicks to the common task; comparison targets that never co-occur |
| who and how | keyboard handlers, focus styles and tab order that already exist; whether touch targets are sized; whether labels exist for icon-only controls; whether anything is hover-only |
| states | which branches the code renders for (loading/error/empty/forbidden), and how many of them share one rendering |
| what a wrong pass looks like | the above, plus asking the person — they know what they do all day and you do not |

Asking is not a failure of this step; it is part of it. The person knows which job their users do,
which screen is used for four hours a day and which once a quarter, and what they'd miss. Two
sentences from them beats a page of your inference — but ask *after* you have a derived answer to
put in front of them, not instead of one.

## How this changes the mode calls

- **The type/spacing scale stops being a taste dial.** It trades against obligation 2. The scale
  move says "past enormous, density drops" — that is a floor speaking. On a surface where volume is
  the job, the comfortable end of the range is the wrong end, and the calm treatment belongs in
  encoding and hierarchy instead. Say which obligation set the number.
- **The page-split call is not always right.** Splitting aggregate from detail helps someone who
  *reads* both and hurts someone who *compares* them, because it puts a navigation between the two
  things being compared. Default to splitting at Ultra; check this question before splitting a
  screen whose entire purpose is side-by-side.
- **"Fold non-scanned values into plain text" needs the population, not the row.** A value that is
  rare per row may be the one thing being checked constantly across rows.
- **Preservation gets teeth.** Keyboard reach, focus order, heading structure, control names, motion
  preferences and time-critical affordances are not styling. Removing one is a defect even when the
  result photographs better — and no screenshot will show it, because the render you looked at is
  one of the ways the screen can be used, not the only one.
- **The closing claim gets harder.** "The grade says Ultra" is satisfiable by paint plus renames.
  The pass also owes what a user can get done better, faster, or with fewer errors — and the names
  of the flows it examined and deliberately left alone. `mode-audit.mjs` prints that ratio so the
  sentence can be checked against a diff instead of against the author's recollection.

## The failure this prevents

The characteristic bad outcome is a pass that is entirely real work and entirely beside the point:
every token rebuilt, every table redistributed, every route re-derived, the palette a genuine ramp —
and the way you create a thing, correct an error, or discover the system is broken is byte-for-byte
the input's, possibly worse, because the container it lived in moved and nothing re-fitted it.
Effort was spent, the map filled, the grade returned Ultra. It has the same shape as every other
checklist failure in this skill: the instrument measured the thing that was easy to measure.
