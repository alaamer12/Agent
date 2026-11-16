# The conflict-resolution method — "which side is correct"

The question this skill exists for. A conflict where both branches advanced
is **not** a coin flip and **not** "main is newer". It is an evidence
exercise: reconstruct each side's intent from history, then produce a result
that satisfies both, or declare the collision and stop.

## The procedure (R0–R12), in order

**R0 — Re-establish state before touching content.**
```bash
git status                                  # which operation is active
git log --oneline --left-right HEAD...MERGE_HEAD   # who is who
git merge-base HEAD MERGE_HEAD              # the common ancestor
```
Triple-dot `HEAD...MERGE_HEAD` lists the unique commits on each side — the
full cast of the conflict. Unsure which operation is in progress? `git
status` answers plainly ("You have unmerged paths", "interactive rebase in
progress", …).

**R1 — Never let side names decide.** Bind each side to a SHA and a role
("integration target" / "contributor's work") in your notes *before* editing.
`ours`/`theirs` invert during rebase because the rebase replays *your*
commits onto *their* base — see `silent-destruction.md` §1. Inspect changes
rather than choosing a side by name (VS Code docs).

**R2 — Show the base.** `merge.conflictStyle=zdiff3` (or `diff3`) is a
precondition for reasoning, not a preference. Git's own man page gives the
reason: *"You can tell that the original just stated a fact, and your side
simply gave in to it while the other side tried a more positive attitude. You
can sometimes come up with a better resolution by viewing the original."*
Markers were destroyed by a previous resolution? Recreate them:
`git checkout -m <file>` or `git checkout --conflict=diff3 <file>`.

**R3 — Ask *why* each side touched those lines.** The actual methodology:
```bash
git log --merge -p -- <file>     # only the commits on each side that touched it
git show :1:<file>               # base
git show :2:<file>               # stage 2 = ours (in current-op terms; R1!)
git show :3:<file>               # stage 3 = theirs
```
A little history usually shows one side fixed a bug, the other added a
feature, and neither knew. Correctness is defined by **base + both intents**,
never by one head (git-merge: Git "asks you to resolve it by leaving what
both sides did to that area").

**R4 — Default to union of intents.** The three legal outcomes, as GitHub
documents them: keep only ours / keep only theirs / **make a new change
incorporating both**. "Wholesale one side" is a decision that silently
discards valid work and must be justified per hunk, in writing.

**R5 — Tests are the arbiter.** Semantic conflicts (both edits textually
clean, jointly broken) are invisible to git *by construction* — it merges
lines, not meaning. Fowler's point stands: tests probe whether each side's
view of semantics still holds. Run them on the **merged result**; the merge
is not finished until they have.

**R6 — Mutually exclusive intents are a design decision, not a merge
conflict.** If both sides made incompatible product/architecture choices,
**stop and report the decision** instead of guessing. (CodeRabbit's agent
policy aborts the entire resolution in exactly this case.) This is the
honest deliverable.

**R7 — Decline categories are enumerable.** Security-critical code —
authentication, encryption, secrets handling, access control — is the named
one: where resolution is genuinely ambiguous there, flag for human review.

**R8 — Keep the resolution narrow (integration only).** Linus, on evil
merges: *"refrain from abusing this option to sneak substantial changes into
a merge commit. Small fixups like bumping release/version name would be
acceptable."* No unrelated formatting, dependency bumps, or refactors ride
in the merge. Afterwards re-audit with `git show --cc <merge>` (§`audit` in
silent-destruction.md).

**R9 — Regenerate derived artifacts instead of resolving them.** Lockfiles,
generated clients, snapshots, minified bundles: see the ladder
(`format-divergence.md` step 1). Resolving their text is the classic wrong
move.

**R10 — When the resolution is going badly, take the cheap reset.**
`git merge --abort` / `git rebase --abort` / `git cherry-pick --abort`
return to the pre-operation state. Prefer abort + re-plan over improvising
on a half-baked resolution. Caveats: abort discards resolution work and may
not restore uncommitted changes that predated the operation.

**R11 — After-the-fact arbitration** of "was this resolution right?":
`git show --cc`, `git diff <parent>..<merge>`, and `git show
--remerge-diff` (recomputes the merge and diffs against what was committed —
the closest thing to an objective resolution audit).

**R12 — Reduce future both-ahead conflicts systemically:** short-lived
branches (conflict size is a function of elapsed time — "merge early and
often"), low merge skew, merge queues at scale, and per-file ownership/
policy declared in `.gitattributes` rather than improvised per conflict.

## Stage-reading cheat sheet

| Command | Shows |
|---|---|
| `git ls-files -u` | every unmerged path with its stages (1/2/3) |
| `git show :1:path` | merge base version — absent in add/add (no stage 1) |
| `git show :2:path` | "ours" = HEAD side of the current operation |
| `git show :3:path` | "theirs" — absent when the other side deleted (UD) |
| `git log --merge -p -- path` | only the side commits that conflict here |
| `git diff` during conflict | combined-vs-stages view; expect noise, prefer the stage files for structured content |

Status codes for unmerged paths (`UU` both modified, `AA` both added, `UD`
deleted by them, `DU` deleted by us, `AU`/`UA` added-one-side, `DD` both
deleted) with their stage implications are tabulated in `internals.md`.

## Capturing blocks mechanically — `scripts/conflict_blocks.py`

A conflicted file is **mixed**: auto-merged regions + HEAD content + marked
regions, and with multiple merge bases the marked regions themselves nest
(>2 candidate versions; see internals.md §multiple-bases). When that
happens — or when there are many regions, or blocks must go to a semantic
tool — do not hand-edit markers; capture, decide, reassemble:

```bash
python scripts/conflict_blocks.py list f.java              # region tree: id, span, marker width, style, nested children
python scripts/conflict_blocks.py extract f.java --region 1.1 --candidate theirs --out cand.txt
python scripts/conflict_blocks.py extract f.java --region 1 --candidate all --out blocks/   # ours/base/theirs files
python scripts/conflict_blocks.py assemble f.java --set 1=theirs --set 2=@edited.txt --out f.resolved
```

Rules that make this safe:

- Region ids are dotted by nesting depth (`1`, `1.1`, …). `list` reports
  each region's width/style/children — `Temporary merge branch` labels mean
  a criss-cross virtual base is embedded there.
- `extract` returns the verbatim block **including** any nested markers —
  feed it to the ladder tools (`format-divergence.md`), diff it against the
  stage blobs, or hand it to a human; nothing is reflowed.
- `assemble` substitutes each selection into the original bytes
  (line endings intact) and **exits 1 while markers remain** — partial
  progress needs `--allow-unresolved` explicitly. Selecting a parent takes
  its whole candidate verbatim; resolve nested ids in the same run to fold
  a nested decision upward.
- Cross-check before trusting either view: `git ls-files -u` shows the same
  path with exactly three stages no matter how deep the nesting — the
  nested versions live *inside* the stage-1 blob (`git show :1:f`). Marker
  parsing and stage reading are complementary, not alternatives.

Manual editing remains correct for small, human-scale, unnested regions:
edit *between* the markers, never retype marker lines, and re-read the
result with `git diff` before `git add`. The script is the answer when the
file is nested, huge, machine-fed, or when you must *prove* a block was
ported unchanged.

## Worked shape (from the lab and a real i18n replay)

Main kept a locale JSON pretty-printed (~1117 lines); the feature branch
added four keys to its minified (1-line) original. Git sees the whole file
changed on both sides — a textually hopeless conflict.
Base + stage read: the only **semantic** delta is four added keys (R7
ladder output: added=4, removed=0, changed=0). Resolution: leaf-wise union
against the base, then re-format once. The mechanical ladder produced a
result equal to the human historical resolution (R7 replay), which is the
proof that this reading is teachable, not artisanal.
