---
name: branch
description: 'Plans, names, and safely runs Git branches, including repositories several agents share. Three situations differ: alone; beside other agent processes (a second session or tool, e.g. Claude Code + Codex) sharing one .git; and your own subagents in this process. Where sessions can collide, the claim is a session-scoped ledger plus an atomic ref that git refuses to clobber - acquire, release, never steal; collisions resolve by renaming, splitting scope, or serializing. Ask-first where no standard exists, after detecting what the repo answers: naming, PR-on-origin versus local merge, whether a fix needs its own branch or may ride the feature flow, whether agent authorship is disclosed (a Co-authored-by trailer, an agent segment in the branch name) or deliberately absent, branch lifetime, who integrates. Permanent policy goes into AGENTS.md (agents-md owns it); session choices stay in the claim file. Covers worktree isolation, integration order, merge-tree conflict pre-flight, destructive-op gates.'
when_to_use: The user asks how to branch, which branch to create, how to name branches, how to run several agents or sessions on one repo without collision, whether to use worktrees, what a branch strategy should be, or is about to create/merge/delete branches in a repo shared with other agents.
argument-hint: "[plan | name | worktree | claim | policy] [topic]"
---

# branch

Branching has no universal standard, and the cost of picking wrong is paid in merge conflicts and clobbered work —
especially when the other worker is a process, not a person. So this skill does three things: **asks what the repo
cannot answer**, **makes agent collisions visible before they happen**, and **keeps the durable policy where the
next agent will actually read it**.

## Do this first: detect, then ask

Never ask what the repository already says. Check it, then ask only about what is genuinely undecided:

```bash
git symbolic-ref --short HEAD                        # the trunk, usually
git for-each-ref --sort=-committerdate --format='%(refname:short) %(committerdate:short)' refs/heads/ | head -20
git log --oneline --merges -8                        # merge commits? squash? rebase-only?
ls .github/workflows .gitlab-ci.yml azure-pipelines.yml 2>/dev/null   # who merges, and what triggers
test -f AGENTS.md && grep -niA6 "workflow\|branch\|author\|version control\|stash" AGENTS.md | head -40
git log -20 --format='%an <%ae>%n%(trailers:key=Co-authored-by)'   # is authorship already decided?
git config --get pull.rebase; git config --get merge.ff
```

From that you can usually *read* the incumbent convention: live branch names (50 `feature/*` branches says the
convention exists and is used), whether remote branches are deleted after merge, whether history is linear.

| Situation | Behavior |
|---|---|
| Convention is visible in the repo | follow it, say you detected it, ask nothing about that axis |
| Repo is new, or conventions conflict with each other | **ask** (the five questions below) |
| The user is asking for a personal/human convention you cannot see | ask; do not import Git Flow because it is famous |

## The five questions (ask in one round, not one at a time)

1. **Naming** — "How should branches be named?" Offer real options with what each buys: `<type>/<description>`
   (Conventional Branch: `feature/`, `fix/`, `hotfix/`, `release/`, `chore/`, plus `ai/`, `claude/`, `codex/`,
   `copilot/`, `cursor/` for agent-authored work), issue-first (`1234-login-page`), `owner/topic`,
   `feature/x-y-semantic-name`, date-scoped `sprint-2026-11/…`, or the repo's incumbent pattern. Details and the
   validation rules: [`02-naming.md`](references/02-naming.md).
2. **Where merging happens** — "Is a PR on the origin side the merge point, or are you solo and merging locally?"
   Solo/local means branches are an *organizing* mechanism: keep them short-lived, integrate into the trunk by
   hand, and there is no review gate to lean on — so the discipline moves into the branch lifetime and the commit
   hygiene. PR-side means the branch name and history shape are **contract surface** (`main` protection rules, CI
   path filters, `Closes #` semantics depend on them).
