# Rolling a pass over a whole application

Everything else in this skill describes one pass over one input. This is the other job: the
person hands you an application — 40, 70, 120 screens — and asks for the pass across all of it.

The single-page moves still apply to each screen. What they do not give you is the shape of the
work: how to keep 71 files consistent, how to know which are actually done, how to delegate
without the delegation becoming a fiction, and how to prove at the end that nothing broke. Those
are the things this file is about, and every trap in it was stepped in during a real rollout.

**Read `verification.md` alongside this.** That file is about proving one pass didn't break the
app. This one is about getting through the pass itself.

---

## The order the work wants

Skipping a step is how you end up with 71 files that disagree with each other.

1. **Snapshot the behaviour surface before touching anything.** `rollout/identity.mjs snapshot`
   against the pristine tree. This is the thing you will diff against at the end, and it cannot
   be reconstructed later — a baseline taken after the pass freezes the redesign and reports
   zero failures while comparing nothing.
2. **Build the map.** `rollout/map.mjs` generates the origin ↔ current table with per-page
   state. It is the work queue, the progress report and the reviewer's index in one file, and
   it is regenerated rather than maintained because a hand-kept one goes stale within a day and
   everyone keeps trusting it.
3. **Design the system first, once.** Tokens, primitives, the palette, the type scale. Every
   page converted against a moving design system produces 71 slightly different answers. Land
   the shared layer, then freeze it for the duration of the rollout.
4. **Pilot on two or three real pages.** Not the easiest ones and not the biggest — the ones
   that represent the middle. The pilot's job is to find the ambiguities in the primitives
   before 12 agents each resolve them differently.
5. **Wave the rest out through subagents**, in batches, each batch writing its own ledger shard.
6. **Review round.** A second set of agents, each comparing a converted page against its
   origin, recording a verdict per file.
7. **Recheck the failures.** Every `fail` gets repaired and re-reviewed, and the re-review is a
   different record from the original — not an edit of it.
8. **Close with the gates**: the map regenerated, the ledger audited, the identity diff read,
   and the render/verification loop from `verification.md` run over the whole app.

---

## Delegating without the delegation becoming a fiction

This is where large passes actually fail. An agent that returns "all pages reviewed, no issues"
has usually read nothing, and you cannot tell from the sentence.

**What each worker gets:**
- The exact files it owns, and the explicit statement that it must not touch any other file.
- The frozen shared layer — the token names and the primitive components with their props — so
  it does not invent a variant of something that already exists.
- The origin path for each of its files, from the map. Without this a reviewer compares the
  file against its memory of what it should look like.
- What must survive, stated as a checklist rather than as "preserve everything".
- The record format, and the instruction to write it with the tool rather than by hand.

**What each worker must return, and why the shape matters:**

| field | why |
|---|---|
| file list actually touched | catches the agent that edited a neighbour |
| per-file verdict `pass \| fail \| blocked` | a summary sentence is not a verdict |
| what it checked, specifically | "all 8 columns, the date filter and both row actions present" is checkable; "looks good" is not |
| what it could not verify | the honest remainder, which is where the real bugs live |

**Never let parallel workers write one file.** A shared ledger loses lines under concurrent
appends — the same failure as two agents editing the token layer at once. One shard per
batch, per reviewer; the tools merge them.

**Give reviewers a different set of files from the converters.** An agent reviewing its own work
confirms it. That is not a review.

**Cap concurrency and stagger starts.** Fanning out 20 agents at once against one dev server
produces timeouts that look like broken pages. The failure is invisible in the results because
the agent reports what it managed to see.

---

## The ledger, and why it needs auditing

`rollout/ledger.mjs` records one line per file per reviewer, and `audit` asks whether the
ledger is evidence or theatre. It is not a paranoid feature.

