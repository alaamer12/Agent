# Case 9 — rewriting history with a net under it

**Situation:** an asset-path bug took three attempts. The branch history reads:

```text
abc1234 fix: fix assets
def5678 fix: fix assets again
9ab3cde fix: really fix assets this time
```

Two of those three commits changed nothing that worked. The PR is open, the branch is yours alone, and the
reviewer has not looked yet. This is the moment for a rewrite — and the moment people lose an afternoon.

## Step 0 — the backup ref, before anything else

```bash
git branch backup/pre-rebase-assets
git rev-parse --short backup/pre-rebase-assets        # 4f2a1c9  <- printed, so it is in the transcript
```

Why a branch and not the reflog: reflog entries expire (`gc.reflogExpire`, ~90 days) and `git gc` prunes
unreachable objects. A named ref keeps those commits alive and findable by anyone, not just by this session.

## Step 1 — classify before touching anything

```bash
git log --oneline origin/main..HEAD
git show --stat abc1234
git show --stat def5678
git show --stat 9ab3cde
```

Not every "attempt" is noise. Ask of each: **does this commit contain a change that is still in the final
code?**

- `abc1234` added a debug flag that is still there → it is a `chore(assets): add path tracing debug mode`, not
  a failed attempt.
- `def5678` changed a resolver and then `9ab3cde` reverted that change internally → genuinely dead.
- `9ab3cde` is the actual fix.

## Step 2 — rewrite with intent, not with a squash-everything reflex

```bash
git rebase -i HEAD~3
```

```text
pick   abc1234  fix: fix assets            -> reword to: chore(assets): add path tracing debug mode
drop   def5678  fix: fix assets again
pick   9ab3cde  fix: really fix assets...  -> reword to: fix(assets): resolve root-relative path issue
```

The result is the *good version of the same story* — three commits that each say what was learned:

```text
chore(assets): add path tracing debug mode
fix(assets): resolve root-relative path issue
```

…or, if the debug mode was only ever scaffolding, drop it too and leave one honest commit.

## Step 3 — prove the rewrite was content-neutral

```bash
git diff backup/pre-rebase-assets HEAD      # MUST print nothing
git log --oneline origin/main..HEAD
```

An empty diff is the entire claim: same tree, better story. **If it is not empty, the rewrite changed code** —
either restore the backup and redo it, or keep the difference and give it its own commit with its own review.
Silently absorbing a code change into a cleanup is how "I only tidied the history" ships a regression.

## Step 4 — publish, only because the branch is yours

```bash
git push --force-with-lease
```

`--force-with-lease` refuses if the remote moved while you were rewriting — the only acceptable variant. Plain
`--force` overwrites someone else's work without noticing. If the branch were shared, or had been reviewed
already, this step does not exist: the answer would have been a new honest commit instead.

## Step 5 — delete the net, after everything is verified

```bash
git branch -D backup/pre-rebase-assets
```

Keep it longer if collaborators are mid-review on the old hashes; the cost of a stray `backup/*` branch is
clutter, and the cost of deleting it too early is unrecoverable work.

## If the rewrite went wrong

```bash
git reset --hard backup/pre-rebase-assets    # back to exactly where you started
```

Say out loud that you restored it, and why. Do not present a rollback as if the history had always been this
way.

## The pushed-and-shared variant, for contrast

Same three commits, already merged or already reviewed by others: you cannot safely erase them. Reword toward
honesty where you can, and add the real fix forward:

```text
chore(assets): explore asset path issue      (reworded from "fix: fix assets")
wip(assets): diagnose loader path            (reworded from "fix: fix assets again")
fix(assets): resolve root-relative path issue
```

Rewriting shared history is forbidden by rule 9, not by taste: other people built on those hashes, and a force
push turns their local state into a conflict.

## Report line

```text
BEFORE : 3 commits, two of them recording no progress
AFTER  : 2 commits - chore(assets) debug mode, fix(assets) root-relative path
PROOF  : git diff backup/pre-rebase-assets HEAD -> empty (content unchanged)
PUSHED : --force-with-lease (branch authored by me, unreviewed)
BACKUP : deleted after verification
```

That last line is the one a future reader of this transcript needs: the net existed, the jump was checked, and
the net was taken away only after landing.
