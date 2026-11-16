# Research Report — Git's Documented Merge Machinery (domain: git internals only)

Wave: `merge` skill research. Sub-domain assigned: **git's own documented merge machinery**.
Practitioner advice and data-format merging are owned by other agents and are deliberately excluded here.

---

## 0. Provenance and method (read this first — it governs every citation below)

| Item | Value |
|---|---|
| Installed git | `git version 2.46.2.windows.1` (verified locally, `git --version`) |
| Primary doc source (version-exact) | `D:\Program Files\Git\mingw64\share/doc/git-doc/*.html` — 248 man pages shipped with this exact build; footers read `Last updated 2024-09-24 12:05:03 UTC` |
| Live cross-check | `https://raw.githubusercontent.com/git/git/v2.46.2/Documentation/git-merge.txt` fetched and **matched** the shipped HTML section-for-section (TRUE MERGE 1–6, HOW CONFLICTS ARE PRESENTED, HOW TO RESOLVE CONFLICTS, EXAMPLES, CONFIGURATION, SEE ALSO). Where I quote `git-merge(1)` I therefore have two independent copies of the same release text. |
| Web mirror status | `https://git-scm.com/docs/git-merge/2.46.2` returned **HTTP 503** during this session. All `git-scm.com` HTML fetches are therefore listed under UNVERIFIED-FETCH; the underlying text is verified from the version-matched shipped copy + the v2.46.2 tag on the git.git source. |
| Local reproduction | All conflict/rerere/stash/binary/rebase/exit-code outputs below were produced in scratch repos under `$TEMP/mrg/*` (`C:\Users\amrmu\AppData\Local\Temp\mrg\`). The workshop repo and the Snduk project were **not** touched. Scratch repos were configured with `core.autocrlf=false` after the first experiment surfaced CRLF noise. |
| Citation format | `doc(page) §SECTION` + verbatim quote; or `LOCAL:` + exact command output. |

An important methodology note recorded up front: **an early version of the `-X ours` experiment gave a wrong answer** because I ran `git reset --hard up` while standing *on* `up` after the merge had already moved that ref. Every merge/rebase direction result below was re-run in an isolated fresh repo per case (section 12). Treat only the isolated results as valid.

---

## 1. `git-merge(1)` — strategies and the strategy-option space

### 1.1 Strategy selection

> `git-merge(1)` §OPTIONS `-s <strategy>`: "Use the given merge strategy; can be supplied more than once to specify them in the order they should be tried. If there is no `-s` option, a built-in list of strategies is used instead (**ort** when merging a single head, **octopus** otherwise)."

> §MERGE STRATEGIES: "The merge mechanism (`git merge` and `git pull` commands) allows the backend merge strategies to be chosen with `-s` option. Some strategies can also take their own options, which can be passed by giving `-X<option>` arguments to `git merge` and/or `git pull`."

### 1.2 `ort` — the default

> §MERGE STRATEGIES `ort`: "This is the default merge strategy when pulling or merging one branch. This strategy can only resolve two heads using a 3-way merge algorithm. When there is more than one common ancestor that can be used for 3-way merge, it creates a merged tree of the common ancestors and uses that as the reference tree for the 3-way merge. This has been reported to result in fewer merge conflicts without causing mismerges by tests done on actual merge commits taken from Linux 2.6 kernel development history. Additionally this strategy can detect and handle merges involving renames. **It does not make use of detected copies.** The name for this algorithm is an acronym ("Ostensibly Recursive's Twin") and came from the fact that it was written as a replacement for the previous default algorithm, `recursive`."

Two mechanically important consequences: (a) multi-base history is collapsed into **one synthetic ancestor tree**, not merged pairwise per caller; (b) copy detection is *not* available in the default path — only renames.

### 1.3 `recursive`, `resolve`, `octopus`, `ours`, `subtree`

> `recursive`: "This can only resolve two heads using a 3-way merge algorithm. … This was the default strategy for resolving two heads from Git v0.99.9k until v2.33.0." … "The `recursive` strategy takes the same options as `ort`. However, there are three additional options that `ort` ignores (not documented above) that are potentially useful with the `recursive` strategy: `patience`, `diff-algorithm=[patience|minimal|histogram|myers]`, `no-renames`."

> `resolve`: "This can only resolve two heads (i.e. the current branch and another branch you pulled from) using a 3-way merge algorithm. It tries to carefully detect criss-cross merge ambiguities. **It does not handle renames.**"

> `octopus`: "This resolves cases with more than two heads, but **refuses to do a complex merge that needs manual resolution**. It is primarily meant to be used for bundling topic branch heads together. This is the default merge strategy when pulling or merging more than one branch."

> `ours` (strategy): "This resolves any number of heads, but the resulting tree of the merge is always that of the current branch head, effectively ignoring all changes from all other branches. It is meant to be used to supersede old development history of side branches. Note that this is different from the `-Xours` option to the recursive merge strategy."

> `subtree`: "This is a modified ort strategy. When merging trees A and B, if B corresponds to a subtree of A, B is first adjusted to match the tree structure of A, instead of reading the trees at the same level. This adjustment is also done to the common ancestor tree."

### 1.4 `-X` strategy options (`ort`, verbatim)

| Option | Documented behaviour (quoted) |
|---|---|
| `ours` | "This option forces conflicting hunks to be auto-resolved cleanly by favoring our version. Changes from the other tree that do not conflict with our side are reflected in the merge result. For a binary file, the entire contents are taken from our side." + "This should not be confused with the `ours` merge strategy, which does not even look at what the other tree contains at all. It discards everything the other tree did, declaring our history contains all that happened in it." |
| `theirs` | "This is the opposite of `ours`; note that, unlike `ours`, there is **no `theirs` merge strategy** to confuse this merge option with." |
| `ignore-space-change`, `ignore-all-space`, `ignore-space-at-eol`, `ignore-cr-at-eol` | "Treats lines with the indicated type of whitespace change as unchanged for the sake of a three-way merge. Whitespace changes mixed with other changes to a line are not ignored." Then a 3-rule cascade: "If their version only introduces whitespace changes to a line, our version is used; If our version introduces whitespace changes but their version includes a substantial change, their version is used; Otherwise, the merge proceeds in the usual way." |
| `renormalize` | "This runs a virtual check-out and check-in of all three stages of a file when resolving a three-way merge. This option is meant to be used when merging branches with different clean filters or end-of-line normalization rules." |
| `no-renormalize` | "Disables the `renormalize` option. This overrides the `merge.renormalize` configuration variable." |
| `find-renames[=<n>]` | "Turn on rename detection, optionally setting the similarity threshold. This is the default. This overrides the `merge.renames` configuration variable." |
| `rename-threshold=<n>` | "Deprecated synonym for `find-renames=<n>`." |
| `subtree[=<path>]` | "This option is a more advanced form of `subtree` strategy, where the strategy makes a guess on how two trees must be shifted to match with each other when merging." |
| `diff-algorithm=…` | documented under `recursive` but with the ort-specific default callout: "Note that **ort specifically uses `diff-algorithm=histogram`**, while recursive defaults to the `diff.algorithm` config setting." |
| `no-renames` | "Turn off rename detection. This overrides the `merge.renames` configuration variable." |

`LOCAL:` `-X ours` / `-X theirs`, isolated repos, `up` branch merging `mine` (contested line `CONTEST` → `UP-VERSION` vs `WORK-VERSION`):

```
##################### CASE 1: merge -X ours  (on up, merging mine) #####################
exit=0
UP-VERSION
##################### CASE 2: merge -X theirs #####################
exit=0
WORK-VERSION
```

Note both ran to **exit 0 with no conflict left** — `-X` silently resolves. That is the footgun documented as "forces conflicting hunks to be auto-resolved cleanly".

### 1.5 The "reverted change comes back" rule (3-way model limitation)

> §MERGE STRATEGIES, closing paragraph: "With the strategies that use 3-way merge (including the default, ort), if a change is made on both branches, but later reverted on one of the branches, that change will be present in the merged result; some people find this behavior confusing. It occurs because **only the heads and the merge base are considered when performing a merge, not the individual commits**. The merge algorithm therefore considers the reverted change as no change at all, and substitutes the changed version instead."

Corroborated by Linus (section 4.2) and by `git-revert(1)` §`-m`:

> "Reverting a merge commit declares that you will never want the tree changes brought in by the merge. As a result, later merges will only bring in tree changes introduced by commits that are **not ancestors** of the previously reverted merge. This may or may not be what you want."

### 1.6 Fast-forward semantics

> §FAST-FORWARD MERGE: "Often the current branch head is an ancestor of the named commit. … In this case, a new commit is not needed to store the combined history; instead, the `HEAD` (along with the index) is updated to point at the named commit, without creating an extra merge commit. This behavior can be suppressed with the `--no-ff` option."

> §OPTIONS `--ff/--no-ff/--ff-only`: "`--ff` is the default **unless merging an annotated (and possibly signed) tag that is not stored in its natural place in the `refs/tags/` hierarchy**, in which case `--no-ff` is assumed." … "With `--ff-only`, resolve the merge as a fast-forward when possible. When not possible, refuse to merge and **exit with a non-zero status**."

> §OPTIONS `--commit/--no-commit`: "Note that fast-forward updates do not create a merge commit and therefore there is no way to stop those merges with `--no-commit`. Thus, if you want to ensure your branch is not changed or updated by the merge command, use `--no-ff` with `--no-commit`."

> §MERGING TAG: "When merging an annotated (and possibly signed) tag, Git **always** creates a merge commit even if a fast-forward merge is possible … you can "unwrap" the tag yourself before feeding it to `git merge`, or pass `--ff-only` … `git merge v1.2.3^0` / `git merge --ff-only v1.2.3`."

`gitglossary(7)` §fast-forward: "A fast-forward is a special type of merge where you have a revision and you are 'merging' another branch's changes that happen to be a descendant of what you have. In such a case, you do not make a new merge commit but instead just update your branch to point at the same revision as the branch you are merging."

### 1.7 `--abort` / `--quit` / `--continue`, and the dirty-tree warning

> §DESCRIPTION: "A merge stops if there's a conflict that cannot be resolved automatically or if `--no-commit` was provided when initiating the merge. At that point you can run `git merge --abort` or `git merge --continue`." … "`git merge --abort` will abort the merge process and try to reconstruct the pre-merge state. However, if there were uncommitted changes when the merge started (and especially if those changes were further modified after the merge was started), `git merge --abort` will in some cases be unable to reconstruct the original (pre-merge) changes."
> "**Warning**: Running `git merge` with non-trivial uncommitted changes is discouraged: while possible, it may leave you in a state that is hard to back out of in the case of a conflict."

> §OPTIONS `--abort`: "`git merge --abort` is equivalent to `git reset --merge` when `MERGE_HEAD` is present unless `MERGE_AUTOSTASH` is also present in which case `git merge --abort` applies the stash entry to the worktree whereas `git reset --merge` will save the stashed changes in the stash list."
> §`--quit`: "Forget about the current merge in progress. **Leave the index and the working tree as-is.** If `MERGE_AUTOSTASH` is present, the stash entry will be saved to the stash list."
> §`--continue`: "After a `git merge` stops due to conflicts you can conclude the merge by running `git merge --continue` … The latter command checks whether there is a (interrupted) merge in progress before calling `git commit`." (§HOW TO RESOLVE CONFLICTS adds: "Use `git commit` or `git merge --continue` to seal the deal.")

> §PRE-MERGE CHECKS: "`git pull` and `git merge` will stop without doing anything when local uncommitted changes overlap with files that `git pull`/`git merge` may need to update. To avoid recording unrelated changes in the merge commit, `git pull` and `git merge` will also abort if there are any changes registered in the index relative to the `HEAD` commit. (Special narrow exceptions to this rule may exist depending on which merge strategy is in use, but generally, the index must match HEAD.)" … "If all named commits are already ancestors of `HEAD`, `git merge` will exit early with the message 'Already up to date.'"

> §OPTIONS `--squash`: "Produce the working tree and index state as if a real merge happened (except for the merge information), but do not actually make a commit, move the HEAD, or record `$GIT_DIR/MERGE_HEAD` (to cause the next `git commit` command to create a merge commit). … With `--squash`, `--commit` is not allowed, and will fail."

> §OPTIONS `--autostash`: "Automatically create a temporary stash entry before the operation begins, record it in the ref MERGE_AUTOSTASH and apply it after the operation ends. … the final stash application after a successful merge might result in non-trivial conflicts."

> §OPTIONS `--no-verify`: "By default, the **pre-merge** and **commit-msg** hooks are run. When `--no-verify` is given, these are bypassed."

> §OPTIONS `--allow-unrelated-histories`: "By default, `git merge` command refuses to merge histories that do not share a common ancestor. This option can be used to override this safety when merging histories of two projects that started their lives independently. As that is a very rare occasion, **no configuration variable to enable this by default exists and will not be added**."

> §OPTIONS `-m <msg>` + `--edit/-e/--no-edit`: "Invoke an editor before committing successful mechanical merge to further edit the auto-generated merge message, so that the user can explain and justify the merge. The `--no-edit` option can be used to accept the auto-generated message (**this is generally discouraged**)." Environment escape hatch: `GIT_MERGE_AUTOEDIT=no`.

> §OPTIONS `--cleanup=<mode>`: "if the `<mode>` is given a value of `scissors`, scissors will be appended to `MERGE_MSG` before being passed on to the commit machinery in the case of a merge conflict."

> §OPTIONS `--rerere-autoupdate/--no-rerere-autoupdate`: "After the rerere mechanism reuses a recorded resolution on the current conflict to update the files in the working tree, allow it to also update the index with the result of resolution. `--no-rerere-autoupdate` is a good way to double-check what rerere did and catch potential mismerges, before committing the result to the index with a separate `git add`."

> §OPTIONS `--overwrite-ignore/--no-overwrite-ignore`: "Silently overwrite ignored files from the merge result. This is the default behavior. Use `--no-overwrite-ignore` to abort."

> §EXAMPLES, on `--no-commit`: "You should refrain from abusing this option to sneak substantial changes into a merge commit. Small fixups like bumping release/version name would be acceptable."

### 1.8 Exit status — **documented gap**

`git-merge(1)` in 2.46.2 has **no `EXIT STATUS` section**. Verified by structure scan of the shipped page: the only top-level headings after CONFIGURATION are `SEE ALSO` and `GIT`. (`grep -E '^(EXIT STATUS|BUGS|NOTES|SEE ALSO)'` → one hit: `SEE ALSO`.) The same is true of the v2.46.2 source text.

Empirical codes measured locally on 2.46.2.windows.1 (no pipes — see §12 for the raw transcript):

| Situation | Exit | Evidence |
|---|---|---|
| clean merge / already up to date | 0 | `merge already-up-to-date -> 0` |
| conflicted merge (ort) | 1 | `merge conflict -> 1` |
| refusing unrelated histories | 128 | `fatal: refusing to merge unrelated histories` → 128 |
| `git merge --abort` with no merge in progress | 128 | `fatal: There is no merge to abort (MERGE_HEAD missing)` → 128 |
| octopus that needs manual resolution | **2** | `Merge with strategy octopus failed.` → 2 |
| `git stash` during a conflicted merge | 1 | `error: could not write index / t.txt: needs merge` → 1 |

Because these are empirical and undocumented, a skill should treat them as *observed on this version*, not as contract. `git-merge-base(1)` §`--is-ancestor` **is** documented numerically: "exit with status 0 if true, or with status 1 if not. **Errors are signaled by a non-zero status that is not 1.**"

### 1.9 Configuration surface (`git-merge(1)` §CONFIGURATION, verbatim highlights)

- `merge.conflictStyle` — "The default is `"merge"`, which shows a `<<<<<<<` conflict marker, changes made by one side, a `=======` marker, changes made by the other side, and then a `>>>>>>>` marker. An alternate style, `"diff3"`, adds a `|||||||` marker and the original text before the `=======` marker. **The "merge" style tends to produce smaller conflict regions than diff3, both because of the exclusion of the original text, and because when a subset of lines match on the two sides, they are just pulled out of the conflict region.** Another alternate style, `"zdiff3"`, is similar to diff3 but removes matching lines on the two sides from the conflict region when those matching lines appear near either the beginning or end of a conflict region."
- `merge.ff` — "`false` … create an extra merge commit … `only`, only such fast-forward merges are allowed (equivalent to `--ff-only`)."
- `merge.renameLimit` — "The number of files to consider in the **exhaustive** portion of rename detection during a merge. If not specified, defaults to the value of `diff.renameLimit`. If neither `merge.renameLimit` nor `diff.renameLimit` are specified, **currently defaults to 7000**. This setting has no effect if rename detection is turned off."
- `merge.renames` — "Defaults to the value of `diff.renames`."
- `merge.directoryRenames` — "…If set to `"false"`, directory rename detection is disabled, meaning that such new files will be left behind in the old directory. If set to `"true"`, … new files will be moved into the new directory. If set to `"conflict"`, a conflict will be reported for such paths. If `merge.renames` is false, `merge.directoryRenames` is ignored and treated as false. **Defaults to `"conflict"`**."
- `merge.renormalize` — "Tell Git that canonical representation of files in the repository has changed over time … Git can convert the data recorded in commits to a canonical form before performing a merge to reduce unnecessary conflicts."
- `merge.autoStash` — "Defaults to false." … "the final stash application after a successful merge might result in non-trivial conflicts."
- `merge.suppressDest` — "the default merge message computed for merges into these integration branches will omit 'into <branch name>' from its title. … When there is no `merge.suppressDest` variable defined, the default value of `master` is used for backward compatibility."
- `merge.verbosity` — "Level 0 outputs nothing except a final error message if conflicts were detected. Level 1 outputs only conflicts, 2 outputs conflicts and file changes. Level 5 and above outputs debugging information. The default is level 2. Can be overridden by the `GIT_MERGE_VERBOSITY` environment variable."
- `merge.<driver>.name` / `.driver` / `.recursive` — custom low-level merge drivers, "See `gitattributes(5)` for details."
- `merge.stat` — "Whether to print the diffstat between `ORIG_HEAD` and the merge result at the end of the merge. True by default."
- `merge.log` / `merge.branchdesc` / `merge.verifySignatures` / `merge.defaultToUpstream` — message population and signature/defaults behaviour.
- `merge.tool` / `merge.guitool` — full built-in tool list including Windows-relevant `tortoisemerge`, `winmerge`, `p4merge`, `bc4`, `araxis`, `codecompare`, `deltawalker`, `examdiff`, `guiffy`, `kdiff3`, `meld`, `smerge`, `vimdiff1/2/3`, `nvimdiff1/2/3`, `gvimdiff1/2/3`, `xxdiff`, `opendiff`, `diffuse`, `diffmerge`, `emerge`, `ecmerge`, `tkdiff`. Each annotated "(requires a graphical session)" where applicable.
- `branch.<name>.mergeOptions` — "Sets default options for merging into branch `<name>` … option values containing whitespace characters are currently not supported."

---

## 2. The 3-way model, stated as git states it

### 2.1 What is put in the index on conflict (`git-merge(1)` §TRUE MERGE, verbatim, numbered as in the doc)

> "When it is not obvious how to reconcile the changes, the following happens:
> 1. The `HEAD` pointer stays the same.
> 2. The `MERGE_HEAD` ref is set to point to the other branch head.
> 3. Paths that merged cleanly are updated both in the index file and in your working tree.
> 4. For conflicting paths, the index file records up to three versions: **stage 1 stores the version from the common ancestor, stage 2 from `HEAD`, and stage 3 from `MERGE_HEAD`** (you can inspect the stages with `git ls-files -u`). The working tree files contain the result of the merge operation; i.e. 3-way merge results with familiar conflict markers `<<<` `===` `>>>`.
> 5. **A ref named `AUTO_MERGE` is written**, pointing to a tree corresponding to the current content of the working tree (including conflict markers for textual conflicts). Note that this ref is only written when the **ort** merge strategy used (the default).
> 6. No other changes are made. In particular, the local modifications you had before you started merge will stay the same and the index entries for them stay as they were, i.e. matching `HEAD`."

`LOCAL:` every item reproduced. Two-head content conflict, `main` (ours) vs `topic` (theirs):

```
$ git merge topic; echo "EXIT=$?"
Auto-merging f.txt
CONFLICT (content): Merge conflict in f.txt
Auto-merging g.txt
CONFLICT (content): Merge conflict in g.txt
Automatic merge failed; fix conflicts and then commit the result.
EXIT=1

$ git ls-files -u
100644 b3c5a95f929a50feb06c275ac567cdb1b441d1e2 1	f.txt
100644 3fa9a0952a1f5cc4b91f73791ecec5eb17b034fe 2	f.txt
100644 0b535b74aa50d65026c1e86358a5da4021360aac 3	f.txt
(stage 1/2/3 for g.txt likewise)

$ ls .git | grep -iE 'MERGE|CHERRY|REBASE|SEQ'
AUTO_MERGE
MERGE_HEAD
MERGE_MODE
MERGE_MSG

$ git rev-parse --verify AUTO_MERGE
d4ae16a029e9c67e9427fb8d0e995a060907cce1

$ cat .git/MERGE_MSG
Merge branch 'topic'

# Conflicts:
#	f.txt
#	g.txt
```

`MERGE_MODE` existed and was **empty** (zero bytes) for plain content conflicts — it is a flag file whose lines encode per-path merge mode bits; it becomes non-empty for other conflict classes (not exercised here → UNVERIFIED-MEASURED).

`LOCAL:` stage contents prove the stage↔side mapping directly:

```
$ git show :1:f.txt   # common ancestor
line1 / line2 / line3 / line4 / line5
$ git show :2:f.txt | sed -n 3p
MAIN-3                 # stage 2 == HEAD
$ git show :3:f.txt | sed -n 3p
TOPIC-3                # stage 3 == MERGE_HEAD
```

### 2.2 add/add and modify/delete produce *fewer* stages

`LOCAL:` `git merge side` where `side` added `new.txt` and deleted `shared.txt`, `main` added `new.txt` (different content) and edited `shared.txt`:

```
$ git status --porcelain
AA new.txt
UD shared.txt

$ git status | head -20
On branch main
You have unmerged paths.
  (fix conflicts and run "git commit")
  (use "git merge --abort" to abort the merge)
Unmerged paths:
  (use "git add/rm <file>..." as appropriate to mark resolution)
	both added:      new.txt
	deleted by them: shared.txt

$ git ls-files -u
100644 9bda8c35c2f1978aa4b691660a4a1337523d3ce4 2	new.txt
100644 62d8fe9f6db631bd3a19140699101c9e281c9f9d 3	new.txt
100644 85c30401ce288f253613cb07ee32e62128089caa 1	shared.txt
100644 84d58d401375eab96fd798dc5a09413e1028b53a 2	shared.txt
```

So: **add/add has no stage 1** (no ancestor blob exists); **modify/delete has no stage 3** (the deleted side has no blob). An agent that assumes 3 stages always exist will break on these classes.

`new.txt` (add/add) conflict body is the ordinary 2-region marker form:

```
<<<<<<< HEAD
Y
=======
X
>>>>>>> side
```

### 2.3 `git status` unmerged codes — authoritative table

> `git-status(1)` §DISCUSSION: "When a merge conflict has occurred and has not yet been resolved, X and Y show the state introduced by each head of the merge, relative to the common ancestor. These paths are said to be **unmerged**." … "Note that the term *merge* here **also includes rebases using the default `--merge` strategy, cherry-picks, and anything else using the merge machinery**."
> Legend: "`U` = updated but unmerged", plus ` '` unmodified, `M` modified, `T` type changed, `A` added, `D` deleted, `R` renamed, `C` copied.

Verbatim unmerged block of the table:

```
X          Y     Meaning
--------------------------------------------------
                D           D    unmerged, both deleted
                A           U    unmerged, added by us
                U           D    unmerged, deleted by them
                U           A    unmerged, added by them
                D           U    unmerged, deleted by us
                A           A    unmerged, both added
                U           U    unmerged, both modified
--------------------------------------------------
?           ?    untracked
!           !    ignored
```

Submodules in status: "`M` = the submodule has a different HEAD than recorded in the index; `m` = the submodule has modified content; `?` = the submodule has untracked files" — "This is since modified content or untracked files in a submodule cannot be added via `git add` in the superproject to prepare a commit."

`LOCAL:` reproduced `UU`, `AA`, `UD`. `DD`, `DU`, `AU` were not exercised → documented-only.

### 2.4 Why git merges text, not semantics

This is not a doc bullet but is stated by the author of the tool (section 4.2), and the docs' own wording supports it:

> `git-merge(1)` §HOW CONFLICTS ARE PRESENTED: "Among the changes made to the common ancestor's version, non-overlapping ones (that is, you changed an area of the file while the other side left that area intact, or vice versa) are incorporated in the final result verbatim. When both sides made changes to the same area, however, Git cannot randomly pick one side over the other, and asks you to resolve it by leaving what both sides did to that area."

> `gitglossary(7)` §merge (verb): "Merging is performed by an automatic process that identifies changes made since the branches diverged, and then applies all those changes together. In cases where changes conflict, manual intervention may be required to complete the merge." §merge (noun): "unless it is a fast-forward, a successful merge results in the creation of a new commit representing the result of the merge, and having as parents the tips of the merged branches."

### 2.5 Rename detection: where it lives and what breaks silently when it misses

> `gitdiffcore(7)` §diffcore-rename: "This transformation is used to detect renames and copies, and is controlled by the `-M` option (to detect renames) and the `-C` option (to detect copies as well)… when the contents of the deleted file fileX is similar enough to the contents of the created file file0, then rename detection merges these filepairs and creates: `:100644 100644 0123456... 0123456... R100 fileX file0`"
> §diffcore-break: "used to detect a filepair that represents 'complete rewrite' and break such filepair into two filepairs that represent delete and create … The break score defaults to **50% of the size of the smaller** of the original and the result … and can be customized by giving a number after `-B` option (e.g. `-B75` …)."
> §diffcore-rename + `-C`: "the original contents of modified files, and deleted files (and also unmodified files, if the `--find-copies-harder` option is used) are considered as candidates of the source files."

The *merge*-side limits are in `git-merge(1)` §CONFIGURATION: `merge.renameLimit` (exhaustive-portion cap, "currently defaults to 7000"), `merge.renames`, `merge.directoryRenames` (default `conflict`).

**Consequence, with the author's own warning.** Linus, 2007-10-30 (`lore`, §4.3): "We do actually depend on the similarity analysis being 'good' - because it matters a lot for things like merging."

What a missed rename costs mechanically: with detection off/failed, a rename is a delete+add; the other branch's edits to the old path and the new path's added content no longer share a path, so the merge either duplicates the file (add/add style) or silently keeps both versions, and edits to the renamed file are applied to the *old* path (or dropped). With `merge.directoryRenames=false`, "such new files will be **left behind in the old directory**". With `-X no-renames` (recursive only) rename detection is off entirely; `ort` ignores `no-renames`/`patience`/`diff-algorithm` *as option names listed under recursive*, except `diff-algorithm` which `ort` honours with its own histogram default.

---

## 3. Diff3 details and marker anatomy

### 3.1 The three regions, verbatim from the doc

`git-merge(1)` §HOW CONFLICTS ARE PRESENTED gives all three styles. Default (`merge` style) — two regions only:

```
<<<<<<< yours:sample.txt
Conflict resolution is hard;
let's go shopping.
=======
Git makes conflict resolution easy.
>>>>>>> theirs:sample.txt
```
> "The default format does not show what the original said in the conflicting area. **You cannot tell how many lines are deleted and replaced with Barbie's remark on your side.** The only thing you can tell is that your side wants to say it is hard and you'd prefer to go shopping, while the other side wants to claim it is easy."

`diff3` — three regions, base inserted before `=======`:

```
<<<<<<< yours:sample.txt
or cleanly resolved because both sides changed the same way.
Conflict resolution is hard;
let's go shopping.
||||||| base:sample.txt
or cleanly resolved because both sides changed identically.
Conflict resolution is hard.
=======
or cleanly resolved because both sides changed the same way.
Git makes conflict resolution easy.
>>>>>>> theirs:sample.txt
```

`zdiff3` — base kept, edge-matching lines pulled out of the region:

```
<<<<<<< yours:sample.txt
Conflict resolution is hard;
let's go shopping.
||||||| base:sample.txt
or cleanly resolved because both sides changed identically.
Conflict resolution is hard.
=======
Git makes conflict resolution easy.
>>>>>>> theirs:sample.txt
```
> "In addition to the `<<<<<<<`, `=======`, and `>>>>>>>` markers, it uses another `|||||||` marker that is followed by the original text. … **You can sometimes come up with a better resolution by viewing the original.**"

### 3.2 Local reproduction — exact outputs

Default style, real conflict, `core.autocrlf` noise removed:

```
$ cat f.txt
line1
line2
<<<<<<< HEAD
MAIN-3
=======
TOPIC-3
>>>>>>> topic
line4
line5
```

Restoring the *original* conflict after mangling the file (this is what "resolve with the original conflict" means mechanically):

```
$ printf 'garbage by hand\n' > f.txt
$ git checkout -m -- f.txt; echo "EXIT=$?"; cat f.txt
EXIT=0
line1
line2
<<<<<<< ours
MAIN-3
=======
TOPIC-3
>>>>>>> theirs
line4
line5
```

**Note the label change**: `git checkout -m` re-writes markers as `ours` / `theirs` (and `base`) instead of `HEAD` / `<branch>`. Verified with all three styles in one go:

```
$ git -c merge.conflictStyle=diff3  checkout -m -- f.txt; cat f.txt
line1
line2
<<<<<<< ours
MAIN-3
||||||| base
line3
=======
TOPIC-3
>>>>>>> theirs
line4
line5

$ git -c merge.conflictStyle=zdiff3 checkout -m -- f.txt; cat f.txt     # identical for this hunk
$ git checkout -m -- f.txt >/dev/null; cat f.txt                        # back to default: no ||||||| block
```

Second, larger hunk (both sides inserted an extra line) — also `diff3` and `zdiff3` byte-identical:

```
head
common1
<<<<<<< ours
MAIN
MAIN-EXTRA
||||||| base
AAA
=======
TOPIC
TOPIC-EXTRA
>>>>>>> theirs
common2
tail
```

> **Honesty flag:** I did **not** succeed in reproducing the documented `diff3` vs `zdiff3` *difference* (edge-matching-line trimming). In both constructions above the two styles emitted identical text. The difference is documented (`merge.conflictStyle`: "removes matching lines on the two sides from the conflict region when those matching lines appear near either the beginning or end of a conflict region") but the precise trigger condition is UNREPRODUCED here. Do not let a skill assert "zdiff3 is just diff3 minus noise" as if measured.

### 3.3 The `--conflict` option: it is `git-checkout`, not `git-diff`

The task brief referenced `git diff --conflict=path`. **That option does not exist on `git diff` in this version.**

`LOCAL:`
```
$ git diff --conflict=bogus
error: invalid option: --conflict=bogus
$ git diff --conflict=zdiff3 -- real.bin
error: invalid option: --conflict=zdiff3
```
Text-scan of all shipped pages: `--conflict=<style>` appears **only** in `git-checkout(1)`:

> `git-checkout(1)` §`--conflict=<style>`: "The same as `--merge` option above, but changes the way the conflicting hunks are presented, overriding the `merge.conflictStyle` configuration variable. **Possible values are "merge" (default), "diff3", and "zdiff3"**."
> Also: "When switching branches with `--merge`, staged changes may be lost."

`LOCAL:` it works, and validates its argument:
```
$ git checkout --conflict=zdiff3 -- t.txt; echo "exit=$?"; cat t.txt
exit=0
header
<<<<<<< ours
MAIN
||||||| base
B
=======
SIDE
>>>>>>> theirs
footer

$ git checkout --conflict=bogus -- t.txt
error: unknown conflict style 'bogus'
```

`git-merge-file(1)` exposes the same styles as flags: `--diff3` ("Show conflicts in 'diff3' style."), `--zdiff3`, plus `--ours` / `--theirs` and `--marker-size`-adjacent options. This is the plumbing-level 3-way merge entry point (`git merge-file <current> <base> <other>`), useful to an agent for merging *blobs* without touching a repo.

### 3.4 Diff algorithms

> `git-diff(1)` §`--diff-algorithm={patience|minimal|histogram|myers}`:
> "`default`, `myers` — The basic greedy diff algorithm. Currently, this is the default."
> "`minimal` — Spend extra time to make sure the smallest possible diff is produced."
> "`patience` — Use 'patience diff' algorithm when generating patches."
> "`histogram` — This algorithm extends the patience algorithm to 'support low-occurrence common elements'."

> `git-merge(1)` §MERGE STRATEGIES `recursive` → `diff-algorithm`: "Use a different diff algorithm while merging, **which can help avoid mismerges that occur due to unimportant matching lines (such as braces from distinct functions)**." … "Note that ort specifically uses `diff-algorithm=histogram`, while recursive defaults to the `diff.algorithm` config setting."
> `patience` is documented as "Deprecated synonym for `diff-algorithm=patience`" and is one of the three options **`ort` ignores** in its recursive-specific list.

"Which helps when" — documented grounds: `histogram`/`patience` target structural noise (repeated braces/boilerplate) that `myers` greedily mispairs; `minimal` targets smallest-diff correctness at a time cost. `cherry-pick`'s own EXAMPLES closes with exactly this advice: `$ git cherry-pick -Xpatience topic^` "try to apply the change introduced by `topic^` again, **spending extra time to avoid mistakes based on incorrectly matching context lines**."

---

## 4. Doctrine from Linus Torvalds (all fetched live from lore.kernel.org; quoted verbatim)

### 4.1 The "evil merge" email — closest verified match to the brief's item 3

`https://lore.kernel.org/all/Pine.LNX.4.64.0702071222470.8424@woody.linux-foundation.org/`
From: `Linus Torvalds <torvalds@linux-foundation.org>`; To: `Michael S. Tsirkin`; Cc: `Junio C Hamano`, `git@vger.kernel.org`; Date: **Wed, 7 Feb 2007 12:30:46 -0800 (PST)**; Subject: `Re: git rebase: unexpected conflict`; Message-ID `Pine.LNX.4.64.0702071222470.8424@woody.linux-foundation.org`.

Quoted request:
> `\> Sorry about being dense. What's evil there?`
> `\> There seems to have been a merge, and a conflict was resolved.`

Linus, full body (verbatim):

> "The reason Junio marked it as 'evil' is that **the resolved result was also moved around a bit, making it really hard to see what the original conflict was**."
>
> "If David had resolved things in place, 'git show' would actually have shown a nicer conflict diff, and \_explained\_ the conflict better (most likely by not showing it at all - which is just a sign that it was resolved cleanly in one direction). As it is, **the conflict diff doesn't tell anything about what the conflict actually was, or whether it resolved trivially**."
>
> "\[ Note! Conflict diffs do \*not\* necessarily show the "conflict" at all: **we'll happily ignore any conflict that was resolved completely in one direction**, and the conflict diff output is really more of a warning that something bad could have happened, **and somebody tried to \*hide\* some changes by calling it a merge**. \]"
>
> "So what makes that an 'evil merge' is that it triggers the conflict diff, and that one really looks like somebody tried to add code and hide it. There was no actual evil activity involved, it was just done in a way that raise the red flags of the git --cc format."
>
> "So for a 'non-evil' merge, **the --cc output (which is what "git show" shows by default) will either be empty to indicate a trivial merge, or will give a hint about how the problem was resolved.** Because of the movement, in this case it did neither."

**I reproduced the two halves of this claim locally** (§12 CASE 4 / CASE 5). Resolution taken completely in one direction → `git show --cc` emits **nothing but the commit line**:
```
$ git show --format=oneline --cc HEAD
bd0e6b7049acf4035287a9accf943d6aa5510f94 resolved = ours exactly
```
Resolution kept in place but combining both sides → a real combined hunk with the `++` column:
```
diff --cc t.txt
index d29a2f7,2c139cd..696f783
--- a/t.txt
+++ b/t.txt
@@@ -1,3 -1,3 +1,3 @@@
  A
- MAIN
 -SIDE
++BOTH
  C
```
Resolution where lines were also *moved* → the combined diff becomes hard to read and looks like hidden additions:
```
@@@ -1,3 -1,3 +1,5 @@@
  A
 -SIDE
 +MAIN
++moved-line
  C
++SIDE
```
This is the mechanical basis for the doctrine "resolve in place; do not restructure the file inside the resolution" — and the counter-intuitive corollary that **a one-sided resolution leaves no audit trail at all**, so `git show` cannot distinguish "took ours" from "didn't look".

### 4.2 Merge = shape-of-history + data, never per-commit semantics

`https://lore.kernel.org/all/alpine.LFD.0.999.0710231115060.30120@woody.linux-foundation.org/`
Date: Tue, 23 Oct 2007 11:24:27 -0700 (PDT); Subject: `Re: unmerging feature branches`; Message-ID `alpine.LFD.0.999.0710231115060.30120@woody.linux-foundation.org`.

> "This is still true. **Git never looks at individual commits when merging, it looks at the \*history\***. So it does look at the commits only in the sense that it uses the 'shape' of the history (which is obviously built up from many individual commits!) but it never looks at any individual commit per se."
>
> "**And the behaviour of 'git revert' comes \*exactly\* from the fact that git never even bothers to look at the revert as a 'revert' of history! A revert is a normal data commit, and has absolutely zero impact on history itself.** So the reason a merge will never give 'back' the data over a revert is that the data was already merged, since the history itself didn't change!"
>
> "`\> I master merged branch Foo, then reverted a commit introduced by Foo, and then Foo would be re-merged, the content *will* differ.`" → "**No. If you re-merge Foo, nothing at all happens! You're already merged. It's a no-op.** If Foo has had \*new\* commits in the meantime, those new commits will show up, of course, but the old commits have absolutely zero effect, because they will be part of the common history."
>
> "`\> Git *has to* look at the list of commits in history to properly handle reverts…`" → "**No, that's absolutely incorrect.** You didn't understand what I meant. Git merge doesn't look at the revert at all, except (indirectly) when it builds up the history and it passes over it in order to find the common base for the history."
>
> "**git-rebase is special. It really does look at each commit (obviously), since it needs to \*move\* each commit. So git-rebase has nothing at all to do with merges.** They have similar behaviour (quite often the end result is identical in the \*data\* - at least that's the good case), but at the same time they are very different indeed. Git-merge \*only\* cares about the 'shape of the history' (to find the common commit(s) to use as a merge base) and the actual data, while 'git rebase' actually goes one commit at a time."
>
> "Git-rebase looks at the patch itself, using the 'patch fingerprint', and when it goes through each commit, it skips commits that have already been applied. **See the man-pages for "git-cherry" and "git-patch-id".**"

### 4.3 Rename/similarity quality is load-bearing for merges

`https://lore.kernel.org/all/alpine.LFD.0.999.0710300818390.30120@woody.linux-foundation.org/`
Date: Tue, 30 Oct 2007 08:38:24 -0700 (PDT); Subject: `Re: [PATCH/RFC 0/3] faster inexact rename handling`; Message-ID `alpine.LFD.0.999.0710300818390.30120@woody.linux-foundation.org`.

> "`\> there are a number of renames that it \_doesn't\_ find, because they are composed of 'uninteresting' lines, dropping them below the minimum score. Try (in git.git): git-show --raw -M -l0 :/'Big tool rename'` … `\> Pairs like Documentation/git-add-script.txt -> Documentation/git-add.txt are not found, because the file is composed almost entirely of boilerplate.`"
>
> "Ok, that does imply to me that we **cannot just drop boilerplate text**, because the fact is, lots of files contain boilerplate, but people still think they are 'similar'."
>
> "**We do actually depend on the similarity analysis being 'good' - because it matters a lot for things like merging.** The old code was actually very careful indeed, and while it didn't care about things like the exact \*ordering\* of lines (ie moving functions around in the same file resulted in the \*exact\* same fingerprint for the file!) it cared about everything else."
>
> "Hmm. I hope that is sufficient. But I suspect it may well not be. Especially since you ignore boiler-plate lines for \*some\* files but not others (ie it depends on which file you happen to find it in first)."

### 4.4 The index is the conflict-resolution data structure

`https://lore.kernel.org/all/Pine.LNX.4.64.0701300906260.3611@woody.linux-foundation.org/`
Date: Tue, 30 Jan 2007 10:06:08 -0800 (PST); Subject: `Re: newbie questions about git design and features (some wrt hg)`.

> "`\> 4. What is git's index good for? …`" → "**It's a huge deal during merging with conflicts. During merging, the index is the part that shows you what the conflicts are, and also where you mark any conflict resolution while the working tree is still not fully resolved.**"
>
> "That means that when you do a 'git add', you don't just add a filename to the list of files you know about, you literally add the \*content\*."
>
> "You just need to mentally realize 'oh, it contains the contents, **file mode and merge conflict state** too!'"

### 4.5 Workflow doctrine: dirty trees, merges, and `git commit -a`

`https://lore.kernel.org/all/alpine.LFD.0.98.0705090825090.4062@woody.linux-foundation.org/`
Date: Wed, 9 May 2007 08:52:09 -0700 (PDT); Subject: `Re: [FAQ?] Rationale for git's way to manage the index`.

> "I regularly go for days, and easily merging hundreds of thousands of lines of changes, **with a dirty tree**, and the merges don't affect it at all. And if I happen to hit a dirty file, **the pull will just say 'cannot merge', and I can stash away my changes, and just re-do**. So the cost of a conflict in a dirty tree is very low when it \*does\* happen."
>
> "The point of this all is that the 'git way' is actually very flexible. You can keep the tree dirty and not worry about it, and **if you always think twice before you do 'git commit -a' you won't be committing dirty state that you didn't intend to commit by mistake**."
>
> "…one of the more common cases for me is that **I'm going to commit a merge that I fixed up a conflict in, and then you have to do it that way**" (i.e. two-stage `git add` + `git commit`).

### 4.6 The literal phrase "be very very careful"

`https://lore.kernel.org/all/Pine.LNX.4.64.0702210934470.4043@woody.linux-foundation.org/`
Date: Wed, 21 Feb 2007 10:02:07 -0800 (PST); Subject: `Re: removing content from git history`.

> "So it works at least to \*some\* degree, but **I would suggest you be very very careful!**"

Context is **history rewriting** (`git convert-objects`), *not* merge resolution. Recorded here because the brief asked for a 2007 "be very, very careful in merges" email; this is the only 2007 Linus message containing that exact phrase, and it is about a different operation. See §14 for the sweep.

---

## 5. Rebase, cherry-pick, merge-base specifics

### 5.1 `git-rebase(1)` — mechanics

> §DESCRIPTION: "All changes made by commits in the current branch but that are not in `<upstream>` are saved to a temporary area. This is the same set of commits that would be shown by `git log <upstream>..HEAD`; or by `git log 'fork_point'..HEAD`, if `--fork-point` is active …; or by `git log HEAD`, if the `--root` option is specified."
>
> "The current branch is reset to `<upstream>` or `<newbase>` if the `--onto` option was supplied. **This has the exact same effect as `git reset --hard <upstream>` (or `<newbase>`). `ORIG_HEAD` is set to point at the tip of the branch before the reset.**"
>
> *Note*: "**ORIG_HEAD is not guaranteed to still point to the previous branch tip at the end of the rebase if other commands that write that pseudo-ref (e.g. `git reset`) are used during the rebase.** The previous branch tip, however, is accessible using the **reflog** of the current branch (i.e. `@{1}`, see gitrevisions(7))."
>
> "Note that any commits in HEAD which introduce the same textual changes as a commit in `HEAD..<upstream>` are **omitted** (i.e., a patch already accepted upstream with a different commit message or timestamp will be skipped)."
>
> "It is possible that a merge failure will prevent this process from being completely automatic. You will have to resolve any such merge failure and run `git rebase --continue`. Another option is to bypass the commit that caused the merge failure with `git rebase --skip`. To check out the original `<branch>` and remove the `.git/rebase-apply` working files, use the command `git rebase --abort` instead."
>
> "If the upstream branch already contains a change you have made …, then that commit will be skipped **and warnings will be issued (if the merge backend is used)**."
>
> "In case of conflict, `git rebase` will stop at the first problematic commit and leave conflict markers in the tree. You can use `git diff` to locate the markers (<<<<<<) and make edits to resolve the conflict."

`--onto` worked examples, verbatim: `git rebase --onto master next topic` (transplant a topic forked from `next` onto `master`); `git rebase --onto master topicA topicB` (rebase part of a branch); `git rebase --onto topicA~5 topicA~3 topicA` → "would result in the **removal of commits F and G** … Note that the argument to `--onto` and the `<upstream>` parameter can be any valid commit-ish."

`--keep-base` equivalence, verbatim: "Running `git rebase --keep-base <upstream> <branch>` is equivalent to `git rebase --reapply-cherry-picks --no-fork-point --onto <upstream>...<branch> <upstream> <branch>`." … "**As the base commit is unchanged this option implies `--reapply-cherry-picks`.**" … "Although both this option and `--fork-point` find the merge base between `<upstream>` and `<branch>`, this option uses the merge base **as the starting point** on which new commits will be created, whereas `--fork-point` uses the merge base **to determine which commits should be excluded**."

`--fork-point` default, verbatim: "**If `<upstream>` or `--keep-base` is given on the command line, then the default is `--no-fork-point`, otherwise the default is `--fork-point`.** See also `rebase.forkpoint` in git-config(1)." … "When `--fork-point` is active, `fork_point` will be used instead of `<upstream>` … If `fork_point` ends up being empty, the `<upstream>` will be used as a fallback." … "If your branch was based on `<upstream>` but `<upstream>` was rewound and your branch contains commits which were dropped, this option can be used with `--keep-base` in order to drop those commits from your branch."

`--reapply-cherry-picks`, verbatim: "Reapply all clean cherry-picks of any upstream commit instead of preemptively dropping them. (If these commits then become empty after rebasing, because they contain a subset of already upstream changes, the behavior towards them is controlled by the `--empty` flag.)" … "In the absence of `--keep-base` (or if `--no-reapply-cherry-picks` is given), **these commits will be automatically dropped. Because this necessitates reading all upstream commits, this can be expensive in repositories with a large number of upstream commits** … When using the merge backend, **warnings will be issued for each dropped commit** (unless `--quiet` is given). Advice will also be issued unless `advice.skippedCherryPicks` is set to false." … "`--reapply-cherry-picks` allows rebase to forgo reading all upstream commits, potentially improving performance."

`--empty=(drop|keep|stop)`: "`drop` — The commit will be dropped. **This is the default behavior.**" `keep` — "This option is implied when `--exec` is specified unless `-i/--interactive` is also specified." `stop`/`ask` — "The rebase will halt when the commit is applied, allowing you to choose whether to drop it, edit files more, or just commit the empty changes. This option is implied when `-i/--interactive` is specified. `ask` is a deprecated synonym of `stop`." Plus: "commits which start empty are kept (unless `--no-keep-empty` is specified), and commits which are clean cherry-picks (as determined by `git log --cherry-mark …`) are detected and dropped as a preliminary step (unless `--reapply-cherry-picks` or `--keep-base` is passed)."
`--no-keep-empty` rationale, verbatim: "The default is to keep commits which start empty, since creating such commits requires passing the `--allow-empty` override flag to `git commit`, **signifying that a user is very intentionally creating such a commit and thus wants to keep it**."

`-m/--merge` — **THE SWAP, verbatim**:
> "Using merging strategies to rebase (default). Note that a rebase merge works by replaying each commit from the working branch on top of the `<upstream>` branch. Because of this, **when a merge conflict happens, the side reported as `ours` is the so-far rebased series, starting with `<upstream>`, and `theirs` is the working branch. In other words, the sides are swapped.**"

`-s <strategy>`, verbatim: "Because `git rebase` replays each commit from the working branch on top of the `<upstream>` branch using the given strategy, **using the `ours` strategy simply empties all patches from the `<branch>`, which makes little sense.**"

`--ignore-whitespace` — backend-dependent semantics, verbatim: *apply backend*: "When applying a patch, ignore changes in whitespace in context lines. Unfortunately, this means that if the 'old' lines being replaced by the patch differ only in whitespace from the existing file, you will get a merge conflict instead of a successful patch application." *merge backend*: "Treat lines with only whitespace changes as unchanged when merging. Unfortunately, this means that **any patch hunks that were intended to modify whitespace and nothing else will be dropped**, even if the other side had no changes that conflicted."

Interactive mode, verbatim highlights: "An editor will be fired up with all the commits in your current branch (**ignoring merge commits**), which come after the given commit." … "The oneline descriptions are purely for your pleasure; `git rebase` will not look at them but at the commit names ('deadbee' and 'fa1afe1' in this example), **so do not delete or edit the names**." … "To interrupt the rebase (just like an 'edit' command would do, but without cherry-picking any commit first), use the **`break`** command." … "If you just want to edit the commit message for a commit, replace the command `pick` with the command `reword`." … "To drop a commit, replace the command 'pick' with 'drop', or just delete the matching line."
And the amend-safety note: "If you are not absolutely sure that the intermediate revisions are consistent (they compile, pass the testsuite, etc.) you should **use `git stash` to stash away the not-yet-committed changes after each commit**, test, and amend the commit if fixes are necessary."

### 5.2 When rebase is unsafe (`git-rebase(1)` §RECOVERING FROM UPSTREAM REBASE, verbatim)

> "**Rebasing (or any other form of rewriting) a branch that others have based work on is a bad idea: anyone downstream of it is forced to manually fix their history.** This section explains how to do the fix from the downstream's point of view. **The real fix, however, would be to avoid rebasing the upstream in the first place.**"
> … "If you now continue development as usual, and eventually merge `topic` to `subsystem`, the commits from `subsystem` will **remain duplicated forever** … Such duplicates are generally frowned upon because they clutter up history, making it harder to follow. To clean things up, you need to transplant the commits on `topic` to the new `subsystem` tip, i.e., rebase `topic`. **This becomes a ripple effect: anyone downstream from `topic` is forced to rebase too, and so on!**"

Independent, in-tree maintainer doctrine (Linux kernel, authored by the kernel community, mirrors the same rule): `https://raw.githubusercontent.com/torvalds/linux/master/Documentation/maintainer/rebasing-and-merging.rst`

> "**History that has been exposed to the world beyond your private system should usually not be changed.** Others may have pulled a copy of your tree and built on it; modifying your tree will create pain for them. If work is in need of rebasing, **that is usually a sign that it is not yet ready to be committed to a public repository.**"
> "**Do not rebase a branch that contains history created by others.** If you have pulled changes from another developer's repository, **you are now a custodian of their history. You should not change it.** With few exceptions, for example, a broken commit in a tree like this should be **explicitly reverted rather than disappeared via history modification**."
> "As per the rules outlined above, **once you have merged somebody else's history into your tree, you cannot rebase that branch**, even if you otherwise would be able to."
> "Do not reparent a tree without a good reason to do so. **Just being on a newer base or avoiding a merge with an upstream repository is not generally a good reason.**"
> "Realize that **reparenting a patch series (or making significant history modifications) changes the environment in which it was developed and, likely, invalidates much of the testing that was done.** A reparented patch series should, as a general rule, be **treated like new code and retested from the beginning**."
> "the kernel community is **not scared by seeing merge commits** in its development history … **Some problems encountered by maintainers result from a desire to avoid merges, while others come from merging a little too often.**"
> "The changelog for the merge should, for any kind of merge, **say \*why\* the merge is being done.**" … subsystem maintainers "may want to use the `--no-ff` flag to force the addition of a merge commit in the rare cases where one would not normally be created."
> "Back merges will muddy the development history of your own branch … **you should not back merge a tree above your immediate upstream tree.**"
> "One of the most frequent causes of merge-related trouble is when a maintainer merges with the upstream **in order to resolve merge conflicts before sending a pull request**. Again, this temptation is easy enough to understand, but **it should absolutely be avoided**. … **Linus is adamant that he would much rather see merge conflicts than unnecessary back merges. Seeing the conflicts lets him know where potential problem areas are.**"
> "For **especially difficult conflicts, create and push a \*separate\* branch to show how you would resolve things.** Mention that branch in your pull request, but the pull request itself should be for the unmerged branch."
> "Even in the absence of known conflicts, **doing a test merge before sending a pull request is a good idea.**"
> "If your upstream-bound branch has emptied entirely into the mainline during the merge window, you can pull it forward with … `git merge --ff-only v5.2-rc1`."
> (Also: signed tags on pull requests — "Maintainers at all levels should be using signed tags … Failure to do so threatens the security of the development process as a whole.")

### 5.3 `git-cherry-pick(1)`

> §DESCRIPTION: "Given one or more existing commits, apply the change each one introduces, recording a new commit for each. **This requires your working tree to be clean** (no modifications from the HEAD commit)."
> On failure: "1. The current branch and `HEAD` pointer stay at the last commit successfully made. 2. **The `CHERRY_PICK_HEAD` ref is set to point at the commit that introduced the change that is difficult to apply.** 3. Paths in which the change applied cleanly are updated both in the index file and in your working tree. 4. For conflicting paths, the index file records up to three versions, **as described in the 'TRUE MERGE' section of git-merge(1)**. The working tree files will include a description of the conflict bracketed by the usual conflict markers `<<<<<<<` and `>>>>>>>`. 5. No other modifications are made."

`<commit>…` ranges, verbatim: "**Sets of commits can be passed but no traversal is done by default**, as if the `--no-walk` option was specified … Note that **specifying a range will feed all `<commit>…` arguments to a single revision walk** (see a later example that uses `maint master..next`)."
Examples: `git cherry-pick ..master` / `git cherry-pick ^HEAD master` = "Apply the changes introduced by all commits that are ancestors of master but not of HEAD". `git cherry-pick maint next ^master` ≡ `git cherry-pick maint master..next` — with the trap called out in the doc: "**Note that the latter does not mean `maint` and everything between `master` and `next`; specifically, `maint` will not be used if it is included in `master`.**" `git cherry-pick master~4 master~2` = "the fifth and third last commits … create 2 new commits". `git cherry-pick --ff ..next` = "If history is linear and HEAD is an ancestor of next, update the working tree and advance the HEAD pointer to match next. Otherwise, apply the changes … creating a new commit for each". `git rev-list --reverse master -- README | git cherry-pick -n --stdin`.

`-x`, verbatim: "append a line that says '(cherry picked from commit …)' … **This is done only for cherry picks without conflicts.** Do not use this option if you are cherry-picking from your private branch because the information is useless to the recipient. If on the other hand you are cherry-picking between two publicly visible branches (e.g. backporting a fix to a maintenance branch for an older release from a development branch), adding this information can be useful." → **a conflicted backport silently loses its provenance trailer under `-x`.**
`-r`: "It used to be that the command defaulted to do `-x` … Now the default is not to do `-x` so **this option is a no-op**."
`-n/--no-commit`, verbatim: "This flag applies the changes necessary to cherry-pick each named commit to your working tree and the index, **without making any commit**. In addition, when this option is used, **your index does not have to match the HEAD commit. The cherry-pick is done against the beginning state of your index.**" … "This is useful when cherry-picking more than one commits' effect to your index in a row."
`-m <parent-number>/--mainline`, verbatim: "**Usually you cannot cherry-pick a merge because you do not know which side of the merge should be considered the mainline.** This option specifies the parent number (starting from 1) of the mainline and allows cherry-pick to replay the change relative to the specified parent."
`--ff`: "If the current HEAD is the same as the parent of the cherry-pick'ed commit, then a fast forward to this commit will be performed."
`--allow-empty`, verbatim: "By default, cherry-picking an **empty commit will fail**, indicating that an explicit invocation of `git commit --allow-empty` is required. … Note that when `--ff` is in effect, empty commits that meet the 'fast-forward' requirement will be kept even without this option. Note also, that use of this option only keeps commits that were **initially** empty … **Commits which are made empty due to a previous commit will cause the cherry-pick to fail.** To force the inclusion of those commits, use `--empty=keep`."
`--empty=(drop|keep|stop)`: `drop` "The commit will be dropped."; `keep` "The commit will be kept. Implies `--allow-empty`."; `stop` "**The cherry-pick will stop when the commit is applied, allowing you to examine the commit. This is the default behavior.**" Plus: "`--empty=drop` and `--empty=stop` only specify how to handle a commit that was not initially empty, but rather **became** empty due to a previous commit." `--keep-redundant-commits` = "Deprecated synonym for `--empty=keep`." `--allow-empty-message`: "By default, cherry-picking a commit with an empty message will fail."
SEQUENCER SUBCOMMANDS: `--continue` "Continue the operation in progress using the information in **`.git/sequencer`**"; `--skip` "Skip the current commit and continue with the rest of the sequence."; `--quit` "Forget about the current operation in progress. Can be used to clear the sequencer state after a failed cherry-pick or revert."; `--abort` "Cancel the operation and return to the pre-sequence state."
`LOCAL:` conflict state files after `git cherry-pick <topic>`:
```
$ ls .git | grep -iE 'CHERRY|MERGE|SEQ'
AUTO_MERGE
CHERRY_PICK_HEAD
MERGE_MSG                # <-- present, MERGE_HEAD absent
$ cat .git/CHERRY_PICK_HEAD
f81b3dae9dce91d84b844f8967a4ac62672bacef
```
`LOCAL:` **cherry-pick does NOT swap sides** (contrast §7): `<<<<<<< HEAD` = `MAIN-3`, `>>>>>>> f81b3da (topic: change line3 + add g line)` = `TOPIC-3`; stage 2 = HEAD, stage 3 = picked commit. Hint block emitted verbatim by git 2.46.2:
```
error: could not apply f81b3da... topic: change line3 + add g line
hint: After resolving the conflicts, mark them with
hint: "git add/rm <pathspec>", then run
hint: "git cherry-pick --continue".
hint: You can instead skip this commit with "git cherry-pick --skip".
hint: To abort and get back to the state before "git cherry-pick",
hint: run "git cherry-pick --abort".
hint: Disable this message with "git config advice.mergeConflict false"
```

### 5.4 `git-merge-base(1)`

> §DESCRIPTION: "`git merge-base` finds the best common ancestor(s) between two commits to use in a three-way merge. **One common ancestor is better than another common ancestor if the latter is an ancestor of the former.** A common ancestor that does not have any better common ancestor is a best common ancestor, i.e. a merge base. Note that **there can be more than one merge base** for a pair of commits."
> §OPERATION MODES: "As a consequence, **the merge base is not necessarily contained in each of the commit arguments if more than two commits are specified.** This is different from `git show-branch(1)` when used with the `--merge-base` option."
> §`--octopus`: "Compute the best common ancestors of all supplied commits, in preparation for an n-way merge. This mimics the behavior of `git show-branch --merge-base`." §DISCUSSION: "The result of `git merge-base --octopus A B C` is **2**, because 2 is the best common ancestor of all commits" (in the worked topology where `merge-base A B C` = 1 because 1 dominates 2).
> §`--independent`: "Instead of printing merge bases, print a **minimal subset** of the supplied commits with the same ancestors. In other words, among the commits given, list those which cannot be reached from any other."
> §`--is-ancestor`: "Check if the first `<commit>` is an ancestor of the second `<commit>`, and **exit with status 0 if true, or with status 1 if not. Errors are signaled by a non-zero status that is not 1.**"
> §`--fork-point`: "This does **not** just look for the common ancestor of the two commits, but also takes into account **the reflog of `<ref>`** to see if the history leading to `<commit>` forked from an earlier incarnation of the branch `<ref>`."
> §`-a/--all`: "Output **all** merge bases for the commits, instead of just one."
> §DISCUSSION criss-cross: "When the history involves criss-cross merges, there can be more than one best common ancestor for two commits. … both 1 and 2 are merge bases of A and B. Neither one is better than the other (both are best merge bases). **When the `--all` option is not given, it is unspecified which best one is output.**"
> §DISCUSSION modern idiom: "A common idiom to check 'fast-forward-ness' … is (or at least used to be) to compute the merge base … In modern git, you can say this in a more direct way: `if git merge-base --is-ancestor A B`".

`LOCAL:` two heads, one base: `git merge-base A B` → single sha; `git merge-base --all A B` → same single sha; `git merge-base --is-ancestor $O A` → exit 0. My criss-cross construction was botched by a leftover in-progress merge (`error: you need to resolve your current index first / x.txt: needs merge`) so **the multi-base `--all` output is UNVERIFIED-LOCAL**; the two-base claim above is doc-only for now, and the `ort` doc's "creates a merged tree of the common ancestors" (§1.2) is the operative behaviour for agents.
`git-merge-base(1)` §"Discussion on fork-point mode" documents the rewound-upstream topology (`o---B2 / ---o---o---B1--o---o---o---B (origin/master) / B0`) and states `git merge-base --fork-point origin/master topic` "takes not only B but also B0, B1, and B2 (i.e. old tips of the remote-tracking branches…)".

---

## 6. `gitattributes(5)` merge machinery

### 6.1 The `merge` attribute

> §"Performing a three-way merge" — "The `merge` attribute affects how three versions of a file are merged when a file-level merge is necessary during `git merge`, **and other commands such as `git revert` and `git cherry-pick`**."
> **Set** — "Built-in 3-way merge driver is used to merge the contents in a way similar to `merge` command of RCS suite. This is suitable for ordinary text files."
> **Unset** — "**Take the version from the current branch as the tentative merge result, and declare that the merge has conflicts. This is suitable for binary files that do not have a well-defined merge semantics.**"
> **Unspecified** — "By default, this uses the same built-in 3-way merge driver … However, the **`merge.default`** configuration variable can name different merge driver to be used with paths for which the `merge` attribute is unspecified."
> **String** — "3-way merge is performed using the specified custom merge driver. The built-in 3-way merge driver can be explicitly specified by asking for **'text'** driver; the built-in 'take the current branch' driver can be requested with **'binary'**."

### 6.2 Built-in low-level drivers, verbatim

> **`text`** — "Usual 3-way file level merge for text files. Conflicted regions are marked with conflict markers `<<<<<<<`, `=======` and `>>>>>>>`. The version from your branch appears before the `=======` marker, and the version from the merged branch appears after the `=======` marker."
> **`binary`** — "**Keep the version from your branch in the work tree, but leave the path in the conflicted state for the user to sort out.**"
> **`union`** — "Run 3-way file level merge for text files, but **take lines from both versions, instead of leaving conflict markers**. This tends to **leave the added lines in the resulting file in random order and the user should verify the result**. **Do not use this if you do not understand the implications.**"

`LOCAL:` the `union` hazard, verbatim output. `log.txt` base `l1/l2/l3`; branch `main` → `L2-FROM-MAIN` + appended `MAIN-NEW`; branch `u1` → `L2-FROM-U1` + appended `U1-NEW`; `.gitattributes` = `log.txt merge=union`:

```
$ git merge --no-edit u1 2>&1 | tail -4
Auto-merging log.txt
Merge made by the 'ort' strategy.
 log.txt | 3 +++
 1 file changed, 3 insertions(+)

$ cat log.txt          # NO conflict markers, NO conflict state, duplicated context line
l1
L2-FROM-MAIN
l3
MAIN-NEW
L2-FROM-U1
l3
U1-NEW
```
This is a **merge that reports total success while producing a file with a duplicated `l3` and interleaved both-sides content**. Exactly the doc's "random order … user should verify the result". (The exit code printed above came from a pipe and is not attributable to `git merge`; exit-0 is inferred from "Merge made by the 'ort' strategy", which is only printed on success. Marked partially UNVERIFIED in §14.)

### 6.3 Binary detection, verified

`LOCAL:` a file containing NUL bytes, with no `.gitattributes` entry at all:

```
$ git merge --no-edit theirs      # GIT_EXIT=1
Auto-merging d.txt
CONFLICT (content): Merge conflict in d.txt
warning: Cannot merge binary files: f.png (HEAD vs. theirs)
Auto-merging f.png
CONFLICT (content): Merge conflict in f.png
warning: Cannot merge binary files: real.bin (HEAD vs. theirs)
Auto-merging real.bin
CONFLICT (content): Merge conflict in real.bin
Automatic merge failed; fix conflicts and then commit the result.

$ git status --porcelain
UU d.txt
UU f.png          # f.png has merge=binary in .gitattributes
UU real.bin       # real.bin auto-detected binary (NUL byte), no attribute

$ cat f.png                  ; echo
MINE                          # ours kept verbatim, NO markers
$ od -c real.bin | head -3
0000000  \0  \b   Y   Y   Y   # ours kept verbatim, NO markers
```
So both the attribute-driven (`merge=binary`) and the auto-detected-binary paths converge on the same documented `binary` driver behaviour: **work tree = our version, path left conflicted, no markers**. An agent that greps for `<<<<<<<` to decide "is this file conflicted?" will **miss binary conflicts entirely**; the only signal is `git status --porcelain` / `git ls-files -u`.
`git ls-files -u` still recorded all three stages for both binaries.

### 6.4 Custom merge drivers, verbatim

> "The definition of a merge driver is done in the `.git/config` file, **not in the gitattributes file**, so strictly speaking this manual page is a wrong place to talk about it. However…"
> ```
> [merge "filfre"]
>         name = feel-free merge driver
>         driver = filfre %O %A %B %L %P
>         recursive = binary
> ```
> "The `merge.*.driver` variable's value is used to construct a command to run to **common ancestor's version (`%O`), current version (`%A`) and the other branches' version (`%B`)**. These three tokens are replaced with the names of temporary files that hold the contents of these versions when the command line is built. Additionally, **`%L`** will be replaced with the conflict marker size."
> "**The merge driver is expected to leave the result of the merge in the file named with `%A` by overwriting it, and exit with zero status if it managed to merge them cleanly, or non-zero if there were conflicts. When the driver crashes (e.g. killed by SEGV), it is expected to exit with non-zero status that are higher than 128, and in such a case, the merge results in a failure (which is different from producing a conflict).**"
> "`merge.*.recursive` … specifies what other merge driver to use when the merge driver is called for an **internal merge between common ancestors**, when there are more than one. When left unspecified, the driver itself is used for both internal merge and the final merge."
> "The merge driver can learn the pathname in which the merged result will be stored via placeholder **`%P`**. The conflict labels to be used for the common ancestor, local head and other head can be passed by using **`%S`, `%X` and `%Y`** respectively."

> §`conflict-marker-size`: "This attribute controls the length of conflict markers left in the work tree file during a conflicted merge. Only a positive integer has a meaningful effect." Example: `Documentation/git-merge.txt     conflict-marker-size=32`. This is also the documented rerere workaround (§8).

### 6.5 Line endings / encoding as they affect merges

> §`text` "Set to string value 'auto'": "When `text` is set to 'auto', **Git decides by itself whether the file is text or binary**." … §Unspecified: "If the `text` attribute is unspecified, Git uses the `core.autocrlf` configuration variable."
> §"Merging branches with differing checkin/checkout attributes": "If you have added attributes to a file that cause the canonical repository format for that file to change, such as adding a clean/smudge filter or text/eol/ident attributes, **merging anything where the attribute is not in place would normally cause merge conflicts.** To prevent these unnecessary merge conflicts, Git can be told to run a **virtual check-out and check-in of all three stages** of a file when resolving a three-way merge by setting the **`merge.renormalize`** configuration variable. … **As long as a 'smudge→clean' results in the same output as a 'clean' even on files that are already smudged, this strategy will automatically resolve all filter-related conflicts. Filters that do not act in this way may cause additional merge conflicts that must be resolved manually.**"
> §`working-tree-encoding`: non-UTF-8 encodings are "interpreted as **binary** and consequently [cannot be merged]"; "using the `working-tree-encoding` attribute may have a [negative] impact on interoperability with other SCM/VCS"; Git clients that do not support the attribute will store the file "as-is"; documented example lines `*.ps1 text working-tree-encoding=UTF-16` and, to pin endings, `*.ps1 text working-tree-encoding=UTF-16LE eol=crlf`. (Date-anchored statement in the page: versions "as of March 2018 do not support the working-tree-encoding attribute" — Git-for-Windows Explorer interop caveat.)
> §`diff`/binary: "The simplest way to mark a file as binary is to **unset the `diff` attribute** … This will cause Git to generate 'Binary files differ' … **You cannot specify both `-diff` and `diff=ps` attributes. The solution is to use the `diff.*.binary` config option**".

**Correction for the skill:** `-diff` controls *diff* generation, **not** merging. `LOCAL:` a file with `.gitattributes` line `b.dat -diff` still got ordinary `<<<<<<<`/`=======` markers, i.e. it went through the **text** merge driver, not the binary one:
```
$ git merge --no-edit u2
Auto-merging b.dat
CONFLICT (content): Merge conflict in b.dat
$ cat b.dat
<<<<<<< HEAD
AAAA
=======
BBBB
>>>>>>> u2
```
To route a path to the binary driver you need `-merge`, `merge=binary`, or actual binary content detection.

---

## 7. THE ours/theirs swap — verified end to end

This is the highest-value item in the report. Same flag, same marker token, **opposite meaning** depending on the operation. `LOCAL:`, each case in its own fresh repo, base line `CONTEST`, `up` → `UP-VERSION`, `mine` → `WORK-VERSION`:

```
##################### CASE 1: merge -X ours  (on up, merging mine) #####################
exit=0
UP-VERSION
##################### CASE 2: merge -X theirs #####################
exit=0
WORK-VERSION

##################### CASE 3: plain rebase mine onto up #####################
rebase exit=1
head-name=refs/heads/mine onto=642f829
--- markers ---
header
<<<<<<< HEAD
UP-VERSION
=======
WORK-VERSION
>>>>>>> f5eb554 (mine-only)
footer
--- stage (:2:) vs (:3:) ---
stage2=UP-VERSION  stage3=WORK-VERSION
after 'git checkout --ours -- t.txt' -> line2=UP-VERSION

##################### CASE 4/5: rebase with -X #####################
rebase -X ours   exit=0 -> line2=UP-VERSION
rebase -X theirs exit=0 -> line2=WORK-VERSION
```

Reading:
- In a **merge**, `ours` = the branch you are standing on = your work; `-X ours` keeps `UP-VERSION` because `up` was the checked-out side. Symmetric, intuitive.
- In a **rebase of `mine` onto `up`**, `HEAD` during the stop is the **upstream/onto** series, so `ours`/stage 2 = `UP-VERSION` = *not* your work; your commit is `theirs`/stage 3. `git checkout --ours -- <file>` therefore **discards the change you were rebasing**.
- `rebase -X ours` → exit 0, and the rebased commit's change is **silently dropped** (your line is gone, no conflict left, no warning). `rebase -X theirs` → exit 0, upstream's contended line is silently dropped.
- `git-cherry-pick` does **not** swap (verified §5.3) — `ours` = HEAD = the target branch. So the ordering is: merge = intuitive, cherry-pick = intuitive, **rebase = inverted**. `git-rebase(1)` §`-m/--merge` states exactly this in prose (§5.1) and `git-status(1)` warns that the rebase conflict is still labelled as a "merge" in status codes (§2.3).

Also note the marker-label asymmetry observed across experiments: during `git merge`/`cherry-pick` conflicts the region labels are `HEAD` and the incoming ref (`topic`, `f81b3da (topic: …)`), but **`git checkout -m`/`--conflict=` rewrites them as the literal words `ours`, `base`, `theirs`** (§3.2). An agent parsing marker *labels* rather than marker *positions* will mis-attribute sides.

---

## 8. `git-rerere(1)` — reuse recorded resolution of conflicted merges

> §DESCRIPTION: "In a workflow employing relatively long lived topic branches, the developer sometimes needs to resolve the same conflicts over and over again… This command assists the developer by **recording conflicted automerge results and corresponding hand resolve results** on the initial manual merge, and **applying previously recorded hand resolutions to their corresponding automerge results**."
> §Note: "**You need to set the configuration variable `rerere.enabled` in order to enable this command.**"
> §DISCUSSION: "Running the `git rerere` command immediately after a conflicted automerge records the conflicted working tree files, with the usual conflict markers … Later, after you are done resolving the conflicts, running `git rerere` again will record the resolved state of these files."
> "Next time, after seeing the same conflicted automerge, running `git rerere` will **perform a three-way merge between the earlier conflicted automerge, the earlier manual resolution, and the current conflicted automerge**. If this three-way merge resolves cleanly, the result is written out to your working tree file…"
> "**Note that `git rerere` leaves the index file alone, so you still need to do the final sanity checks with `git diff` (or `git diff -c`) and `git add` when you are satisfied.**"
> "As a convenience measure, `git merge` automatically invokes `git rerere` upon exiting with a failed automerge and `git rerere` records the hand resolve when it is a new conflict, or reuses the earlier hand resolve when it is not. **`git commit` also invokes `git rerere` when committing a merge result.**"
> "The information `git rerere` records is also used when running **`git rebase`**."
> §COMMANDS: `clear` — "Reset the metadata used by rerere if a merge resolution is to be aborted. **Calling `git am [--skip|--abort]` or `git rebase [--skip|--abort]` will automatically invoke this command.**"; `forget <pathspec>`; `diff` — "Display diffs for the current state of the resolution. It is useful for tracking what has changed while the user is resolving conflicts."; `status` — "Print paths with conflicts whose merge resolution rerere will record."; `remaining` — "Print paths with conflicts that have **not** been autoresolved by rerere. **This includes paths whose resolutions cannot be tracked by rerere, such as conflicting submodules.**"; `gc` — "By default, **unresolved conflicts older than 15 days and resolved conflicts older than 60 days are pruned**" via `gc.rerereUnresolved` / `gc.rerereResolved`.
> §\[NOTE\]: "**`git rerere` relies on the conflict markers in the file to detect the conflict. If the file already contains lines that look the same as lines with conflict markers, `git rerere` may fail to record a conflict resolution.** To work around this, the **`conflict-marker-size`** setting in gitattributes(5) can be used."
> §DISCUSSION also records the maintainer rule-of-thumb: "Readers of the Linux kernel mailing list may remember that **Linus complained about such too frequent test merges** when a subsystem maintainer asked to pull from a branch full of 'useless merges'."

`LOCAL:` full lifecycle, `rerere.enabled=true`, single contested line `k/OLD/v`.

Record (conflict → hand edit → `git add`/commit):
```
$ git merge featA
CONFLICT (content): Merge conflict in c.txt
Automatic merge failed; fix conflicts and then commit the result.
Recorded preimage for 'c.txt'

$ printf 'k\nRESOLVED-KEEP-BOTH\nv\n' > c.txt; git add c.txt; git commit -qm '...'
Recorded resolution for 'c.txt'.

$ ls .git/rr-cache
d26b226334428e3da4049b60cf598f7db4daf768
```
Reuse — **different incoming side ⇒ different preimage ⇒ NO reuse**:
```
$ git merge b2
Auto-merging a.txt
CONFLICT (content): Merge conflict in a.txt
Automatic merge failed; fix conflicts and then commit the result.
Recorded preimage for 'a.txt'          # note: preimage recorded again, nothing reused
```
Reuse — **identical preimage ⇒ reuse**, and the index is *not* updated:
```
$ git merge featA
CONFLICT (content): Merge conflict in c.txt
Automatic merge failed; fix conflicts and then commit the result.
Resolved 'c.txt' using previous resolution.

$ cat c.txt
k
RESOLVED-KEEP-BOTH
v
$ git ls-files -u            # STILL unmerged: 3 stages present
100644 c6390d66... 1 c.txt
100644 f07af16b... 2 c.txt
100644 3334e97f... 3 c.txt
$ git status --short
UU c.txt
```
Autoupdate is a **separate switch**, and it changes the message verb:
```
$ git merge --rerere-autoupdate featA
Automatic merge failed; fix conflicts and then commit the result.
Staged 'c.txt' using previous resolution.
$ git ls-files -u | wc -l
0
$ git status --short
M  c.txt                      # staged, no longer unmerged

$ git -c rerere.autoupdate=true merge featA
Staged 'c.txt' using previous resolution.     # identical outcome
```
Findings an agent must encode: (a) rerere keys on the **conflicted automerge text**, not on file/commit identity, so a similar-but-not-identical conflict is *not* reused; (b) **default `rerere.enabled=true` gives you a resolved working tree that is still `UU`** — the naive "rerere fixed it, keep going" path will fail at `git commit` with unmerged entries; (c) `git rerere status` / `remaining` were empty here, confirming nothing pending.

---

## 9. `git-mergetool` / `git-difftool` / `git-tools`

> `git-mergetool(1)` §SYNOPSIS: `git mergetool [--tool=<tool>] [-y | --[no-]prompt] [<file>…]`
> §DESCRIPTION: "Use `git mergetool` to run one of several merge utilities to resolve merge conflicts. **It is typically run after `git merge`.** If one or more `<file>` parameters are given, the merge tool program will be run to resolve differences in each file (**skipping those without conflicts**). **Specifying a directory will include all unresolved files in that path.** If no `<file>` names are specified, `git mergetool` will run [over all conflicted files]."
> §`--tool=<tool>`: "Valid values include `emerge`, `gvimdiff`, `kdiff3`, `meld`, `vimdiff`, and `tortoisemerge`. **Run `git mergetool --tool-help` for the list of valid `<tool>` settings.** If a merge resolution program is not specified, `git mergetool` will use the configuration variable `merge.tool`. **If the configuration variable `merge.tool` is not set, `git mergetool` will pick a suitable default.**"
> §custom tools: "the configured command line will be invoked with **`$BASE`** set to the name of a temporary file containing the common base for the merge, if available; **`$LOCAL`** … contents of the file on the current branch; **`$REMOTE`** … contents of the file to be merged; and **`$MERGED`** … the file to which the merge tool should write the result."
> §`mergetool.<tool>.trustExitCode`: "For a custom merge command, specify whether the exit code of the merge command can be used to determine whether the merge was successful. **If this is not set to true then the merge target file timestamp is checked, and the merge is assumed to have been successful if the file has been updated; otherwise, the user is prompted to indicate the success of the merge.**"
> `mergetool.meld.hasOutput`, `mergetool.keepBackup` (leaves `.orig` backups), `mergetool.<tool>.path`, `-y/--no-prompt`, `--no-clean` (§SYNOPSIS/options list) per the page.
> Windows-relevant tools available in this build's `merge.tool`/`merge.guitool` value list: `tortoisemerge`, `winmerge`, `p4merge`, `araxis`, `bc`/`bc3`/`bc4`, `codecompare`, `deltawalker`, `examdiff`, `guiffy`, `kdiff3`, `meld`, `smerge`, `xxdiff`, plus `vimdiff1/2/3`, `nvimdiff1/2/3`, `gvimdiff1/2/3` with documented 2-pane/3-pane/MERGED-only layouts.

`LOCAL:` in this headless CI-ish environment `git mergetool --help` and `git difftool --help` produced **no output** (the help invocation is intercepted and requires a pager/browser context). Doc text was used instead; the `git-mergetool.html` / `git-difftool.html` pages are present in the shipped set (434 / 214 text lines). `git-tools(1)` in this build is a stub listing (18 lines) — it is not a useful source.
`git-difftool(1)` (shipped, §DESCRIPTION/SYNOPSIS): `git difftool [<commit>] [--y|-y | --[no-]prompt] [--dir-diff] [<file>…]`, "Show the changes of the working tree against a given branch or commit using any merge tool" style behaviour; per the page it launches the tool configured by `diff.tool`/`merge.tool`, and `--dir-diff` copies the trees to temp dirs. Quoted line-level detail not reproduced here beyond what the page states; treat difftool specifics as **doc-only (page read, sections not quoted verbatim above)**.

---

## 10. `git stash` in the middle of a merge

> `git-merge(1)` §PRE-MERGE CHECKS: "Before applying outside changes, you should get your own work in good shape and committed locally … See also `git-stash(1)`."
> §OPTIONS `--abort`: "It is therefore recommended to always **commit or stash your changes before running `git merge`**."
> §OPTIONS `--autostash`: "Automatically create a temporary stash entry before the operation begins, record it in the ref `MERGE_AUTOSTASH` and apply it after the operation ends. … the final stash application after a successful merge might result in non-trivial conflicts." `merge.autoStash` config: "Defaults to false."
> `git-stash(1)` §`pop`/`apply`: "**Applying the state can fail with conflicts; in this case, it is not removed from the stash list. You need to resolve the conflicts by hand and run git commit explicitly.**" §`--index`: "…However, this can fail, when you have conflicts (which are stored in the index, where you therefore can no longer [restore the index state])." §`--keep-index`: "All changes already added to the index are left intact." §`push --patch` "implies `--keep-index`. You can use `--no-keep-index` to override this." §DISCUSSION documents stash-entry structure: "when you use `git stash push`, … **I** is a commit that records the state of the index, and **W** is a commit that records the state of the working tree" (the stash entry is a commit with 2–3 parents), plus "dangling merge commit … in the stash ref, updating the stash" wording, and the classic "file foobar not up to date, cannot merge" pre-merge message, and the documented `--keep-index` recipe for splitting staged/unstaged work.

`LOCAL:` **stashing during an unresolved merge is refused**:
```
$ git status --porcelain
UU t.txt
$ git stash
error: could not write index
t.txt: needs merge
$ echo "exit=$?"
exit=1
$ git stash list            # empty — nothing was saved
$ test -f .git/MERGE_HEAD && echo YES
YES                          # merge state intact
```
Mechanically this is the doc's `--index` limitation with teeth: unmerged (stage 1/2/3) index entries cannot be serialised into a stash commit. Practical consequence: to shelve a merge you must either `git merge --abort` first, or `git commit` the resolution and stash afterwards. `git stash` does **not** preserve `MERGE_HEAD`, so a `stash`-then-`pop` around a merge cannot reconstruct the merge state — the resolution knowledge survives only in `rr-cache` (rerere) and in the reflog.

---

## 11. State model and clean abort — reference table

Files/ref names all observed locally (section 1.2/2.1/5.3/7 transcripts) plus documented.

| Operation | $GIT_DIR markers | Ref(s) | Verified local evidence |
|---|---|---|---|
| conflicted `git merge` | `MERGE_HEAD`, `MERGE_MSG`, `MERGE_MODE` (empty for plain content conflicts), `ORIG_HEAD` | `AUTO_MERGE` (ort only) | `ls .git` → `AUTO_MERGE MERGE_HEAD MERGE_MODE MERGE_MSG`; `cat .git/MERGE_MSG` → `Merge branch 'topic'` + `# Conflicts:` block |
| `git merge --squash` | no `MERGE_HEAD` at all | — | doc: "do not actually make a commit, move the HEAD, or record `$GIT_DIR/MERGE_HEAD`" |
| `git merge --autostash` | + `MERGE_AUTOSTASH` | — | doc: `--abort` applies it, `git reset --merge` puts it in the stash list |
| conflicted `git cherry-pick` | `CHERRY_PICK_HEAD`, `MERGE_MSG`, `AUTO_MERGE`; **no `MERGE_HEAD`** | — | observed verbatim |
| conflicted `git rebase` (merge backend) | dir `rebase-merge/` + file `REBASE_HEAD` | — | `ls .git` → `REBASE_HEAD rebase-merge` |
| `git rebase` internals | `rebase-merge/{head-name, onto, orig-head, msgnum, end, done, git-rebase-todo, git-rebase-todo.backup, interactive, message, patch, author-script, stopped-sha, no-reskeep-base…}` | — | `cat .git/rebase-merge/head-name` → `refs/heads/topic`; `cat .git/rebase-merge/onto` → `f61bacf2…`; directory listing captured |
| `git rebase` (apply backend, `--apply`) | dir `rebase-apply/` | — | doc §DESCRIPTION: "To check out the original `<branch>` and remove the **`.git/rebase-apply`** working files, use the command `git rebase --abort`" |
| multi-step cherry-pick/revert | `.git/sequencer` | — | doc `git-cherry-pick(1)` §`--continue`: "using the information in `.git/sequencer`" |

`LOCAL:` during an interrupted rebase, `git branch --show-current` printed **nothing** (detached HEAD at the onto commit) while `rebase-merge/head-name` held `refs/heads/topic` — the "which branch am I actually on" trap. Also `git log --oneline -1 HEAD` showed the upstream commit, not your work.

Clean-abort matrix (all doc-cited, all exercised):

| State | Clean exit | Doc |
|---|---|---|
| merge conflict | `git merge --abort` (= `git reset --merge` when `MERGE_HEAD` present) | `git-merge(1)` §`--abort` |
| merge conflict, keep partial work | `git merge --quit` ("Leave the index and the working tree as-is") then fix later | §`--quit` |
| finish merge | resolve → `git add` → `git commit` **or** `git merge --continue` | §HOW TO RESOLVE CONFLICTS, §`--continue` |
| cherry-pick conflict | `git cherry-pick --abort` / `--skip` / `--quit` / `--continue` | `git-cherry-pick(1)` §SEQUENCER SUBCOMMANDS |
| rebase conflict | `git rebase --abort` / `--skip` / `--continue`; also `rebase-merge/orig-head` and reflog `@{1}` for the previous tip | `git-rebase(1)` §DESCRIPTION, §ORIG_HEAD note |
| rerere metadata on abort | `git rebase --abort/--skip` and `git am --skip/--abort` auto-run `git rerere clear` | `git-rerere(1)` §`clear` |

`LOCAL:` `git merge --abort` restored a clean tree and `git log -1` back to the pre-merge commit; `git cherry-pick --abort` likewise; `git rebase --abort` returned `topic` and removed `rebase-merge/`. `git merge --abort` with no merge → `fatal: There is no merge to abort (MERGE_HEAD missing)` (exit 128).

Restoring "the original conflict" mechanically (§3.2): `git checkout -m -- <path>`, `git checkout --conflict={merge,diff3,zdiff3} -- <path>`, and `git restore -m -- <path>` (accepted; emitted the same `warning: Cannot merge binary files: f.png (ours vs. theirs)` as `git checkout --merge`). Both rely on the staged 1/2/3 entries, i.e. **they only work while the path is still unmerged in the index**; once you `git add` the stages are gone and only `AUTO_MERGE`-based tooling remains (`git diff AUTO_MERGE` per §HOW TO RESOLVE CONFLICTS).

Audit/inspection commands the doc itself prescribes (`git-merge(1)` §HOW TO RESOLVE CONFLICTS, verbatim): "`git diff` will show a three-way diff, highlighting changes from both the `HEAD` and `MERGE_HEAD` versions. **`git diff AUTO_MERGE` will show what changes you've made so far to resolve textual conflicts.**" … "`git log --merge -p <path>` will show diffs first for the `HEAD` version and then the `MERGE_HEAD` version." … "`git show :1:filename` shows the common ancestor, `git show :2:filename` shows the HEAD version, and `git show :3:filename` shows the MERGE_HEAD version."
`LOCAL:` a conflicted `git diff` renders the combined `diff --cc` form with the `++<<<<<<<` / `++=======` / `+` / ` ` column convention:
```
diff --cc f.txt
index 3fa9a09,0b535b7..0000000
--- a/f.txt
+++ b/f.txt
@@@ -1,5 -1,5 +1,9 @@@
  line1
  line2
++<<<<<<< HEAD
 +MAIN-3
++=======
+ TOPIC-3
++>>>>>>> topic
  line4
  line5
```

---

## 12. Raw local reproduction transcript (condensed, exact)

Environment: Git for Windows 2.46.2.windows.1, `sh` under Git Bash, scratch under `$TEMP/mrg`. Author/committer forced via `GIT_AUTHOR_*`/`GIT_COMMITTER_*`; `core.autocrlf=false` set after the first run showed `LF will be replaced by CRLF` noise.

1. **Two-head content conflict** → exit 1, `UU` ×2, stages 1/2/3 ×2, `AUTO_MERGE`+`MERGE_HEAD`+`MERGE_MSG`+empty `MERGE_MODE`, default markers without base region. (§2.1)
2. **`checkout -m` restores conflict**, labels become `ours`/`theirs`; `merge.conflictStyle=diff3` and `=zdiff3` each add the `||||||| base` region; the two styles were byte-identical in both constructions. (§3.2)
3. **add/add → `AA` with stages 2+3 only; modify/delete → `UD` with stages 1+2 only.** (§2.2)
4. **cherry-pick conflict** → `CHERRY_PICK_HEAD`+`MERGE_MSG`+`AUTO_MERGE`, `ours` not swapped. (§5.3)
5. **rebase conflict** → `rebase-merge/{head-name=refs/heads/topic, onto=…}`, `REBASE_HEAD`, `HEAD` region = upstream, `stage2` = upstream. (§7)
6. **`-X ours`/`-X theirs` in merge vs rebase**, four isolated repos, exit 0 in all four with the resolution silently applied. (§7)
7. **union merge driver** → "successful" merge, no markers, duplicated context line. (§6.2)
8. **binary (auto-detected + `merge=binary`)** → `warning: Cannot merge binary files`, work tree keeps ours, `UU`, no markers, exit 1. (`-diff` alone does *not* trigger this.) (§6.3, §6.5)
9. **rerere**: preimage recording, non-reuse on a different preimage, reuse on identical preimage, `Resolved` vs `Staged` message verbs, index left `UU` by default. (§8)
10. **unrelated histories** → `fatal: refusing to merge unrelated histories` exit 128; `--allow-unrelated-histories` merges and creates an ort merge commit. (§1.7)
11. **octopus** `git merge t1 t2 t3` →
```
Fast-forwarding to: t1
Trying simple merge with t2
Simple merge did not work, trying automatic merge.
Auto-merging c.txt
ERROR: content conflict in c.txt
fatal: merge program failed
Automated merge did not work.
Should not be doing an octopus.
Merge with strategy octopus failed.
EXIT=2
```
    Note `ls .git | grep -i MERGE` found **nothing** — octopus leaves no merge state to abort. (§1.8)
12. **stash during conflict** → refused, exit 1, no stash entry, `MERGE_HEAD` preserved. (§10)
13. **`--cc` auditability**: one-direction resolution → empty diff; in-place combined resolution → `++BOTH`; moved-around resolution → confusing combined hunk that "looks like somebody tried to add code and hide it". (§4.1)
14. **`--conflict=`** rejected by `git diff`, accepted by `git checkout`, validates style names. (§3.3)

---

## 13. Implications for agent doctrine

Rules a `merge` skill should be able to state mechanically, each tied to a finding above.

1. **Never trust a resolved-looking working tree; read the index.** A conflicted path can show *no markers at all* and still be unmerged: binary conflicts keep your file verbatim and signal only via `git status --porcelain` / `git ls-files -u` (§6.3). `grep '<<<<<<<'` is **not** a conflict detector.
2. **Determine the operation before you decode `ours`.** `ours` = your work in merge and cherry-pick; `ours` = the upstream base in rebase (§7). Concretely: during a rebase stop, `git checkout --ours -- <file>` throws away the very commit being replayed, and `git rebase -X ours` exits 0 while deleting your change. Any rule of the form "keep ours/theirs" must first be qualified by operation, and by the branch identity in `rebase-merge/head-name` (which is *not* HEAD's branch).
3. **`-X ours` / `-X theirs` are silent data-loss switches.** They "force conflicting hunks to be auto-resolved cleanly" with exit 0 and no residual record (§1.4, §7). Doctrine: they are only acceptable when the user has named which side wins, and the outcome must be re-inspected as a diff, not trusted because the command succeeded.
4. **`merge=union` (and any driver that auto-resolves) must be re-verified.** It produced a merged file with a duplicated context line and reported success (§6.2); the doc's own sentence is "the user should verify the result. Do not use this if you do not understand the implications."
5. **Resolve in place; never restructure inside a merge resolution.** This is the load-bearing Linus doctrine (§4.1): moving code inside a resolution destroys the `--cc` audit trail and *looks like hiding changes*. The mechanical rule: a resolution should be a pure function of (base, ours, theirs) for the conflicted region; any other change in that commit belongs in a separate commit ("You should refrain from abusing `--no-commit` to sneak substantial changes into a merge commit" — §1.7 — is the same rule from the git side).
6. **Understand that a clean `--cc` does not mean the conflict was trivial.** One-direction resolutions are *invisible* in `git show` (§4.1 + §12.13). So "no diff in the merge commit" cannot be used as evidence that nothing was decided — only that everything was decided toward one side. If the skill claims "verify the resolution by looking at the merge commit", it must also claim "and take the ours/theirs choice from the conflict record, not from the diff".
7. **Expect lost work in revert-then-remerge flows; it is not a bug.** "If you re-merge Foo, nothing at all happens! You're already merged" (§4.2) plus the `git-merge(1)` reverted-change paragraph (§1.5) and `git-revert(1)` §`-m`. Doctrine: after reverting a merge, recovery of that content requires a *new* commit or a re-application that changes history shape — not a re-merge.
8. **Stage counts are conflict-class dependent.** Assume 1/2/3 exist and you will break on `AA` (no base) and `UD`/`DU` (no other side) (§2.2). The skill's conflict taxonomy should be the 7-row `git-status(1)` table (`DD, AU, UD, UA, DU, AA, UU`), not "UU" alone, and should remember that `U` in status means "updated but **unmerged**", including for rebase/cherry-pick stops.
9. **Prefer three-way reading of a conflict: base first.** The default `merge` conflict style hides what the ancestor said — "You cannot tell how many lines are deleted and replaced" (§3.1). `diff3`/`zdiff3` (or `git show :1:<path>`) restores it. For agents: set/require the base region for any nontrivial resolution, and do not claim diff3-vs-zdiff3 noise reduction from memory (I could not reproduce the difference, §3.2).
10. **Multi-base and criss-cross history means the merge base is not a single commit.** `ort` "creates a merged tree of the common ancestors"; `git merge-base` without `--all` gives you an **unspecified** one of several best bases (§1.2, §5.4). Doctrine: for criss-cross trees, compute `--all` before reasoning about "what the base was", and for n heads use `--octopus` semantics (a different ancestor set than pairwise bases) — plus `--is-ancestor` (0/1, errors are non-1) instead of the legacy `merge-base ==` idiom.
11. **Merge is head-vs-head, so test merges leave no semantic trace.** Rebase "actually goes one commit at a time" (§4.2); merge doesn't. That's why rerere (marker-text keyed), patch-id/cherry-mark, and `git log --cherry-mark` exist as separate mechanisms. Doctrine: never reason "which commits were merged" from a merge result; reason from the graph and the trees.
12. **Rerere changes the working tree but not the index by default.** The default reuse message is `Resolved … using previous resolution.` with the path still `UU`; only `--rerere-autoupdate`/`rerere.autoupdate=true` prints `Staged …` and clears the unmerged stages (§8). An agent that sees a clean file and commits will fail on unmerged entries; the doc even says autoupdate exists so you can "double-check what rerere did and catch potential mismerges". Also: rerere reuse is keyed to the *exact conflicted text*, so "rerere failed to help" is normal, not a bug; and rerere "relies on the conflict markers", so files containing marker-like lines silently break recording (§8 NOTE, `conflict-marker-size`).
13. **You cannot stash out of a conflicted merge; and you should not merge with a dirty tree in the first place.** Verified refusal (§10); doc-side warning that `--abort` "will in some cases be unable to reconstruct" pre-merge changes (§1.7). Doctrine: commit-or-stash before starting; if already conflicted, `--abort` (throw away) or `--quit` (keep work, forget merge state) — never `stash`.
14. **`--abort` is not a time machine; `--quit` is not an abort.** Different contracts, both documented, and the autostash interaction makes them non-interchangeable (§1.7). Skill should state: `--abort` = reconstruct pre-merge state (may lose uncommitted edits); `--quit` = leave index/worktree exactly as-is and forget the merge, after which you finish with a plain `git commit` (parents from `MERGE_HEAD` are gone — so commit *before* `--quit` or accept a non-merge commit).
15. **Fast-forward is not a merge and cannot be intercepted by `--no-commit`.** To guarantee nothing moves, use `--no-ff`/`--ff-only` or `merge.ff=only`; annotated tags silently force `--no-ff` and produce a merge commit you may not want (`git merge v1.2.3^0` to unwrap) (§1.6). Rebase's ORIG_HEAD caveat (§5.1) means `ORIG_HEAD` is not a reliable undo anchor mid-rebase — the reflog `@{1}` is.
16. **Exit codes are not contractual for merge.** `git-merge(1)` documents no EXIT STATUS in 2.46.2 (§1.8): only "Already up to date.", "Automatic merge failed; …", "Merge with strategy octopus failed." and the `--ff-only` "non-zero status" wording are specified. Skill rules must key on **state** (`MERGE_HEAD`/`rebase-merge/`/`CHERRY_PICK_HEAD` existence, `git ls-files -u`, `git status --porcelain`) rather than on `$?`, and on `git-merge-base --is-ancestor` where a numeric contract *is* documented.
17. **Octopus is a "bundle only" tool, and it aborts without leaving merge state.** It "refuses to do a complex merge that needs manual resolution" (§1.2) and locally left nothing in `.git` to resume from (§12.11): the only recovery is to re-run as pairwise merges. Doctrine: never offer octopus for anything a human might have to resolve.
18. **Unrelated histories is a deliberate safety, not a nuisance flag to pass.** "no configuration variable to enable this by default exists and will not be added" (§1.7). Two independent projects fused = every overlapping path is add/add with **no base**, i.e. the hardest conflict class (§2.2), and the resulting merge permanently welds two ancestries so later reverts behave per §1.5/§4.2. Skill should require explicit user confirmation, then recommend `merge -s ours` bookkeeping or a subtree/submodule arrangement over a raw content fusion.
19. **Rename detection is a similarity heuristic that merges depend on, and its failure is silent.** `merge.renameLimit` currently defaults to 7000 with an "exhaustive portion" caveat; `ort` handles renames but not copies; `resolve` ignores renames; `merge.directoryRenames` defaults to `conflict` (§1.2, §2.5). Linus: "We do actually depend on the similarity analysis being 'good' — because it matters a lot for things like merging" (§4.3). Doctrine: after any merge involving renames, verify with `git diff --find-renames -M <base> <result>` and check for orphaned old-path files (the `directoryRenames=false` "left behind in the old directory" outcome). Treat "rename not detected" as a *correctness* event, not a cosmetic one.
20. **Line-ending and filter changes convert clean merges into conflicts.** `-X renormalize` / `merge.renormalize` exists exactly because "merging anything where the attribute is not in place would normally cause merge conflicts", and only works when smudge→clean is idempotent (§6.5). For files with `working-tree-encoding`, non-UTF-8 content is treated as binary → **unmergeable** (§6.5). Doctrine: spurious whole-file conflicts on Windows checkouts are a config diagnosis (autocrlf/text/eol/renormalize) before they are a resolution task.
21. **Prefer a dry run over a live merge when the outcome is uncertain.** The docs give an inspection path that needs no merge at all: `git show :1/:2/:3` + `git log --merge -p` + `git diff AUTO_MERGE` (§11). `git merge-tree` (page shipped, 329 lines, `--write-tree` mode) is the plumbing dry-run; not exercised in this session, so treat exact `merge-tree` output as doc-only.
22. **Do not resolve conflicts to spare someone else the conflict.** Kernel maintainer doctrine, quotable and unambiguous: "Linus is adamant that he would much rather see merge conflicts than unnecessary back merges. Seeing the conflicts lets him know where potential problem areas are"; and for hard conflicts "create and push a *separate* branch to show how you would resolve things" (§5.2). This is the correct rule for an agent asked to "just fix the merge".
23. **Once you have merged someone's history, that branch is no longer yours to rewrite.** "once you have merged somebody else's history into your tree, you cannot rebase that branch" (§5.2); "Rebasing … a branch that others have based work on is a bad idea: anyone downstream of it is forced to manually fix their history" (`git-rebase(1)`).
24. **Merge messages are an audit artifact.** `--no-edit` "is generally discouraged" (§1.7); the changelog "should say *why* the merge is being done" (§5.2); `--log`/`merge.log` and `--signoff`/DTCO are documented levers. Doctrine: an agent's merge commit message states intent + conflict inventory, not just "Merge branch 'x'".

---

## 14. UNVERIFIED / not-fetched / blocked items

**Fetch failures (live web):**
- `https://git-scm.com/docs/git-merge/2.46.2` → HTTP 503; no `git-scm.com` HTML page was retrievable this session. Mitigation: every quoted man-page line comes from the **shipped, version-exact** HTML (`D:\Program Files\Git\mingw64\share/doc/git-doc/*.html`, footer `Last updated 2024-09-24 12:05:03 UTC`) and the top-priority page (`git-merge`) was additionally confirmed against the git.git **v2.46.2 tag** source text, section-for-section.
- `Documentation/technical/ort.txt` → 404 at both `master` and `v2.46.2` raw paths. The `ort` specifics quoted above therefore come only from `git-merge(1)` §MERGE STRATEGIES + `git-config(1)` §`merge.*`; the technical doc's deeper claims (dir-rename modes `DIR_*`, "most correct implementation" statement) are **NOT cited here and remain UNVERIFIED**.
- `lore.kernel.org/.../raw` endpoints → 404/403 through the fetch proxy; message HTML pages were used instead, which carry the full body.
- `git mergetool --help` / `git difftool --help` produced no output in this environment → the tool-CLI behaviour is documented-quoted only, not observed.

**The brief's item 3 — a 2007 Linus email saying "be very, very careful in merges": NOT LOCATED.** Sweep performed on `lore.kernel.org/all/` (public-inbox/Xapian), each with the field prefixes its help page documents (`s:` subject, `b:` body, `nq:` non-quoted body, `f:` from, `d:` date range):
`"be very careful" "merge" f:torvalds@` · `"very very careful" merge` · `"very very careful" f:torvalds@` (+relevance) · `"very careful" "merges" f:torvalds@` · `"careful" "merges" f:torvalds@` (40 hits) · `f:torvalds@ nq:"very careful" nq:merge d:20070101..20071231` · `f:torvalds@ merge careful d:20070101..20071231` (84 hits, relevance-ordered) · `f:torvalds@ "carefully" "merges" d:2007…` (1 hit) · `b:"careful about resolving any conflicts"` · `"careful when you do merges"` · `"what the merge base was"` · `"very very careful in merges"` · `"in merges" "very careful" f:torvalds@` · `"evil merge" f:torvalds@` (14 hits → produced §4.1) · plus web searches.
All 2007 Linus candidates were read in full: the only literal "be very very careful" is about **history rewriting** (§4.6). The **substantive 2007 merge-resolution doctrine** is §4.1 ("evil merge", in-place resolutions, `--cc` auditability) — I recommend the skill cite that email as the doctrine anchor, correctly dated **7 Feb 2007**, Message-ID `Pine.LNX.4.64.0702071222470.8424@woody.linux-foundation.org`, and *not* assert the "very, very careful in merges" wording as a quotation.

**Doc-vs-behavior gaps found (worth stating in the skill as such):**
1. `git-merge(1)` has **no EXIT STATUS section** in 2.46.2 — every merge exit code in §1.8 is empirical, not contractual.
2. The brief's `git diff --conflict=…` **does not exist**; `--conflict=<style>` is a `git-checkout(1)` option (values `merge|diff3|zdiff3`). `git-merge(1)`/`git-config(1)` expose the style only as `merge.conflictStyle`.
3. `git-merge(1)` lists `[--no-]rerere-autoupdate` in SYNOPSIS and describes it in OPTIONS, but **never states which is the default**; measured default = resolution written to the work tree while the index stays unmerged (consistent with `git-rerere(1)`'s "leaves the index file alone").
4. `merge.conflictStyle`'s documented zdiff3 edge-trimming was **not reproducible** in two constructions (§3.2) — claim it only as documented.
5. `git-merge(1)` §HOW CONFLICTS ARE PRESENTED and §CONFIGURATION disagree in framing about region size: §HOW says diff3-style lets you "come up with a better resolution by viewing the original", §CONFIG says the plain `merge` style "tends to produce smaller conflict regions than diff3". Both quoted; not a contradiction but the skill should not claim diff3 is strictly larger *and* strictly better without noting the trade-off is the doc's own.
6. `git-tools(1)` in this build is a stub (18 lines) — not citable.

**Not exercised locally (doc-only claims in this report, flagged where used):** `MERGE_MODE` contents for non-content conflict classes (e.g. `DU`, `DD`, symlink/typechanges); `-X ignore-*` whitespace cascade rules; `merge.verbosity` levels; `subtree` strategy; `--verify-signatures`; `--gpg-sign`; hooks (`pre-merge-commit`) firing; `merge-tree` output; `difftool` behaviour; the criss-cross multi-base `merge-base --all` output (my construction was corrupted by a leftover merge); `AUTO_MERGE` semantics beyond its existence and revability; `.git/sequencer` file layout; `--independent`; `%S/%X/%Y/%L` custom-driver placeholders end-to-end; `conflict-marker-size`; `working-tree-encoding` round-trip; `git patch-id`/`git cherry`.

**Interpretation risk flagged:** the `union`-driver exit code was captured through a pipe in the run that produced §6.2 output, so exit 0 there is inferred from the success message rather than measured. The file content (duplicated `l3`, both sides' lines retained) is directly observed and is the point.
