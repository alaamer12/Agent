# Silent destruction: merges that lie

Every entry here succeeded with **exit 0** (or a plausible-looking stop)
while destroying, duplicating, or inventing content. Each has: mechanism,
detection, and the lab scenario that reproduces it on a real git
(observed on 2.46.2.windows.1; re-run `scripts/merge_lab.sh` to check on
yours).

## 1. `ours`/`theirs` flip under rebase — one flag deleted a feature

**Mechanism:** in a merge, stage 2/`--ours` = the branch you stand on. A
rebase internally flips the roles: it replays *your* commits onto *their*
base, so mid-rebase `--ours` means **upstream** and `--theirs` means **your
own work**. The words stay identical; the meaning swaps (internals §7,
end-to-end verified; lab S13).
**Detection:** none after the fact — that's the point.
**Doctrine:** never choose a side by name; bind SHAs and roles first
(conflict-method R1). Resolve rebase conflicts with content checks, not
"ours/theirs".

## 2. `-X ours` / `-X theirs` / `-s ours` as a "resolve everything" button

**Mechanism:** `-X ours` auto-wins *overlapping* hunks for one side —
exit 0, the other side's changes quietly dropped; conflicting hunks where
the other side is absent are still kept, so the result is neither "all
ours" nor "all theirs", it is *mangled*. `-s ours` goes further: **the
merge's tree is ours, entirely** — the other branch's content is discarded
by design while its history is adopted (use case: ancestry-only
bookkeeping, e.g. keeping a release line in main's history without taking
its code; NEVER a resolution strategy).
**Lab:** S12 destroys a side with exit 0.
**Detection:** `git show --remerge-diff <merge>` (the `-X` effect vanishes
when re-merged without options) or diff the merge against each parent.

## 3. `merge=union` silently duplicates

**Mechanism:** concatenates both sides' hunks — right for append-only
files (CHANGES, `.gitignore` sometimes). For structured content it
produces duplicate keys (JSON: two top-level objects; CSV: duplicate
primary keys) and the merge **succeeds**. JSON union garbage even passes
`jq -e .` because jq parses a stream (format-divergence step 7).
**Lab:** S11.
**Doctrine:** union is a per-file policy decision recorded in
`.gitattributes` with a reason, never an interactive resolution.

## 4. Reverting a merge does not undo it (re-merge is a silent no-op)

**Mechanism:** `revert -m 1` adds a new commit that inverts the merge's
net diff, but the merged branch's commits remain **ancestors of HEAD**.
Fix the branch and re-merge: git sees "already up to date" — the reverted
content stays gone while history claims integration happened.
**Lab:** S16 reproduces the no-op.
**Fix path:** revert the revert (branch continued on top), or rebuild the
branch so commits are new (`rebase --no-ff <fork-point>`). Full doctrine:
operations.md §reverting-merges; git's own `howto/revert-a-faulty-merge`.

## 5. Silent resurrection of a reverted change

**Mechanism:** the documented 3-way limitation — *"if a change is made on
both branches, but later reverted on one of the branches, that change will
be present in the merged result… only the heads and the merge base are
considered, not the individual commits"* (git-merge §MERGE STRATEGIES
closing paragraph). The reverted side's "no change" reads as
"leave-it-alone", so the **pre-revert version wins** and the revert is
quietly undone.
**Detection:** after merging, diff the result against each parent for
content you know was deleted.
**Doctrine:** reverts that must stick go forward on both lines (or via
cherry-pick of the revert), never only one side.

## 6. Rebase across merge commits drops resolutions and topology

**Mechanism:** plain rebase flattens — merge commits vanish, and the
resolutions they carried (the merge-base judgments) are recomputed from
scratch or dropped; `--rebase-merges` keeps topology, `ort` resolutions do
not survive automatically. A rebase of a branch that merged main twice can
reproduce conflicts you already solved — or worse, resolve them wrongly
with exit 0.
**Lab:** S15.
**Detection:** `git range-diff old-base..old-tip new-base..new-tip` —
compare old vs replayed commits 1:1; a resolution that changed patch-id
shows up.

