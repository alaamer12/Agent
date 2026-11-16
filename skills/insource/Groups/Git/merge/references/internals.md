# Git merge internals — what the machine actually computes

Reference for reasoning during a conflict and for auditing afterward.
Observed on git **2.46.2.windows.1** unless marked documented-only; docs
citations are the shipped man pages of that version. Re-verify with
`scripts/merge_lab.sh` before trusting across versions.

## The 3-way model, stated mechanically

Merge input = **merge base** + **head A** + **head B** — individual commit
history is not consulted (this is why reverted-change surprises exist,
silent-destruction §5). Non-overlapping edits are both taken verbatim;
overlapping edits become conflicts. Consequences that agents get wrong:

- FF is not a merge: no base/head/B triple, no merge commit, no
  integration record (operations.md §FF).
- "Already up to date" is an *ancestry* verdict, not a content verdict
  (silent-destruction §4).
- Rename detection happens before the 3-way (diffcore), and its failures
  change the *shape* of conflicts, not just their labels (§rename below).

## Stages and the status table

On conflict, the index keeps up to three **stages** per path:
`git ls-files -u` shows them; `git show :N:path` reads them.

- Normal content conflict: stage 1 (base), 2 (ours), 3 (theirs) — all three.
- **add/add (`AA`): no stage 1** — there was no base version.
- **modify/delete (`UD` = deleted by them): no stage 3**; `DU` = deleted by
  us keeps theirs at stage 3. `DD` (both deleted) has only 2 and 3.
- One-sided modes (`AU`/`UA`) come from rename/copy detection pairing a
  path with a stage on a *different* path.

