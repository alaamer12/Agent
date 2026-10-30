# Case 8 — a fix appears mid-feature, and the policy forbids `fix:` here

**Situation:** three days into `feat/report-generation`. `load_data()` is broken — it mis-parses empty rows —
and the feature cannot be tested until it works. Team policy: `fix:` commits land only on `fix/*` branches,
because hotfixes deploy straight from them.

The wrong moves, both of them tempting: fold the fix into the feature commit ("it's related"), or leave the fix
uncommitted while continuing to build on broken code.

## The base case: separate concerns even while interrupting

```bash
# load_data() fixed in the working tree
git add -p src/io/load_data.py     # select ONLY the parsing hunk
git commit -m "fix(data): correct load_data() handling of empty rows"
git checkout -b fix/load-data-empty-rows   # or route it properly, next section
```

The fix is now a commit object that exists, is testable, and can be cherry-picked. It is not yet in the wrong
place, because the branch was created from where it belongs.

## Routing it properly when the policy is enforced

```bash
git stash push -m "feat: report generation WIP"   # park the feature, named
git checkout main && git pull
git checkout -b fix/load-data-empty-rows
git stash pop                                     # only the fix is relevant; discard the rest if mixed
git add -p src/io/load_data.py                    # take ONLY the fix hunk again
git commit -m "fix(data): correct load_data() handling of empty rows"
git push origin fix/load-data-empty-rows          # open the PR

git checkout feat/report-generation
git stash pop 2>/dev/null || true                 # resume the feature
git cherry-pick <fix-sha>                         # so the feature branch is testable now
```

`cherry-pick` is the honest shortcut: the feature gets the fix immediately, and the `fix/*` PR still merges on
its own track. Duplicate commit messages across branches are fine; duplicate *subjects* are what confuse a
reader later.

## When you cannot switch branches at all

Some environments make a checkout expensive or impossible — a long build, a locked working tree, another agent
sharing the directory. Then, in order of preference:

**1. Local `wip/` branch** — a real commit, invisible to the remote:

```bash
git checkout -b wip/fix-load-empty-rows
git add -p && git commit -m "fix(data): handle empty rows (parked; extract to fix/*)"
git checkout feat/report-generation
```

**2. Named stash** — the fix exists as a restorable object without any commit:

```bash
git add -p
git stash push -m "fix: load_data empty rows"
git reset
# later: git stash list && git stash apply stash@{0}
```

**3. Warning-label commit** — when the fix must go onto this branch now:

```bash
git commit -m "wip-fix(data): temp empty-row fix - extract to fix/* before merge"
git log --grep=wip-fix          # find every parked one during cleanup
```

Then, when policy allows: cherry-pick it to a real `fix/*` branch, `revert` it here or rebase it out, and
reword the copy to `fix(data): …`.

**4. Patch file** — only if none of the above works. Untracked, invisible in history, conflict-prone on
re-apply; if a project genuinely keeps them, they belong in a tracked folder with a README, applied with
`git apply`.

## Keep working on the fixed code

Do not roll the fix back to preserve branch purity, and do not build the report logic on top of a parser you
know is wrong. This is a surgical pre-commit: the critical independent part goes in now, the paperwork comes
later. The door must work now, even if the report is filed later.

## Cleanup before the PR

```bash
git branch backup/pre-rebase-report        # before any rebase, always
git rebase -i origin/main                  # drop the wip-fix from the feature branch
git diff backup/pre-rebase-report HEAD     # must be empty for the parts that were pure history
git push --force-with-lease                # branch is yours alone; verified above
git branch -D backup/pre-rebase-report
```

## Report line

```text
COMMITTED : fix(data): correct load_data() handling of empty rows   (on fix/load-data-empty-rows)
            feat(report): generate weekly summary section           (on feat/report-generation)
CHERRY-PICKED: <fix-sha> onto the feature branch so it is testable today
PARKED   : none - the fix is a real commit on the right branch
NOT STAGED: scratch/debug-parse.py, .env.local
```

The line that matters most to a reviewer: the fix and the feature are two commits on two branches, and the
feature branch was made testable by a cherry-pick rather than by mixing them.
