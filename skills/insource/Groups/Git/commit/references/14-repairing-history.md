# Repairing history — and the backup rule that makes repair safe

Mistakes are normal; the recovery is a decision tree. The one rule that outranks all of them: **before any
command that rewrites history, create a backup ref, and delete it only after the result is verified good.**

## The backup rule (mandatory)

Dangerous operations: `rebase -i` (squash/drop/edit), `commit --amend` on anything but the last local commit,
`reset` (any mode beyond `--soft` on unstaged work), `filter-branch`/`filter-repo`, `gc --prune`,
`push --force` / `--force-with-lease`, and any merge-conflict resolution you are unsure of.

```bash
git branch backup/pre-rebase-<short-name>        # 1. a named ref at the current tip
git rev-parse --short backup/pre-rebase-<short-name>   # 2. print it, so it is in the transcript
# ... do the rewrite ...
git log --oneline origin/main..HEAD              # 3. verify: same net change, cleaner shape
git diff backup/pre-rebase-<short-name> HEAD     # 4. MUST be empty — the tree did not change, only history
git push --force-with-lease                      # 5. only after 3 and 4 are right
git branch -D backup/pre-rebase-<short-name>     # 6. delete once verified good
```

Why each step exists:

- **A branch, not a memory.** Reflog entries expire (`gc.reflogExpire`, default 90 days) and `git gc` prunes
  unreachable objects; a named branch is a real ref that keeps the commits alive and is legible to anyone who
  opens the repo later.
- **Print the SHA.** If the rewrite goes wrong in a shared worktree, the recovery instruction must not depend
  on scrolling back through your own output.
- **`git diff backup HEAD` must be empty.** That is the whole claim of a history rewrite: same content,
  different story. If the diff is non-empty, you did not clean history — you changed the code, and it needs its
  own commit and its own review.
- **Delete it after, not before.** A leftover `backup/*` branch is cheap clutter; a deleted one after a bad
  rewrite is unrecoverable work. If the rewrite touched a shared branch, keep the backup until collaborators
  have re-based.

Recovery, when the rewrite went wrong:

```bash
git reset --hard backup/pre-rebase-<short-name>   # undo the rewrite entirely
```

Say plainly what you restored and why; do not present a rollback as if the history had always been this way.

## The feature you just committed is broken (p.54–56)

| State | Move |
|---|---|
| Committed **and pushed** | honest follow-up commit: `fix: correct output generation in report export`. History reads `feat:` then `fix:`, which is *fine* — it is what happened |
| Committed, **local only** | fix it → `git add <files>` → `git commit --amend` folds it into the original `feat:`. Never amend what is pushed or shared |
| Hopeless for now | `git stash push -m "broken-report-feature"`, work elsewhere, `git stash pop` later |
| Half-done but harmless | a valid commit: `feat: scaffold report export logic (not active yet)` — the app works and the code is inert or flag-gated |

Forbidden (p.56): force-pushing broken work to `main`; hiding a fix inside a `feat:` label; mixing the fix and
the feature into one commit because it is "the same task".

## You committed a wrong fix, then built a feature on top (p.69–71)

| State | Move |
|---|---|
| Not pushed | backup ref → `git rebase -i HEAD~2` → mark the fix `edit` → correct the code → `git add <file>` → `git commit --amend` → `git rebase --continue`. History now reads as if you got it right first time — which is honest *about the code* and should not be stretched past that |
| Pushed, branch nobody else uses | fix forward locally, then `git push --force-with-lease`. Never on `main`, `dev`, or anything others depend on |
| Pushed, shared | a new honest commit: `fix: finalize fix in _generate_graph (missed edge case)`. It preserves the timeline and is safe for a team |

`--force-with-lease` rather than `--force` always: it refuses the push if someone else advanced the branch
while you were rewriting.

## Three "fix attempts" that fixed nothing (p.74–76)

Bad history: `fix: fix assets` → `fix: fix assets again` → `fix: really fix assets this time`. It records
progress that did not happen.

- **Not pushed:** backup ref → `git rebase -i HEAD~3` → `drop` the dead ends or squash them into the one
  meaningful fix.
- **Pushed, not merged:** `git rebase -i main` and collapse them before the PR.
- **Pushed and shared:** you cannot safely erase them. Reword honestly as exploratory instead:
  `chore(assets): explore asset path issue`, `wip(assets): diagnose loader path`.
- **The good version of the same story** (p.76): `wip(assets): attempt to handle path inconsistencies` →
  `chore(assets): debug mode added for path tracing` → `fix(assets): resolved root-relative path issue`. Each
  step says what was learned.

Rule: **history should reflect meaningful, net-positive changes** (p.76).

## Two commits fixing the same function — duplicates? (p.72–74)

- The second is literally forgotten code from the first → amend or squash into one unit **before merge**.
- The second is a distinct attempt or extension → keep it, with its own descriptive message:
  `fix(_generate_graph): correctly handle disconnected nodes`,
  `fix(_generate_graph): prevent infinite loop when graph is cyclic`.
- The anti-pattern is two commits titled the same thing: "which is the real fix?"
- Principle (p.73): **don't worry about duplicate fixes; avoid duplicate messages.**

## Fixing Bug A caused Bug B (p.83–85)

- **Default: two `fix:` commits.** `fix(component): correct X behavior in overlay (Bug A)` then
  `fix(component): resolve regression in scroll context (Bug B)`. B is a *consequence fix*: trackable,
  selectively revertable, and honest about the sequence.
- **One commit** only if B is trivial, untestable without A, or too tightly coupled —
  `fix(overlay): fix position and handle scroll container regression` — and explain both bugs in the body.
- **Never** bundle two *unrelated* bugs in one commit.

## Reverting, in order of safety

```bash
git revert <sha>                  # the default: a new commit that undoes one, safe on shared branches
git revert -m 1 <merge-sha>       # undo a merge, keeping the first parent
git reset --hard backup/...       # undo YOUR OWN rewrite, with the backup ref in place
git push --force-with-lease       # last resort, unshared branches only, after the backup exists
```

A `revert` of a merge is not free: re-merging the same branch later will not re-apply the reverted commits
without a revert-of-the-revert. Say that out loud before doing it on a release branch.
