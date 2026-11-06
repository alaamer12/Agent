# Migrating an existing tree

> The wall is easy; the sweep is where parallel work collides and where a "mechanical" refactor
> turns into a review nobody can do. Read this before the first batch.

## 1. Order of operations

Adding the wall after the sweep means the sweep runs unpoliced and new debt lands in it. Adding it
first and freezing it at the current count means growth is caught the same day.

```
1. Land the seam file (it may be one line) and the rule registry entries.
2. Turn the rules on: hard-zero for judgment-free codes, ratcheted-and-frozen for the rest,
   stating the starting count in the same commit (§5).
3. Codemod batch by batch, disjoint files only (§2).
4. Re-bless downward with each batch, in that batch's commit.
5. Delete the exemptions that ran out of contents (§4 in arming-the-gate.md).
6. Flip any ratcheted code that reached zero to hard-zero and remove its baseline rows.
```

Step 2 before step 3 is the whole point: the wall stops the tide while the sweep drains it.

## 2. Batches are disjoint by file, not by size

Partition by **file ownership**, and put every file that a rule can touch in exactly one batch. Two
agents editing the same file in different batches produces a merge that has to be re-run through the
codemod, and a re-run over hand-edited output is where a mechanical change stops being mechanical.

| Partition by | Parallel-safe | Reviewable | Watch out |
| --- | --- | --- | --- |
| [file set per owner] | yes, if the sets are disjoint | yes — one reviewer per owner | two owners touching one shared file: that file goes in one batch only |
| [rule code] | no — one file can violate three rules and appears in three batches | good per rule | guaranteed collisions; use only for a rule whose scope is a single directory |
| [N files per batch] | no | poor | size is not a boundary; a chunk of 40 random files is unreviewable and collides |

Name a batch as a set of paths in the commit body, so "did this batch touch anything outside its
claim" is a question a reviewer can actually answer.

## 3. The counts file is the one shared resource — key it deliberately

Every batch lowers a count, and if the counts file holds one grand total per rule, **every batch
edits the same line**. That is a merge conflict by design, and it is why people hand-edit totals.
Pick one of these two, and say which in the plan:

| Strategy | How it works | Costs | Pick it when |
| --- | --- | --- | --- |
| **Keyed per file (or directory)** | the stored shape is `{ path -> { code -> count } }`; each batch rewrites only its own keys, so parallel batches touch disjoint lines | merge conflicts disappear, but a violation can move from A to B and no key changes, so total drift is invisible until a whole-tree bless | more than one person or one agent is migrating at once |
| **One final re-bless over the merged tree** | batches leave the counts file alone; after the last batch lands, one job regenerates the whole file | a single clean bless that is exactly right, but the window has to be closed: no parallel batches editing it, and the tree is unpoliced on the *number* (not the code) while it is open | one owner, one pass, a tree small enough that the bless is the same afternoon |

Default: **keyed per file during the sweep, then one authoritative whole-tree bless when the last
batch lands.** Keys keep batches disjoint; the final bless catches the movement that per-file keys
structurally cannot see. The two are sequential, not alternatives.

Three things that are not options:

- **Never two people hand-editing one total.** If the file can be edited by hand, it will be, and the
  number in it will stop being a measurement.
- **The counts file is generated, not authored.** A human commit that changes a count without
  running the scan is a rejected commit, whatever it claims.
- **A key that no longer has a file is a bug in the counts file**, not a fact about the tree. Have
  the generator drop keys for missing paths so a deletion cannot hide behind a stale row. See
  `assets/counts.example.json` for the shape.
- **During the sweep, a migration commit may only shrink the counts.** Adding an entry needs its own
  rebaseline commit with a reason, because the natural conflict resolution — "keep mine" — resurrects
  rows someone else deleted, and the ledger grows during the work whose whole point is that it
  shrinks. A diff whose only change is a deletion is reviewable at a glance; one that deletes and
  adds is a rebaseline pretending to be a batch.

## 4. Codemod mechanics

A codemod is only "safe" if these are testable, so they must be tested:

- **Idempotent.** Run it twice; the second run must change nothing. Prove it by asserting the second
  run's output is byte-identical to the first — that is a fixture assertion, not a claim.
- **Tag-only in its diff.** The diff may rename a tag, move an attribute, or change an import path.
  It may not reorder logic, reformat untouched lines, add a wrapper "for clarity", or normalise
  quotes. Every hunk must map to a transformation the batch's claim names. **A diff that changes
  more than it claims is a rejected diff** — reject the whole run, not the offending lines, because
  partial acceptance is how a codemod's side effects get merged by accident.
- **Verified by fixture plus snapshot.** Feed the codemod a small fixture tree, compare its output
  against a reviewed expected snapshot, and fail the run on any difference. A codemod with no
  fixture is a search-and-replace with confidence.
- **Applied to the snapshot target list, not the whole tree.** Restrict the run to the batch's
  declared paths; a codemod that also formats an unrelated file has broken the disjointness of §2.

The reviewer's job then shrinks to the two claims that need a human: is the transformation what the
batch says it is, and did the rule count move by exactly the amount the batch predicts.

## 5. A wall added over existing violations states its starting count in the same commit

"0 errors" from a tool that scanned nothing is indistinguishable from "0 errors" from a clean tree.
So the commit that introduces a ratcheted rule must contain its baseline number, and the commit that
introduces a hard-zero rule must contain zero offenders **and** the planted-violation fixture that
proves the rule can fire. Without the fixture in the same change, the reviewer cannot tell whether
the tree is clean or the rule is dead.

## 6. What this file does not own

The commit message format and staging discipline: `commit`. Whether the look survives the swap:
`spike`. Which name the seam should hand upward: [the-two-walls.md](./the-two-walls.md).
