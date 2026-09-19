# how-to-do workflow — full decision logic

This reference covers the reasoning an agent applies on every task in a repo
that has a `.htd/` folder. Read this in full before writing or editing any
`.htd/*.md` file — the value of this system depends on the structural
decisions (which file, which task-ID, patch vs. new entry) being made
consistently, not just on individual files looking correct in isolation.

## Why this exists

A human asking for "add a schema" or "refactor the auth flow" is describing
an *outcome*, not a checklist. The actual correct sequence of edits for that
outcome in a specific codebase is knowledge that either lives in a human's
memory (unreliable, and not transferable across sessions or models) or gets
re-derived from scratch every time (expensive, and prone to silently
dropping a step — the code still looks right, it's just incomplete).

`.htd/` is where that sequence gets written down once, generalized, and
corrected over time — so completing a task correctly stops depending on one
session's interpretation of a vague request.

## The three-way decision

On every task that plausibly falls into an existing or new domain, decide
among exactly these three outcomes. Do this explicitly — don't skip straight
to doing the task.

1. **No matching domain file exists** → after completing the task, create a
   new domain file (see "Creating a new domain file" below).
2. **A matching domain file exists, but no task-ID inside it matches this
   request** → after completing the task, add a new task-ID section to that
   file (see "Adding a task-ID").
3. **A matching task-ID exists, and following it produced an incomplete or
   incorrect result** (something had to be done that isn't in the
   documented steps) → write a task-patch under that task-ID (see "Writing
   a patch"). Do not rewrite the base steps directly.

If a matching task-ID exists and it was sufficient as written, no `.htd`
edit is needed — the whole point is that a well-documented task-ID should
eventually need no further writing, just following.

## Matching: finding the right domain file and task-ID

Before starting the task itself:

1. List `.htd/*.md`. Domain filenames should be descriptive of the class of
   change (e.g. `changing-table-schemas.md`, `auth-flow-changes.md`) —
   match the request against these by meaning, not just keyword overlap.
2. If a domain file plausibly matches, read its "Tasks in this file" index
   first (not the whole file) to find a task-ID whose title or "Matches
   queries like" examples fit the current request.
3. Only read the full task-ID section once you've identified a likely
   match from the index.

This index-first approach is why every domain file must keep its index
current — it's what keeps matching cheap as a domain file accumulates many
task-IDs over time.

If a request could plausibly fit two existing task-IDs, prefer the one
whose "Matches queries like" phrasing more specifically overlaps with the
request's actual wording and intent, and note the ambiguity in a comment
if you create a patch or new task-ID as a result — future matching should
get easier from this, not harder.

## Creating a new domain file

Use `assets/domain-file-scaffold.md` as the starting structure. Name the
file for the *class* of task it covers, not the specific instance that
prompted it — `changing-table-schemas.md`, not `add-catalog-table.md`. The
goal is that a future, differently-worded request in the same domain
should plausibly land in this same file.

Immediately add one task-ID to it (see below) — a domain file with no
task-IDs isn't useful yet.

## Adding a task-ID

Use `assets/task-id-template.md`. Two things matter more than following
the template shape exactly:

- **Generalize past the originating instance.** The task was completed for
  one specific request (e.g. "add a `catalog` table"), but the task-ID
  documents the *procedure*, not that instance. Write file edits and step
  descriptions in terms general enough to apply to the next differently-named
  table, not "add `catalog` table" specifics. The Origin query fields exist
  precisely so the *one instance that caused this to be written* stays
  distinguishable from the *general pattern* it's meant to match going
  forward ("Matches queries like").
- **Files affected is the only mandatory field per step.** Beyond that,
  write whatever structure actually transfers understanding to a future
  agent — nested lists, a caveat paragraph, a warning about a
  non-obvious side effect. Optimize for a future agent not repeating a
  mistake, not for uniformity across steps.
- **`Why` explains why the step must exist, not why a particular file was
  edited the way it was.** The test: if this step were skipped entirely,
  what breaks or silently degrades? That's what `Why` answers — not "this
  file is the source of truth the generator reads from" (that's mechanics
  belonging in the Files list itself, if anywhere), but "skipping this
  step means the table is defined but invisible everywhere else in the
  pipeline." A step with no real failure mode if skipped can leave `Why`
  as `—`.

Mark a step `(optional)` when it only applies given some condition in the
query (e.g. seeding dummy data, adding an index) rather than always. An
optional step **must** have a `Condition:` line stating the exact signal
that triggers inclusion — "optional" without a stated condition just
reintroduces the ambiguity this system exists to remove. When an agent
skips an optional step, it should say so explicitly in its summary to the
user, so a deliberate skip reads differently from a dropped step.

Update the domain file's "Tasks in this file" index in the same edit.

## Writing a patch

Use `assets/task-patch-template.md`, appended under the relevant task-ID's
`#### Patches` section (newest first).

A patch is written when, while executing a task matched to an existing
task-ID, the documented steps turned out to be insufficient or slightly
wrong for the current request — not when the task-ID was simply followed
successfully.

Patches are **additive, not corrective-in-place**. Don't silently edit the
numbered base steps when a gap is found — append a patch instead. This
matters for two reasons: it preserves an honest record of when a step was
actually discovered to be necessary (yesterday's completion using 4 steps
wasn't wrong at the time if a 5th step's necessity was only surfaced
today), and it lets a human or a later consolidation pass decide whether a
patch reflects the general case or only a narrower variant, rather than an
agent unilaterally deciding a base procedure changes.

Always capture both the raw query and the interpolated query on a patch,
not just one. The gap between them is often the actual signal — whether a
step was missing because the request had a genuinely new requirement, or
because the request was ambiguous and got misread. Losing that distinction
makes it harder to tell, later, whether the base task-ID needs to change
or whether a future agent just needs a matching hint added.

Use the `Scope note` to flag whether a patch is likely general (should
eventually fold into the base steps) or narrow (specific to a variant of
the task, e.g. soft-delete columns specifically, not all new columns).
Don't guess — if genuinely unsure, say that it's unconfirmed rather than
picking a side.

## Promotion: when do patches become base steps?

Patches accumulate as an append-only, dated log under a task-ID. They are
**not** auto-merged into the numbered steps by an agent, even when several
patches say the same thing. Repeated patches pointing at the same gap are a
strong signal the base steps should be updated — but folding a patch into
the base steps (and advancing a task-ID's `status` from `draft` to
`stable`) is a deliberate consolidation action, not something to do
silently while executing an unrelated task.

If you notice, while working on a task-ID, that its Patches section has
multiple entries converging on the same missing step, say so to the user
and propose consolidating — don't just do it inline. This keeps the base
steps trustworthy: anything numbered in "Steps" has been through that
deliberate check, not folded in mid-task by whichever agent happened to
notice the pattern first.

## After finishing any task matched to an existing task-ID

Before considering the task done, compare what was actually done against
the documented steps — including any optional steps and their conditions.
If execution diverged from the documented procedure in any way, even if
nothing broke and the result looks correct, write a patch. This is what
catches silent drift (5 steps today, 4 tomorrow) proactively, rather than
only reacting when something visibly fails.
