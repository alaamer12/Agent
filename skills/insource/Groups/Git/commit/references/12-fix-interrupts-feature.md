# A fix interrupts your feature

Mid-feature on `feat/report-generation` you discover `load_data()` is broken. The principle is
**"separate concerns, even if interrupting"** (p.25–26) — and the hard part is doing that when the branch
policy says the fix does not belong here.

## The base case (p.25–26)

```bash
# fix load_data() in the working tree
git add -p                     # select ONLY the fix hunk
git commit -m "fix(data): correct load_data() parsing logic"
# back to the feature; commit it later as its own unit
git commit -m "feat(report): generate weekly summary section"
```

Why bother: one-thing-per-commit history, easier debugging, and a teammate can cherry-pick the fix without
inheriting your half-finished feature.

Mindset, quoted because it is the actual discipline: **leave campsites cleaner** — fixing as you go *is* the
job (p.26).

## Team policy: `fix:` commits only on `fix/*` branches (p.27–30)

You still cannot put the fix on the feature branch. Route it through a temporary branch:

```bash
git checkout main && git pull
git checkout -b fix/load-data-bug
# apply the fix
git add -p && git commit -m "fix(data): handle empty rows in load_data()"
git push origin fix/load-data-bug          # + PR

git checkout feat/report-generation
git pull origin main                       # after the merge, or immediately:
git cherry-pick <fix-commit-sha>
```

**Already committed the fix on the wrong branch?** (p.29)

```bash
git log                                    # find the SHA
git checkout -b fix/extract-bugfix main
git cherry-pick <sha>
git push origin fix/extract-bugfix         # + PR
git checkout feat/report-generation
git revert <sha>                           # remove it from the feature branch
# after the fix merges: rebase/merge fix/* into feat/*
```

Why teams enforce this (p.29): hotfixes deploy straight from `fix/*`, and history stays clean for blame and
changelogs. It can be enforced automatically (p.30): a pre-commit or CI check comparing branch name to message
prefix — `if branch != fix/* && msg == fix:* → reject`.

## The hardest case: needed now, and you cannot switch branches (p.34–43)

Four options, cleanest first:

1. **Local `wip/` branch** (p.42) — a real commit object, invisible to the remote:
   ```bash
   git checkout -b wip/fix-load-bug
   git add -p && git commit -m "fix: temporary fix to unblock report generation"
   git checkout feat/report-generation
   # later, when allowed: cherry-pick it into the proper fix/* branch
   ```
2. **Named stash** (p.42) — `git add -p` then:
   ```bash
   git stash push -m "fix: load_data issue"
   git reset
   # later: git stash list && git stash apply stash@{0}
   ```
   "Safer than a patch file. Traceable, restorable, versioned." Named, never anonymous.
3. **Warning-label commit** (p.43) — when you must commit in place:
   ```bash
   git commit -m "wip-fix: load_data() temp fix - extract to fix/* later"
   git log --grep=wip-fix                   # find it again (p.37)
   ```
   Then reword or cherry-pick during cleanup ([`13`](13-wip-checkpoints-and-squash.md)).
4. **Patch file** — last resort, and see the caveats in [`10`](10-hunks-and-splitting.md).

## Commit now, reorganize later (p.38–40)

Two rules that look like compromises and are not:

- **Keep working on the fixed code.** Do not shelve the fix and continue building on a broken foundation, and
  do not roll back a correct fix for branch-purity's sake. Think of it as a *surgical pre-commit*: the critical
  independent part goes in now; the paperwork comes later (p.39).
- The construction analogy (p.40): you are building a room (`feat:`) and the door (`load_data()`) is broken —
  **"the door must work now, even if the report is filed later."**

History-repair tools for the later part (p.40): interactive rebase to reorder or squash, `cherry-pick` to move
the fix to its rightful branch, `reword` to turn `wip:` into `fix:` once it has landed where policy wants it.
All of them are local-only operations unless you take the safety step in [`14`](14-repairing-history.md).

## What not to do

- Do not bundle the fix into the feature commit "because it is related". It is *adjacent*, not related.
- Do not leave the fix uncommitted while you continue — one crash and the diagnosis is gone.
- Do not force-push a shared branch to make the history look policy-compliant.
- Do not name the commit `fix:` when it is exploratory; label it honestly (`wip-fix:`, `debug:`) so the cleanup
  pass knows what it is looking at.