## 7. rerere: exact-preimage cache that leaves the index unmerged

**Mechanism:** rerere keys on the **exact preimage** of the conflict.
Two consequences, both reproduced:
- **Reuse applies to the worktree but leaves the index unmerged** (default
  `rerere.autoupdate=false`): `k.txt` looks resolved, `git ls-files -u`
  still lists it, and committing without `git add` refuses or (after add)
  commits the cached resolution *without your review*. Lab S17.
- **Near-misses are NOT reused** — a different side-content pair with the
  same shape is a different preimage; the conflict recurs fresh. Lab S35.
  (This is the *good* property: no fuzzy matches. The bad one is trusting
  reuse.)
**Doctrine:** rerere output is a *draft*, re-verify it against current
intents (practice §1.19/§2.12); `git rerere status` / `diff` while
resolving; `rerere.requiredTests` semantics belong to the tool's docs, not
to vibes.

## 8. Evil merge vs evil resolution — the `--cc` audit

**Definitions (gitglossary / Linus 2007):** an *evil merge* is a merge
that introduces content in the merge commit itself that exists in
**neither parent** ("changes that were not in either branch" — sometimes
pragmatically necessary, e.g. adjusting a default so both features
coexist, always suspect). An *evil resolution* is different: lines that
`--cc` flags because they were moved/reworked during resolution, yet the
change genuinely exists in a parent.

**Detection procedure (this is the tested triage):**
```bash
git show --cc <merge>          # hunks that differ from BOTH parents
# for each --cc addition, search BOTH parents:
git show <merge>^1 | grep -F "<line>" ; git show <merge>^2 | grep -F "<line>"
```
- Every flagged addition found in a parent → **INTEGRATION/relocation**,
  not evil (real replay R6: all 8 sampled `--cc` additions existed in a
  parent — accusation dissolved).
- Genuine invented lines present in neither parent → evil merge: demand a
  written reason on the merge commit, or split it out as its own change
  with its own review. R3 replay shows a relocated parent edit that
  `--cc` flags *even though* parent-2 owns the change — so **`--cc`
  non-empty is a triage trigger, not a verdict**.
- `small fixups like bumping release/version name would be acceptable`
  (Linus). Anything larger means the merge is doing two jobs.

**Whole-history variant:** recompute with `git show --remerge-diff`;
divergence between the recomputed merge and the committed one is exactly
the human (or agent) intervention — evil or merely corrected, the diff
shows you which.

## 9. Binary content: markers never appear

Text merge of binary-ish bytes conflicts with a warning about NUL bytes
and **no usable `<<<<<<<` markers**; hand-splicing bytes from two versions
is how corrupt assets ship. Declare `merge=binary`, decide a side
(format-divergence step 2; lab S10).

## 10. `.gitignore` confusion around deletions

Ignore rules never un-track files; after a merge where one side deleted a
tracked file and the other modified it, "my deletion disappeared" is
usually the modify/delete conflict (DU/UD) resolved wrong, not gitignore
magic. Status codes in internals.md; lab S06/S34.

## 11. Unrelated histories forced in

`refusing to merge unrelated histories` (exit 128) is git protecting you:
two roots means **no merge base**, so every file is add/add. Merging with
`--allow-unrelated-histories` is legitimate only for the narrow cases
(vendoring a project's history into a fresh repo); as a habit it is
history-vandalism bait (practice §2.9; lab S18).

## Reading the room: exit codes prove nothing about correctness

`0` = the text machinery had nothing to say. The catalog above mostly
fails *with* exit 0. Corollary: definition-of-done is always
post-merge-verification (tests on the merged result, parent diffs,
`--cc` audit), never the exit status.