The first real rollout produced 81 review records. **36 of them shared a sentence with a record
about a different file** — one reviewer emitted the identical paragraph for eight unrelated
pages. Every one was a `pass`. Read as a whole, the ledger said "73 files reviewed and clean",
and that number would have been quoted onward as the basis for shipping.

What the audit looks for, because each of these is how a green ledger lies:

- **Reused notes.** The same sentence about two different files means at least one of them was
  not read. This is the common failure and the only one that looks like thoroughness.
- **Notes too short to check.** A pass in under a dozen words has not named what survived.
- **Files whose latest verdict is not a pass** — the open items, which a summary count hides.
- **Batch ids shared by several reviewers**, which means attribution is unreliable.

`record` refuses a `pass` with a one-line note outright. That is deliberate: the friction is the
point, and an agent that has to write down what it looked at will sometimes go and look.

---

## The map is the artifact that survives

`map.md` answers the two questions anyone joining later asks: *what did this file used to be*,
and *is it done*. Generated from the filesystem and the snapshot, never maintained by hand.

Three columns carry the weight:

- **ancestor** — the origin path, with `_(moved)_` when the file was relocated. Without a move
  table, every renamed file reads as "new, no ancestor", which looks exactly like unverified
  work and will be re-reviewed from scratch or, worse, trusted because it looks untouched.
- **state** — raw colour and utility-palette classes still present in **markup**. Counting
  class strings inside script blocks makes the gate unsatisfiable: a colour stored in a data
  array or produced by a computed is frozen for a design pass, so a scanner that counts it
  reports work that cannot be done and the number is ignored by everyone within a day.
- **wiring** — a component used in markup but never imported. This renders as an unknown
  element: a blank hole on screen, no error in source, and completely invisible to a compile
  check. It is the most common way a component swap silently deletes part of a page.

The review column pulls from the ledger, so "we checked it" and "here is the record" are the
same cell — and it will happily fill in ✔ for a copy-pasted verdict, which is why the audit runs
before the map is trusted.

---

## The identity diff is a queue, not a verdict

`rollout/identity.mjs` snapshots the logic block, the bindings, the declared emits and the API
call sites per file, then diffs. It catches what an eye misses: a dropped `v-model`, a handler
that quietly stopped being wired, a column that vanished into a restyled card.

Two things about reading it:

- **A failure is not automatically a mistake.** When you rename a route, the string literal
  inside the page's script genuinely changes and the diff correctly reports it. The output is a
  list of things to classify — intended or not — and the classification belongs in the ledger.
  A tool that reports zero changes after a large pass is more suspicious than one that reports
  fifty.
- **A moved file looks identical to a deleted one.** The diff will tell you the baselined file
  no longer exists, which is true and useless. Keep the move table and say which files moved,
  or the signal drowns.

The normalisation used must be recorded in the baseline and reused by the diff. Hashing one side
with imports stripped and the other with them kept disagrees on every file that gained an
import — which is every converted file — and reads as a catastrophic breakage of 54 pages that
were actually fine. The tool refuses that combination now, because the tempting "fix" is to
re-snapshot after the pass until the number goes to zero, and that produces a perfectly clean,
perfectly meaningless report.

---

## Traps, each of which cost a wrong conclusion

**A reviewer's confidence is not proportional to its care.** The loudest failures in a rollout
come wrapped in "verified, no issues". Trust the records that name what they checked and the
ones that admit what they could not.

**Counting the wrong thing produces an unsatisfiable gate.** Covered above — markup, not script.

**Two taxonomies describing one thing will drift.** Navigation, permission lists, route tables,
docs. If they are maintained separately they disagree by the time anyone notices, and each
disagreement is a page someone cannot reach. Derive them from one definition. This came up
twice in one project: once as the nav saying "System Settings" while the role editor said
"Advanced Settings", and once as a sidebar that hardcoded which groups start open, naming two
groups that no longer existed.

**Verification tooling can break the thing under test.** A harness file added inside the app's
served root became a build entry, killed dependency pre-bundling for the whole application, and
made a healthy redesign look data-broken. When a check says the work is broken, try to break the
check first.

