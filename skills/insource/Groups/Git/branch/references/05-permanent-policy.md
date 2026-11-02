# The permanent policy — the part that outlives the session

Session decisions are a conversation. A lifecycle decision has to be readable by the next agent, in the place the
next agent looks: **`AGENTS.md`** (or the project's contributing guide, with `AGENTS.md` pointing at it).

## The trigger

Ask before writing it, and ask exactly once per project:

> This is a session-only answer right now. Do you want it as the project's fixed policy — so no future agent asks
> you again, regardless of what changes around it?

"Yes" → the block goes into `AGENTS.md` §3 (Development Workflow) via
[`agents-md`](../../../Viber/agents-md/SKILL.md), which owns that file. This skill supplies the content; it does not
edit `AGENTS.md` on its own initiative. "No" → say what happens next: the question gets asked again by whoever
arrives after you, and the claim ledger remains ephemeral.

## What the block must contain

Every line is a decision someone can act on, not a value. Minimum:

| Field | Why it is there |
|---|---|
| trunk name | so no agent guesses between `main`/`master`/`develop` |
| naming pattern + a real example | so `branch_name.py` can validate, and so agents collide less |
| **authorship disclosure** — co-author trailer in commits: yes/no + the exact spelling; agent segment in branch names: yes/no + which prefix | it is the question agents otherwise decide silently, in both directions |
| where merges happen and by what command | origin-side PR vs local merge; `merge --no-ff` vs squash vs rebase — this decides what history looks like later |
| branch kinds that exist | `release/*` and `hotfix/*` only if they are actually used; every declared kind invites its use |
| lifetime cap | a number ("merge within a working day; delete after merge"), because "keep branches short" is not checkable |
| the fix-interrupts-feature rule | the moment of highest pressure is where an agent must not improvise |
| the agent-claim rule | "shared repo: `branch_claim.py acquire` before creating a branch; worktree per session; never take a held name" |
| worktree layout + ignore | where isolated trees live and what must be gitignored |
| what requires asking first | force-push, deleting a branch you did not create, rewriting published history, retiring a branch |

Template: [`../assets/templates/branch-policy-block.md`](../assets/templates/branch-policy-block.md).

## Making it durable rather than aspirational

- **Point, don't duplicate.** If the full rules live in `docs/branching.md`, `AGENTS.md` carries the duty and the
  path — the same rule that keeps `agents-md` from becoming documentation.
- **Name the tools that enforce it.** A validator nobody runs is a suggestion; if the user wants enforcement, the
  proposal is a CI check or a `pre-push` hook running `branch_name.py` — **proposed, never installed silently**,
  because it changes what every future push of every contributor does.
- **Bots are part of the policy.** Renovate/Dependabot/release tooling create branches; configure their patterns
  to match or the first thing the policy does is fail on a bot.
- **Record the review date.** A policy block with no date cannot be audited later; drift detection below needs it.

## Drift detection (cheap, and worth running)

```bash
python <skill-dir>/scripts/branch_name.py conventions            # what the policy claims is allowed
git for-each-ref --format='%(refname:short)' refs/heads refs/remotes | head -40   # what actually exists
git log -20 --format='%an <%ae>%n%(trailers:key=Co-authored-by)'                   # what is really being written
git branch -r --merged | grep -v HEAD                              # branches that can be deleted
```

Report mismatches as findings, with the evidence, and let the user decide which side is wrong:

| Signal | Reading |
|---|---|
| live branches violate the declared pattern | the policy is aspirational — either enforce it or amend it |
| 30 active branches against a "merge within a day" cap | the cap is fiction; find out what is blocking integration instead of deleting the line |
| co-author trailers present while the policy says none (or the reverse) | someone is deciding authorship silently — re-ask, then fix the policy or the practice |
| stale `refs/agent/*` claims | sessions are ending without releasing; check the cleanup order in `04-worktree-playbook.md` |
| a retired branch (`develop`) still on the remote | the migration was announced to nobody |

Never "clean up" any of that unilaterally. An unused branch may be someone's unfinished week; a trailer someone
did not ask for may be a deliberate legal or attribution choice.