3. **Separation policy** — "Does every fix get its own branch, or may a fix commit ride inside the feature branch?"
   Both are defensible: strict separation keeps `hotfix/*` cherry-pickable into a release while a feature is
   unfinished; allowing fixes inside feature flow costs less ceremony and is usually right for solo work. This
   answer decides what happens the moment a fix interrupts a feature — see
   [`commit`'s fix-interrupts-feature reference](../commit/references/12-fix-interrupts-feature.md) for the
   mechanics, and record the *policy* here.
4. **Lifetime and complexity** — "How long may a branch live, and how many kinds of branch do you want?" Trunk
   names, `release/*` existence, hotfix path, whether `develop` exists at all. DORA's measured targets are worth
   quoting to the user as a default: **three or fewer active branches, merged to trunk at least daily, no code
   freezes**; a few days of age is not "long-lived" by anyone's definition, two weeks of active development is.
5. **Authorship disclosure** — "How should agent-authored work be identifiable?" Two places it can appear, and
   people feel differently about each, so neither may be decided silently:
   - **commits**: a co-author trailer (`Co-authored-by: Qoder (Qwen) <noreply@…>`) or nothing, with the human as
     sole author;
   - **branches**: an identity segment (`qoder-qwen/feature/login-page`, or the registered `ai/`, `claude/`,
     `codex/` prefixes) or no segment at all.

   Ask only if the repo does not already answer — `git log --format='%(trailers:key=Co-authored-by)'` and the live
   branch names are the evidence. Then write the answer into `AGENTS.md`'s **Version Control** section (the
   agents-md home for git tiers, stash policy, and authorship) so nobody is asked twice. Refusing the
   trailer is a legitimate choice; so is requiring it; deciding it for the user — in either direction — is not.
   Details: [`00-the-interview.md`](references/00-the-interview.md), [`02-naming.md`](references/02-naming.md).

Then **restate the chosen strategy in six lines and get agreement before creating anything.** A branch strategy
disagreed with after a week of branches is expensive to unwind.

## Which of the three situations are you in

