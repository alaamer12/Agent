# Strategies, and what each one costs

Named strategies are bundles of decisions: where work happens, how long it lives, who integrates, how releases
get cut. Pick by matching the bundle to the situation — not by which one has the best articles written about it.

## The four that matter

| Model | Shape | Good at | Costs | Fits |
|---|---|---|---|---|
| **Trunk-based** | everyone commits small batches to `main` (or very short branches, hours) | integration never hurts; CI stays honest; no merge tax | needs discipline, fast tests, and often feature flags to hide unfinished work | solo, agent-heavy work, continuous deploys |
| **GitHub Flow** | short-lived branch → PR → merge to `main`, `main` is always deployable | review with a real gate, simple to teach, CI keys on PRs | the PR becomes the queue; small changes still wait for review latency | small teams, product with a staging/prod split |
| **Git Flow** | `develop`, `feature/*`, `release/*`, `hotfix/*`, `main` | parallel versions, planned releases, a place to freeze | the `develop`/`main` duality creates the big-merge and code-freeze problems DORA measured | only when you really ship multiple maintained versions at once |
| **Release-train / long-lived** | branches per epic or version, merged at the end | hard-to-deploy targets (app stores, firmware, on-prem) | merge events are expensive, conflicts compound, work is invisible until it lands | platform-imposed cadence, not preference |

DORA's measurements are the closest thing to a standard, and worth quoting in an interview: elite performers have
**three or fewer active branches** in the repository, **merge to trunk at least daily**, and have **no code
freezes and no integration phases**. Long-lived branching is associated with larger, more complex merges,
stabilization effort, and "code lock" periods. The named thresholds to use as defaults: a branch older than a few
days is a risk, two weeks of active development is long-lived by any definition.

## Choosing without ceremony

```text
who integrates the work?            → nobody but the user          → trunk-based, local merges
                                      a reviewer on the origin side → GitHub Flow
several shipped versions at once?   → yes, and they differ in code → release/* + hotfix/* (+ support/*)
                                      → no                           → one trunk, no develop
can unfinished code sit in trunk?   → yes (flags, or nothing breaks) → trunk-based
                                      → no                             → branch per slice, merge daily-ish
how many agents/sessions write?     → 1          → no coordination machinery
                                      → many       → claims + worktrees (03, 04) regardless of the model above
```

Note the last two rows: **the agent situation is orthogonal to the strategy.** Trunk-based with five sessions
still needs claims and worktrees; Git Flow with one agent still needs branch deletion after merge.

## Where each model breaks in practice

- **Trunk-based without flags** = unfinished features shipped by accident. If the project has no toggle
  mechanism, "merge daily" is not honest advice; say what the exposure is and shorten batches instead.
- **GitHub Flow with a slow review** = branches age out; DORA calls out the mechanism directly (heavy or
  asynchronous review makes developers batch changes, which makes review worse). If PR latency is days, the fix
  is the review process, not longer branches.
- **Git Flow kept out of habit** = a `develop` nobody merges into, plus release branches that never get deleted.
  Detect it (`git branch -r --merged`), propose retiring it, do not replicate it because it exists.
- **Squash-merge everywhere** = branch history vanishes; the durable record must then live in messages and the PR,
  which is a `commit`-skill concern, and worth telling the user before they choose it.

## Hotfix, release, and backport

Conventional shapes (adapt the prefixes to the chosen naming):

```bash
git switch -c release/v1.2.0 main            # cut; then version-bump commits live here
git switch -c hotfix/1.1.3 crash-on-start v1.1.2      # urgent fix against a shipped tag
# fix, verify, tag v1.1.3, then bring it forward:
git switch main && git merge --no-ff hotfix/1.1.3
git switch release/v1.2.0 && git merge --no-ff hotfix/1.1.3   # never let a fix miss a newer line
```

The rule that keeps this from becoming archaeology: **a fix merged to the shipped line must reach the trunk**
(cherry-pick or merge, whichever preserves the history the team reads), and **a fix made on the trunk must reach
any release line still supported**. Every one of those crossings is a decision someone should see in the branch
name — which is why `hotfix/*` earns its place even in a mostly trunk-based project.

## Integrating parallel work

The isolation is the easy half; recombination is where parallel branches cost what they saved.

1. **Pre-flight, before you finish a branch:** does it still merge?
   ```bash
   git merge-tree $(git merge-base HEAD origin/main) HEAD origin/main | grep -c '^+<<<<<<<'
   ```
   `git merge-tree` does a three-way merge without touching the repository — cheap enough to run on every agent's
   "done" report, and it turns a surprise conflict into a scheduled one.
2. **Rebase or merge onto the current trunk first**, then declare the branch ready. A branch that was green
   against a three-day-old trunk is not green.
3. **Integrate one at a time, in dependency order** — after each merge, the next branch rebases onto the new
   trunk. Merging three branches in one pass produces a conflict with three authors and no bisectable state.
4. **Ensembles** (several agents solving the same problem): keep one, delete the rest — cherry-pick the pieces
   worth keeping and say in the commit message which attempt won and why. Merging two alternative implementations
   of one thing is how a repo grows two of it.
5. **After merge: delete.** `git push origin --delete <branch>`, `git branch -d <branch>`, release the claim,
   remove the worktree, prune. Branch inventory is the metric that quietly ruins the strategy chosen in this file.

`git branch -d` refuses when unmerged — that refusal is information, not an obstacle. `git branch -D` on a branch
you did not create is a destructive act: confirm first (SKILL.md's gates).

## Migrating a live strategy

Do not rename an in-flight convention. New branches follow the new rule; old ones live out their life;
CI and bots get reconfigured in the same change so the tools do not fail the very branches the policy just
allowed. Retire `develop` by merging it once, announcing it, and deleting it — not by quietly stopping to use it,
which leaves every clone with a stale remote-tracking branch and every agent guessing.