`git status --porcelain` unmerged block (X = index vs HEAD, Y = worktree vs
index; git-status §DISCUSSION — "merge here also includes rebases using the
default --merge strategy, cherry-picks, and anything else using the merge
machinery"):

```
X  Y   Meaning
-------- -----------------------
D  D   unmerged, both deleted
A  U   unmerged, added by us
U  D   unmerged, deleted by them
U  A   unmerged, added by them
D  U   unmerged, deleted by us
A  A   unmerged, both added
U  U   unmerged, both modified
```

`UU/AA/UD` reproduced locally; `DD/DU/AU` documented-only.

## Marker anatomy

`merge.conflictStyle`:
- `merge` (default): `<<<<<<< HEAD … ======= … >>>>>>> other` — no base.
- `diff3`: adds `||||||| base` section between ours and theirs.
- `zdiff3`: same information, compact — the `|||||||` section is emitted
  only where needed (git's own recommendation is diff3-or-better for
  reasoning). On the tested constructions, zdiff3 output was **byte-identical
  to diff3** — the compaction did not trigger; do not promise "smaller",
  promise "base visible".
- The `<<<<<<<` line carries the ref/label of each side (`<<<<<<< ours`
  during rebase — the flip, silent-destruction §1).
- `conflict-marker-size=<n>` (gitattributes) lengthens markers; it is also
  the documented **rerere workaround** for files that legitimately contain
  marker-looking lines (rerere detects conflicts by parsing markers).

Styles can be recreated mid-resolution: `git checkout -m <path>` or
`git checkout --conflict=diff3 <path>`. Note `--conflict=` belongs to
**git-checkout**, not git-diff (docs drift spotted: agents habitually
type `git diff --conflict=zdiff3`, which is invalid).

### More than two candidates: multiple merge bases, nested markers

Criss-cross history (two tips merged more than once, e.g. `M1=merge(A,B)`
and later `M2=merge(B,A)`) yields **2+ merge bases** — `git merge-base
--all` lists them. `ort`/`recursive` cannot show a base-of-bases, so they
**virtually merge the bases first**, and when that inner merge conflicts,
the conflicted virtual base is embedded in the worktree file as a **nested
region with longer markers**. Reproduced (lab S36, 2.46.2, diff3 style):

```
<<<<<<< HEAD                          <- outer, width 7
X-EDIT
||||||| merged common ancestors
<<<<<<<<< Temporary merge branch 1    <- nested, width 9 (escalates +2/level)
A-EDIT
||||||||| <sha>
line2
=========
B-EDIT
>>>>>>>>> Temporary merge branch 2
=======
Y-EDIT                              <- outer theirs
>>>>>>> Y
```

Facts that matter:

- The literal labels `Temporary merge branch 1/2` are the fingerprint of a
  criss-cross base merge. Marker widths escalate per nesting level
  (7 → 9 → 11), which makes unambiguous parsing possible:
  `scripts/conflict_blocks.py` (see conflict-method.md §Capture).
- A region can hold **more than two candidate versions** of the same lines
  (X, Y, A, B above). The index still has exactly **three stages** — the
  nested mess lives inside the stage-1 blob (`git show :1:f`), so stage
  reads and marker parsing are complementary, not alternatives.
- **Octopus is not a source of this**: merging 3+ heads *aborts* instead of
  leaving conflicts (observed exit 2; lab S19). Nested markers always mean
  multiple bases, never multiple heads.
- Manual marker surgery on a nested file is where agents corrupt content;
  parse or resolve stage-wise instead. Same-width pathological markers only
  occur when files legitimately contain marker-looking lines — the
  documented defense is `conflict-marker-size` (also the rerere workaround,
  internals §rerere).

## Odd path shapes and special contents (all reproduced on 2.46.2)

Standard content-conflict machinery assumes *paths keep their meaning*.
Four classes break that assumption; each has its own signature:

**Directory/file conflict (D/F)** — one side makes `x` a file where the
other has directory `x/`. Git cannot put both on disk, so it *rescues* the
file version to a synthetic path: `CONFLICT (file/directory): … moving it
to x~<side> instead`, with the rescued entry at stage 2 or 3 (`AU`/`UA`
status; `<side>` is `HEAD` or the merged branch depending on direction —
lab S39). Resolution: decide whether the path is a dir or a file, delete
the loser, move the rescued content in, `git add` both paths. Never leave
`x~something` in a commit.

**Case-only filename collision** (`File.txt` vs `FILE.TXT`) on
case-insensitive filesystems (Windows/macOS default). Git stores both
spellings; the filesystem holds ONE file. A rename-case-on-one-side +
edit-on-the-other merge leaves **both index entries with one disk file**:
`A FILE.TXT` + `UD File.txt` (or DU), and checkouts fight over the name
(lab S40). Resolution: keep one spelling (`git rm --cached <loser>` +
`git add` the chosen content), and decide the case policy once in the
project conventions; `core.ignorecase` governs the FS behavior, not the
conflict.

**Submodule (gitlink) conflict** — both sides advanced the recorded
submodule commit. Message `Failed to merge submodule sm` +
`CONFLICT (submodule)`; status `UU sm`; `git ls-files -u` shows THREE
entries at mode **160000** whose "blobs" are the base/ours/theirs
submodule SHAs (lab S41). Git itself warns only *trivial* cases auto-merge
(one side's recorded commit an ancestor of the other's — fast-forwards
silently; non-ancestor pairs conflict). Resolution procedure: go INTO the
submodule, merge (or pick between) the two SHAs the stages name, commit
there, then `git add <path>` in the superproject to record the result. If
the submodule history genuinely diverged, that merge is a real code merge
— this skill's doctrine applies one level down.

**Git LFS pointer conflict** — with LFS, the stored blob is a 3-line
pointer (`version …`, `oid sha256:…`, `size …`), so git line-merges
POINTERS: a binary conflict looks like a trivial 1-line text conflict on
`oid` (lab S42). The danger is field-splicing: taking `oid` from one side
and `size`/`version` from the other yields a syntactically-plausible,
corrupted pointer. Resolution: choose a side *wholesale* per file (stage
2 or 3 verbatim), or re-produce the binary and re-add — never edit a
pointer by hand. Ensure git-lfs filters are installed in every cloning
environment; a clone without the filter smudges pointers as file content
and poisons subsequent merges.

## Strategies

- `ort` — the default since 2.34 ("Ostensibly Recursive's Twin"): single
  pass, renames-aware, no recursion explosion. Options `-X ours/theirs`,
  `-X ignore-space-change/ignore-all-space/ignore-blank-lines/
  ignore-cr-at-eol`, `-X renormalize`, `-X diff-algorithm=…`.
- `recursive` — legacy default; same option space plus `-X no-renames`;
  subtree extension.
- `resolve` — simplest 3-way, no renames.
- `octopus` — merging ≥3 branches at once; **never fast-forwards**, and
  **aborts instead of leaving conflicts**: on the tested version it exited
  **2** with `Merge with strategy octopus failed.` (observed; note the doc
  itself is silent — see exits below). N-way conflicts are "fix branches
  first, pairwise" territory.
- `ours` — the strategy that discards content by design (not a resolution
  tool; silent-destruction §2).
- `subtree` — niche; detection-and-advice only in this skill.

`ort` honors `diff-algorithm` (its own default `histogram`) and ignores the
recursive-only option names `no-renames`/`patience` as such — one more
place where docs inherited from the recursive era mislead.

## Exit codes — empirical, undocumented

`git-merge(1)` in 2.46.2 **has no EXIT STATUS section** (verified by
heading scan of the shipped page). Measured locally:

| Situation | Exit |
|---|---|
| clean merge / already up to date | 0 |
| conflicted merge (ort) | 1 |
| refusing unrelated histories | 128 |
| `--abort` with no merge in progress | 128 |
| octopus needing manual resolution | 2 (observed) |
| `git stash` during conflicted merge | 1 |

Treat as *observed on this version*, never contract. Contrast:
`git merge-base --is-ancestor` **does** document numerics (0 true / 1
false / other-nonzero error). Scripts must branch on "0 vs nonzero"
wherever the code is not load-bearing; where it is (e.g. octopus), re-measure.

## Rename detection and what a miss costs

`gitdiffcore(7)`: `-M`/`-C` similarity detection; `diffcore-break` splits a
"complete rewrite" filepair into delete+create at ≥50%-of-smaller default
change. Merge-side knobs (`git-merge(1)` §CONFIGURATION):
`merge.renames`, `merge.renameLimit` (default 7000 — large trees silently
exhaust it), `merge.directoryRenames` (default `conflict`; with `false`,
renamed-group files are "left behind in the old directory").

Missed rename = delete+add: the other side's edits to the old path and the
new path's content no longer share a path → duplicated file or both
versions kept, edits applied to the wrong path. Linus, 2007: *"we do
actually depend on the similarity analysis being 'good' — because it
matters a lot for things like merging."* Detection during work: `git log
--follow <path>`, `git diff -M --stat` on each side; after merges: look
for near-duplicate files.

## Binary detection, and the `-diff` trap

Git's textness test for unspecified attributes: heuristics on content
(NUL bytes in the early part of the file ⇒ binary), then
`core.autocrlf`/`text=auto` policy. The **verified trap**: `-diff` marks a
file binary **for diffs only** — the merge still ran the *text* driver and
produced ordinary `<<<<<<<` markers on `b.dat -diff` content. To route a
path to the binary driver you need `-merge`, `merge=binary`, or genuinely
binary bytes. Corollary: "Binary files differ" in review does NOT mean the
merge treated it as binary.

`working-tree-encoding` (non-UTF-8): files are "interpreted as binary and
consequently cannot be merged" — documented; interop with other clients is
the listed risk.

## Merge drivers (gitattributes + config)

Built-ins (gitattributes §merge): `text` (3-way with markers), `binary`
("keep the version from your branch in the work tree, but leave the path
in the conflicted state"), `union` ("take lines from both versions… added
lines end up in **random order** and the user should verify… **Do not use
this if you do not understand the implications**" — the docs themselves
are the warning; reproduced: duplicated `l3` context line, exit 0).

Custom drivers are **defined in `.git/config`**, referenced from
`.gitattributes` (`*.json merge=jdriver`):

```ini
[merge "jdriver"]
    name = JSON 3-way
    driver = python3 json3way.py %O %A %B %L %P
    recursive = binary
```

Contract (verbatim semantics): `%O` base, `%A` ours, `%B` theirs as temp
files; **the driver writes its result into `%A`**; exit 0 = clean;
nonzero = conflict; **exit >128 = crash → the merge itself fails** (distinct
from producing a conflict — a crashing driver must not return 137 by
accident); `%L` marker size, `%P` final path, `%S/%X/%Y` stage labels.
`recursive = binary` guards the internal merges when multiple merge bases
exist — the same multi-base reality that makes `recursive`/`ort` "recursive".

`merge.renormalize=true` (or `-X renormalize`): virtual checkout+check-in
of all three stages before merging — resolves *filter-related* conflicts
automatically "as long as smudge→clean is idempotent"; non-idempotent
filters can still conflict. This is the EOL/filter-conflict killer
(format-divergence step 4).

## rerere, precisely

Keys on the **conflicted automerge text** (the marker file), not on file
or commit identity. Lifecycle: `merge` (conflict) records **preimage**;
`git add`/`commit` of the resolved file records **resolution**; a later
*identical* preimage prints `Resolved '<f>' using previous resolution.`
and re-applies the 3-way of (old preimage, old resolution, new preimage)
— if that inner merge is clean, the worktree gets the answer. Two
switches/verbs:
- default (`rerere.enabled=true`, autoupdate unset): **worktree updated,
  index left `UU`** — `git ls-files -u` still shows 3 stages; naive
  "continue" fails at commit.
- `--rerere-autoupdate` / `rerere.autoupdate=true`: message verb changes
  to `Staged`, index is resolved (`M` not `UU`).
- different side contents ⇒ different preimage ⇒ **no reuse** (reproduced).
- `git rerere status|remaining|diff|forget|clear|gc` — `remaining` also
  lists what rerere *cannot* track (conflicting submodules). `clear` runs
  automatically on `rebase/am --skip|--abort`. Prune defaults: unresolved
  15 days, resolved 60.
- Trap: files containing marker-looking lines break preimage detection —
  use `conflict-marker-size` to disambiguate.
- Used by rebase too; Linux-kernel lesson quoted in the man page: avoid
  "useless merges" churn — record resolutions where they recur, not to
  skip review.

## State files and clean abort

`MERGE_HEAD` (+`MERGE_MODE`, `MERGE_MSG`) during merge;
`.git/rebase-merge/` or `.git/rebase-apply/` during rebase;
`CHERRY_PICK_HEAD`/`REVERT_HEAD`/`BISECT_LOG` likewise. `--quit` forgets
state without touching the worktree (safe when you want to inspect a
conflict without an "operation in progress" lock); `--abort` restores the
pre-operation state **and discards resolution work**; `--continue` after
resolution creates the commit(s). A dirty tree from *before* the operation
may not be restorable by abort — start clean (practice: "start clean or
lose the ability to back out").

## Doc-vs-behavior drift register (found while testing 2.46.2.windows.1)

| Claim circulating | Reality measured/documented |
|---|---|
| "octopus conflicting exits 2 per the docs" | git-merge(1) has **no EXIT STATUS section**; 2 is *observed*, not contracted |
| `git diff --conflict=zdiff3` | `--conflict=` is a **git-checkout** option |
| "zdiff3 output is always smaller than diff3" | identical in every tested construction; compaction did not trigger |
| "`-diff` makes git merge it as binary" | text driver ran, markers produced; binary merge needs `-merge`/`merge=binary` |
| `git cherry-pick -q` / `git revert -q` | **no `-q` exists** on those commands (lab hit this: the "silent" flag made a pick fail under `2>/dev/null` and the suite mis-scored) |