| Situation | What changes |
|---|---|
| **A. Alone** — one human, one agent, no other writer | No claim file. The only discipline is lifetime and naming. Worktrees optional, for parallel local experiments. |
| **B. Other agent *processes*** — a second session (another terminal, another tool: Claude Code + Codex) that shares the same `.git` | **Coordination is mandatory.** Claims go in the session-scoped record + atomic ref: [`scripts/branch_claim.py`](scripts/branch_claim.py). Each session works in its **own worktree**, never two agents in one working tree. |
| **C. Your own subagents**, same process | Same collision risk, one big advantage: you are the single writer of the coordination state, so *you* allocate branches up front and hand each worker its branch and path in the brief. Prefer worktree isolation when the harness supports it (this CLI's `Agent` tool has `isolation: worktree`); fall back to "one branch per worker, worker never switches branches". |

B and C differ in one important way: in C you can serialize and re-merge centrally because you see all the results;
in B you cannot assume the other process is polite, so you must not rely on it reading your intentions — only on
the claim, which it either honors or you discover it did not.

## The session claim (situation B and C)

One hidden record per session, plus a ref that makes stealing impossible to miss:

```bash
python <skill-dir>/scripts/branch_claim.py acquire --branch feature/login-page --role subagent-3 \
  --worktree ../proj-login --ttl 4h --note "auth endpoints only"
python <skill-dir>/scripts/branch_claim.py status          # who holds what, including stale claims
python <skill-dir>/scripts/branch_claim.py release --branch feature/login-page
```

What it writes: `<git-dir>/agent-branch` — a readable, human-editable record of **what this session acquired and
what another acquirer should do** — and, when the branch name is claimable, `refs/agent/<slug>` created with a
zero-old-oid CAS, which is git's atomic "only if it does not already exist". Why both, what the collision policy
is (never steal: take a different name, split the scope, or serialize), TTL and stale-claim handling, and why the
file lives in the **common** git dir so every worktree sees the same ledger:
[`03-agent-coordination.md`](references/03-agent-coordination.md).

The claim file is **session-scoped state, never the project's policy**. If the user wants the strategy to outlive
the session, it goes in `AGENTS.md`.

## The permanent policy

When the user asks for strategy that holds "regardless of updates and feedback from the outer world", write it
down where agents read it every session — `AGENTS.md` §3 (Development Workflow), via
[`agents-md`](../../Viber/agents-md/SKILL.md), which owns that file. Template:
[`assets/templates/branch-policy-block.md`](assets/templates/branch-policy-block.md). It must answer: the trunk
name, the allowed branch kinds and naming pattern, where merges happen and by what command, lifetime cap, the
fix-interrupts-feature rule, the agent-claim rule and worktree convention, and what is forbidden without asking
(`push --force` on shared branches, deleting a branch another created, rewriting published history — the backup
gate is in [`commit`'s repairing-history reference](../commit/references/14-repairing-history.md)).

A policy that is not in `AGENTS.md` and not in the repo docs is a conversation. Say that when it happens:
"this holds for this session only — want it permanent?"

## Creating and integrating

Recipes in [`04-worktree-playbook.md`](references/04-worktree-playbook.md) and
[`01-strategies.md`](references/01-strategies.md). The defaults worth knowing:

```bash
git switch -c feature/login-page              # A: from the trunk, after git fetch to be current
git worktree add -B agent/login ../wt-login main   # B/C: own directory, own branch, shared objects
git merge-tree $(git merge-base HEAD origin/main) HEAD origin/main | grep -c '^+<<'  # conflict pre-flight
git worktree remove ../wt-login && git worktree prune   # cleanup after the branch is integrated
```

Integrate one at a time in dependency order, rebase or merge onto the current trunk **before** declaring a
branch ready, and never run two agents in one working tree. A branch that exists but is not integrated is
inventory: after merge, delete it (`git push origin --delete`, `git branch -d`) or the active-branch count
quietly destroys the strategy you chose.

## Boundaries and gates

| Action | Gate |
|---|---|
| Creating a branch | free — but on the agreed naming, from the right base, after `git fetch` |
| Deleting a branch you did not create | ask; check `git branch -r --merged` first, unmerged deletion loses work |
| `push --force`, `push --force-with-lease` on a shared branch | ask. Another agent or person may have built on it. `--force-with-lease` is the minimum, never bare `--force` |
| Rewriting published history | the backup-ref gate, then ask (see `commit` 14) |
| Touching a branch another session claimed | **no.** The claim exists precisely to make this visible; renegotiate instead |
| Committing, message conventions, staging | [`commit`](../commit/SKILL.md) |
| Reviewing what a branch changed | [`diffs`](../diffs/SKILL.md) |
| Making the policy durable in `AGENTS.md` | [`agents-md`](../../Viber/agents-md/SKILL.md) |

This skill plans and executes branch structure. It does not decide product scope, and it does not silently pick a
famous model (Git Flow) because it exists: **the user's answer wins over the literature**.

## References

| File | Owns |
|---|---|
| [`00-the-interview.md`](references/00-the-interview.md) | detection-before-asking, the questions with real options and trade-offs, how to record the answer, what not to ask |
| [`01-strategies.md`](references/01-strategies.md) | trunk-based, GitHub Flow, Git Flow, release/hotfix/backport, solo-dev variants, lifetime rules, which situation each fits, and when a strategy is being violated |
| [`02-naming.md`](references/02-naming.md) | naming schemes, Conventional Branch types and AI prefixes, case and charset rules, ticket ids, validators, migrating a convention |
| [`03-agent-coordination.md`](references/03-agent-coordination.md) | the three situations in depth, the claim ledger and ref, collision policy, TTL/stale handling, subagent briefs, multi-tool etiquette |
| [`04-worktree-playbook.md`](references/04-worktree-playbook.md) | worktree mechanics and gotchas (per-worktree vs shared state, locking, cleanup cost, ports, DBs, deps, ignores, repair) |
| [`05-permanent-policy.md`](references/05-permanent-policy.md) | writing the lifecycle policy into AGENTS.md, what must be in it, drift detection, how it survives upgrades |
| [`06-sources.md`](references/06-sources.md) | the fetched specifications and docs with access dates, and what each one is evidence for |
