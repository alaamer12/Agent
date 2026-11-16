---
name: merge
version: 1.2.0
author: Amr
specialized: git
description: "Merge any two histories safely - merge, rebase, cherry-pick, revert-of-merge, recovery - verified by scripts/merge_lab.sh (47 scenarios plus real replays). Answers 'which side is correct' via a 12-step procedure: correctness = merge base + both intents, union-of-intents default, tests as arbiter, incompatible intents escalated. Preflights integrations with git merge-tree (worktree untouched). Captures nested multi-base blocks (>2 candidates) via scripts/conflict_blocks.py. Covers file-vs-directory, case-collision, submodule and LFS-pointer conflict classes. Silent-destruction catalog (-X ours/theirs invert under rebase; merge=union duplicates with exit 0; merge-revert is not un-merge; rerere keeps the index unmerged; --cc evil-merge triage) and nine-rung ladder for formatted-vs-minified content. Use for conflicted merges, lockfile/JSON/i18n conflicts, bad rebase or cherry-pick recovery, force-push decisions, auditing merge commits. Not branch strategy (branch), commit prose (commit), diff review (diffs)."
when_to_use: Two lines of development must become one - resolving a conflict, doing or undoing a merge/rebase/cherry-pick, deciding which side of a both-ahead conflict is correct, merging formatted-vs-minified or generated files, or auditing a merge commit that looks wrong.
argument-hint: "[resolve|choose|rebase|cherry-pick|recover|audit|ladder|lab] <refs or situation>"
---

# merge — integrate intents, keep it loud

## The one rule

**A loud conflict is cheap; a quiet wrong merge is the most expensive
outcome available** (`IncorrectCost ≫ UnhandledCost ≫ CorrectCost`, ASE 2024
measurement). Git merges **text, not semantics** — the machine cannot know
which side is "ahead". Every tempting shortcut that trades a visible stop for
an invisible error (`-X ours`, `merge=union`, `jq -s '*'`, hand-spliced
lockfiles, "take both") is forbidden by doctrine, not preference.

## First move, before touching any conflicted content

0. **Not started yet? Pre-flight it**:
   `git merge-tree --write-tree <A> <B>` runs the real machinery on
   objects only (worktree untouched); exit 0 = clean, exit 1 = the exact
   conflict set. CI and agents should never enter a blind merge.
1. `git status` — which operation is in progress (merge / rebase /
   cherry-pick / revert all use the same machinery).
2. Bind identity: `git log --oneline --left-right HEAD...MERGE_HEAD` (or the
   equivalent second ref), `git merge-base HEAD <other>`.
3. Write down **SHA + role** ("integration target" vs "contributor work") for
   each side. The words `ours`/`theirs` **swap meaning under rebase** — never
   decide by side name.
4. Set `merge.conflictStyle=zdiff3` (or `diff3`) so the base is visible. The
   default two-way view hides exactly what you need to judge "who changed
   what against what".

## Which question are you answering

| Situation | Read |
|---|---|
| Conflict at hand; "which side is correct / both advanced" | [`references/conflict-method.md`](references/conflict-method.md) — the 12-step procedure, stage reading (`:1:/:2:/:3:`), intent recovery |
| Choosing merge vs rebase vs squash vs cherry-pick; something went wrong | [`references/operations.md`](references/operations.md) — history-policy rules, recovery playbook |
| JSON / lockfile / minified / generated file / whitespace mess | [`references/format-divergence.md`](references/format-divergence.md) — the nine-rung ladder |
| Content vanished silently, merge commit looks off, rerere surprise | [`references/silent-destruction.md`](references/silent-destruction.md) — catalog + detection per trap |
| "What does git actually do with stages/markers/renames" | [`references/internals.md`](references/internals.md) — 3-way model, status codes, drivers, observed exits |
| The file mixes merged code with marked regions; nested markers; capture blocks mechanically instead of by hand | `scripts/conflict_blocks.py` (`list`/`extract`/`assemble`), workflow in [`references/conflict-method.md`](references/conflict-method.md) §Capturing |
| `x~HEAD` paths, two case-spellings, `CONFLICT (submodule)`, pointer-file conflicts | [`references/internals.md`](references/internals.md) §Odd-path — D/F, case-collision, gitlink, LFS classes |

