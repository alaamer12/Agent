# Operations: choosing and undoing merge / rebase / cherry-pick

Same machinery underneath (cherry-pick and rebase are "merge with one
parent dropped"), opposite history policies. This file owns the choice and
the undo.

## The golden rule (and what "public" means)

**Never rewrite history others have built on.** The line is *public*, not
*pushed*: a branch colleagues/pipelines/CI have fetched or based work on is
public even if it lives on your own server. Locally-unpublished work is
yours to reshape freely. Everything below is downstream of this rule.

## Choosing the integration operation

| Goal | Operation | What you pay |
|---|---|---|
| Keep every commit, prove integration happened | `git merge --no-ff <feat>` | non-linear history; merge commits need auditing (§evil) |
| Linear story for a feature branch, before anyone else builds on it | `git rebase <main>` then FF-merge | traceability of *how* it was integrated; rebasing across merges drops resolutions (S15) |
| Take the change, lose the branch's shape | platform squash-merge | the "same conflict twice" loop when the branch lives on: squash discarded the resolution history, so re-integration re-conflicts from scratch |
| One specific commit to a release/maintenance branch | `git cherry-pick -x <sha>` | duplicated history (new SHA); must manage dedup (§patch-id) |
| Integrate a foreign project's code deliberately | subtree merge | complexity; usually prefer vendoring policies |
| Merge as policy at scale (monorepo, release trains) | merge queue + per-file `.gitattributes` ownership | CI capacity — the queue exists because per-PR testing cannot prove the merged state |

Merge early and often: conflict size is a function of elapsed divergence,
not of the number of commits. "Merge master into my branch forever" is the
counter-loop: the sync merges accumulate and the feature merge stays
postponed — sync *and* integrate deliberately.

## Fast-forward semantics

`git merge` on a behind branch fast-forwards — no merge commit, no
integration *record*. That is why teams force `--no-ff` for features: the
merge commit is the history-policy decision (preserve branch topology as
evidence of what was reviewed together). Squash-vs-merge-vs-rebase is a
**project policy** — detect the repo's incumbent convention from
`git log --graph` before picking, ask if none.

## Cherry-pick: a partial merge that duplicates history

- Not a merge: no ancestry link, new SHA, and it re-runs the 3-way merge
  against a *different* base — expect the same conflicts, resolve them the
  same way (R0–R9 of `conflict-method.md`).
- `-x <sha>` records provenance ("cherry picked from commit …") — mandatory
  unless there is a reason not to leave the trail.
- A cherry-picked/reverted *merge commit* needs `-m 1` (mainline parent) or
  git refuses.
- `git cherry-pick` has **no `-q`** flag on tested 2.46.2 (nor does revert) —
  scripts that "work on Linux" sometimes break here only because a wrapper
  differed.
- Direction rules: cherry-pick **forward** (hotfix branch → main) is normal
  and correct; cherry-picking release fixes onto the long-lived feature and
  then merging can double-apply — prefer merging down, cherry-picking up.

## Patch-id: how git knows "that change already exists over there"

`git cherry <upstream> <head>` lists commits of `<head>` as `+` (not
upstream) or `-` (equivalent patch already present). Dedup by **patch-id**,
not ancestry — it is what saves you after pulling a rebased upstream
(`git rebase <upstream>` silently drops your already-applied commits) and
what makes "merge-then-rebase" mostly idempotent. Verified: lab S27 (a
cherry-picked commit is marked `-`, its sibling still `+`). Limits: it
compares *diffs*, so a context-shifted or partially-resolved change counts
as different.

## Fork-point protection

`git rebase` without args uses the reflog-derived fork-point
(`git reflog <branch>`) and can *drop* commits it thinks upstream took over
— usually right, wrong when upstream rewrote and your commits were
"recognized" incorrectly. If commits "disappeared" after a rebase:
they are in the reflog; recover with `git rebase --onto <newupstream>
<fork-point> <branch>` or `git format-patch` the missing range and apply.
`--force-rebase` skips the drop-the-merge / dedup niceties.

## Reverting merges and the re-merge trap

- Revert a *merge commit* with `git revert -m 1 <merge>` (mainline = the
  branch you were on). Without `-m`, git refuses.
- **The trap (verified S16):** after reverting a merge, re-merging the fixed
  branch is a silent NO-OP — the branch's commits are ancestors of HEAD, so
  the merge finds "already up to date", and the reverted content stays
  reverted. The merge machinery dedups by ancestry, not by current content.
- The fixes, per git's own howto (`revert-a-faulty-merge`): if the branch
  continued on top of the original tip, `git revert <the-revert-commit>`;
  if you rebuilt the branch from scratch, merge it as-is (or recreate the
  branch with `git rebase --no-ff <fork-point>` so its commits are new).
- A change reverted **on one side only** can silently reappear after the
  merge (the 3-way model limitation: the other side didn't touch the lines,
  so the "reverted" version is the unchanged one). Detection + doctrine:
  `silent-destruction.md` §silent-resurrection.

## Force-push

Minimum bar: `git push --force-with-lease` — it refuses if the remote moved
since your last fetch (peer pushed while you rewrote). Plain `--force`
clobbers their work; it is never the default in shared repos. Prefer
`--force-with-lease` over `--force-if-includes` combinations only after
understanding that the lease compares to your *remote-tracking* ref, so
`fetch` without inspecting refreshes your own permission slip — fetch,
verify, then push. Verified: lab S28 (lease rejects; note: on Windows,
bare-init remotes default to `master` — give `git init --bare -b main`).

## Pre-flight: know before you touch anything

`git merge-tree --write-tree <branchA> <branchB>` runs the real merge
machinery against objects only — **no worktree, no index, no HEAD**. Exit
0 = would merge clean (stdout: the resulting tree oid, one line); exit 1 =
would conflict (tree oid, then conflicted-path info; `--name-only` for just
the paths). Agents and CI should pre-flight before starting any
integration, and can enumerate the exact conflict set beforehand (lab S38,
2.46.2). `branch`'s worktree-collision doctrine applies: two agents cannot
merge in one worktree simultaneously — but merge-tree has no such limit,
so use it for anything speculative.

## Recovery playbook (the table)

| Situation | Move |
|---|---|
| Conflict going badly, merge in progress | `git merge --abort` |
| Hard restart, nothing uncommitted | `git reset --hard HEAD` (uncommitted work lost) |
| Rebase stopped, abandon | `git rebase --abort` (HEAD back to original branch) |
| Cherry-pick sequence wrong | `git cherry-pick --abort` / `--quit` (quit = forget, keep state) |
| Bad merge, local only | `git reset --hard HEAD~` (rewriting — fine only while unpublished) |
| Bad merge, pushed/public | `git revert -m 1 HEAD` |
| Re-merge must NOT resurrect it | revert the revert (or rebuild branch) — see trap above |
| Redo one conflicted file | stages: `git show :1/:2/:3:f` → `git merge-file` → re-`add` |
| Lost a completed rebase's old tip | branch reflog (`@{1}`), `git reset HEAD@{2}` — git keeps it locally |
| Markers gone but conflict unresolved | `git checkout -m <file>` / `--conflict=diff3 <file>` |
| Local changes block checkout | `git checkout -m <branch>` (autostash-and-reapply; conflicts land in the stash list) |
| Pulled a rewritten upstream | `git rebase <upstream>` (patch-id dedup) — hard case: `--onto` from fork-point |
| About to overwrite remote work | `--force-with-lease`, never bare `--force` |
| Half-resolved work destroyed by `reset --hard` | `git fsck --lost-found` — the resolution you had `git add`-ed survives as a dangling blob in `.git/lost-found/other/`; grep it for distinctive text (write such markers while resolving if the merge is precious — lab S43) |

Reflog caveat: it is **local, temporary, unshared** — the safety net only
exists on the machine that made the mistake, and `gc` eventually prunes it.

## Where the operation's state lives (for scripts/agents)

`MERGE_HEAD` (merge in progress), rebase dir under
`.git/rebase-merge/` or `.git/rebase-apply/` (interactive/apply in
progress), `CHERRY_PICK_HEAD`, `REVERT_HEAD`, `BISECT_LOG`. `git stash`
inside a conflicted merge **fails** (exit 1 on tested 2.46.2 — "could not
write index"): resolve or abort first; the only documented stash-during-merge
use is `git checkout -m` autostash semantics.