**A clean run against a dead server looks identical to a clean run.** Render guards, always.
See `verification.md`.

**The first pass is never the last.** Pages that "converted" in wave one regress in wave four
when someone edits a shared primitive. The map and the gates are re-run at the end, not only in
the middle.

**Do not let the rollout quietly become a logic change.** It is genuinely tempting to fix a bug
found mid-conversion. Note it, keep it out of the pass, and report it separately — otherwise the
diff labelled "redesign" contains behaviour changes nobody reviewed as behaviour changes.

---

## What to hand back at the end

Not "all 71 pages converted". The report has five parts, and the last two are what make the
first three believable:

1. **The map**, regenerated, with the ledger column filled — the per-page status.
2. **The ledger audit** — including any reused or thin notes still present, and what was
   re-reviewed because of them.
3. **The gates** — identity diff classified, render/verification results, console parity across
   the app.
4. **What was deliberately not done** — deferred splits, pages left alone and why, work that
   needs a decision rather than a pass.
5. **What only a person can confirm** — the functional checklist from `verification.md`, with
   the routes that changed most named explicitly.

If you cannot produce item two and item three as artifacts, the rollout is not finished,
whatever the page count says.

---

## Rolling a pass over a whole application

Everything above applies per screen. When the input is an app — dozens of pages, a real codebase, a real backend — a different failure mode takes over, and it is not visual: 71 files drift apart, delegated reviews turn out to have not happened, and "all pages converted" becomes a number nobody can check.

`scripts/rollout/` and `references/rollout.md` are the machinery. The short version, in order:

1. **Snapshot the behaviour surface before touching anything** (`rollout/identity.mjs snapshot`). It hashes each file's logic block and collects its bindings, declared emits and API call sites, so "no logic changed" becomes a diff instead of a feeling. This cannot be reconstructed later — a baseline taken after the pass freezes the redesign and reports zero failures while comparing nothing.
2. **Generate the map** (`rollout/map.mjs`): origin path, conversion state, wiring check, and the latest review verdict per page. Regenerated, never hand-maintained — a stale map is worse than none because it gets trusted.
3. **Freeze the shared layer, then pilot on two or three representative pages** before delegating, so twelve agents don't each resolve the same ambiguity in the primitives differently.
4. **Wave the rest out through subagents**, each owning an explicit file list, forbidden from editing the shared layer, each writing its own ledger shard. Never let parallel workers append to one file. **Reviewers get a different set of files from the converters** — an agent reviewing its own work confirms it.
5. **Audit the ledger before believing any count** (`rollout/ledger.mjs audit`). This exists because a real rollout produced 81 review records of which 36 shared a sentence with a record about a *different file* — one reviewer emitted the identical paragraph for eight unrelated pages, every one a `pass`, and the ledger read as "73 files reviewed and clean". Reused notes, notes too thin to name what was checked, and files whose latest verdict is not a pass are exactly what an audit finds and a summary hides.
6. **Classify the identity diff rather than obeying it.** It is a review queue: renaming a route legitimately changes a string inside a page's script, and a large pass reporting zero changes is more suspicious than one reporting fifty.
7. **Then run the nothing-broke loop above** against the whole app, and hand back five things: the regenerated map, the ledger audit, the gates, what was deliberately not done, and the human functional checklist.

Prompt shapes that produced reviewable output — converter, reviewer, recheck, app-level verifier, each annotated with the failure it defends against: `references/subagent-prompts.md`.

Two rules that do not bend. **Do not fix a bug you find mid-conversion** — note it, keep it out of the pass, and report it separately, or a commit labelled "redesign" ships behaviour changes nobody reviewed as behaviour changes. And **the first pass is not the last**: pages converted in wave one regress in wave four when someone edits a shared primitive, so the map and the gates get re-run at the end, not only in the middle.