## The both-ahead answer, in five moves

Full procedure and citations in `conflict-method.md`; this is the shape:

1. **Neither side is authoritative.** Correctness = base + intent(A) +
   intent(B), not "main wins" or "feature wins".
2. **Read why, not what**: `git log --merge -p <file>`, the staged base
   `git show :1:<file>` — two lines of history usually show that one side
   fixed a bug and the other added a feature, and both must survive.
3. **Default to union of intents**, the only three legal outcomes GitHub
   itself documents: keep ours / keep theirs / **incorporate both**.
   Picking one side wholesale is a decision that must be justified in writing.
4. **Tests are the arbiter** — a clean textual resolution proves nothing
   (semantic conflicts are invisible to git by construction).
5. **Mutually exclusive intents are not a merge conflict; they are a design
   decision.** Stop and escalate; never guess. Security-critical code is a
   named decline category.

## The never-do list (each entry reproduced in the lab)

- Side names without SHAs (`--ours` means *upstream* mid-rebase) — S13.
- `-s ours` / `-X ours/theirs` as a "resolve everything" button: exit 0,
  content destroyed — S12.
- `merge=union` on structured data: duplicate keys/records, accepted silently
  — S11.
- `jq -s '.[0] * .[1]'` as a JSON merge: reverts one side, resurrects a
  deletion — ladder §5.
- Reverting a merge, then re-merging the fixed branch: silently under-delivers
  — re-merge nothing; revert the revert — S16.
- Rebase across merge commits: resolutions dropped, topology lost — S15;
  audit with `git show --remerge-diff`.
- Hand-merging lockfiles/generated artifacts: take one side of the *source*,
  regenerate with the pinned tool — R4 replay.
- Trusting rerere output blindly: keyed on the **exact preimage** (a near-miss
  is not reused — S35), and reuse leaves the **index unmerged** even though
  the worktree looks resolved — S17.
- Hand-editing nested markers (`Temporary merge branch`, >2 candidates from
  multiple merge bases): capture/assemble with
  `scripts/conflict_blocks.py`, or read the stage blobs — S36.
- Splicing LFS pointer fields, leaving a `x~<side>` D/F rescue path or both
  case-spellings in a commit: each is a half-resolved odd class —
  internals §Odd-path (S39/S40/S42).
- Force-push without `--force-with-lease`; rewriting any branch others built
  on ("public" is the line, not "pushed").

## Definition of done

A merge is finished only when: the conflict hunks were resolved against the
base with both intents preserved; **tests/lint ran on the merged result**, not
the pre-merge sides; derived artifacts were regenerated; `git show --cc` on
the merge commit shows only genuine integration (no invented lines — triage
in `silent-destruction.md`); and any policy decision (side-take, union,
driver) was encoded where it survives (`AGENTS.md` / `.gitattributes`), not
left as tribal knowledge.

## The lab

`scripts/merge_lab.sh` reproduces every behavioral claim above:

```bash
bash scripts/merge_lab.sh              # ~40 synthetic scenarios
SNDUK=/path/to/clone bash scripts/merge_lab.sh x R   # real-history replays
python scripts/conflict_blocks.py list <file>        # nested-marker region tree
```

Exit 0 = all green. Run it before trusting a doc claim, and extend it when
reality contradicts documentation (its INFO lines are findings, not noise).
Observed behaviors are labeled with the git version they were measured on —
docs-vs-behavior drift is recorded honestly in `internals.md`.

## Boundaries

- Decides *how* to integrate; the user/parent owns *whether* to rewrite
  public history, force-push, or delete branches — those are asked, never
  done by momentum.
- Multi-agent repos: claim/ledger mechanics live in `branch`; this skill
  only inherits its rule that shared refs are handled with leases.
- Subtree/octopus/pathological strategies get detection + advice here, not
  full workflows.
