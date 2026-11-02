---
name: parallize
description: 'Plan and run parallel work: the main agent decides in chat how to fan out a large or newly approved job, keeps the most sensitive work for itself, and hands bounded slices to subagents in waves that respect the harness concurrency cap. Use when the job is large enough to split, a plan has just been approved, the user says "parallelize/parallize the work", "run agents in parallel", "fan this out", "use a worker pool", "split this across agents", or when the agent itself sees three or more independent chunks. Core rules: no two agents write the same file; interfaces and naming decided once before launch; the main agent never sits idle while subagents work; the wave size follows dependencies and review load, not the maximum; a failed slice is re-run alone, never the whole wave. Not for deciding what to build (planner), writing the per-agent brief itself (subagent), or the pre-code gates (implement).'
when_to_use: A job is large or an approved plan is about to be executed, or the user asks to parallelize/fan out/spawn workers — also self-initiated when a task has several genuinely independent chunks.
argument-hint: "[the plan, task, or scope to parallelize]"
---

# parallize

Parallelism is a schedule, not a headcount. The main agent plans the fan-out in chat, keeps the sensitive work for itself, and gives subagents bounded slices in waves that fit inside the harness's concurrency cap.

## When it runs

- A large job with several independent parts, or an approved plan about to be executed.
- The user says "parallelize the work", "fan this out", "run agents in parallel", "worker pool".
- The agent notices on its own that a task has three or more chunks that do not depend on each other.

## Step 0 — is fan-out worth it?

Fan-out pays when the work splits along real seams. It costs coordination, duplicated context, merge work, and conflicting writes.

| Parallelize when | Keep it serial when |
|---|---|
| Slices have disjoint write sets and clear interfaces | Everything touches the same few files |
| Each slice is verifiable on its own | The work is one chain of dependent decisions |
| The slice is big enough to justify briefing an agent | The slice is a five-minute edit |
| A wrong slice can be detected and re-run cheaply | A mistake is expensive and hard to localize |

If the plan collapses to one row, say so and do the work directly — that is a correct outcome, not a failure to parallelize.

## Step 1 — think in chat before spawning anything

Write the fan-out plan where the user can see and correct it, using `assets/templates/fanout-plan.md`: the goal, one row per slice (output, files owned, dependencies, risk), the wave schedule, and what the main agent keeps. Do not spawn a single agent before this plan is stated.

## Step 2 — split by ownership, not by topic

- **No two agents write the same file.** Each slice owns explicit paths; everything else is read-only for it.
- **Shared files get one owner** — lockfiles, indexes, config, schemas, generated registries — or the main serializes them itself.
- **Interfaces first.** Contracts another slice depends on (types, function signatures, API shapes, data formats) are decided and written down before launch; a subagent never invents an interface another slice consumes.
- **Ambiguity is resolved once, centrally.** Two agents interpreting the same open question silently diverge.

How to cut a job well, and the dependency shapes that work: `references/01-decomposition.md`.

## Step 3 — the main agent keeps the sensitive work

The main agent is not a dispatcher waiting for replies. It takes the riskiest work and does it while the waves run:

- architecture and interface decisions, and anything that constrains two slices at once;
- security-, auth-, payment-, or data-migration-sensitive code;
- destructive operations (deletes, rewrites, history changes);
- the shared files above, and the final integration.

Subagents get work that is independent, fully specified, and verifiable by their own checks. If the sensitive work is too big to finish alongside the waves, run fewer waves — never hand sensitivity away to save time: `references/03-main-agent-work.md`.

## Step 4 — waves under the cap

The harness caps how many agents can run at once — treat [20] as a hard ceiling and verify it when it is unknown. The cap is a limit, not a target.

- Size each wave by independence and review load: [3–5] for coupled work, up to the cap for a sweep of truly independent files.
- A wave ends when its results are integrated, then the next launches. A slice that depends on another waits for it; independent slices can share a wave.
- Stop increasing parallelism when merge and review cost exceeds the time saved. "As much as the job allows" is the rule, not "as many as the cap allows".

Launch mechanics, monitoring, failure re-runs, and diminishing returns: `references/02-waves-and-limits.md`.

## Step 5 — every slice gets a real brief

Each subagent gets a self-contained brief from the `subagent` skill: context, scope with owned paths, do-not-touch list, done-when checks, and return format. Add the exact snapshot it was planned against (commit, file version). A vague slice returns vague work that costs more to integrate than to have done.

## Step 6 — integrate and verify

- Merge in dependency order; resolve conflicts by the interface decided in Step 2, not by whichever slice landed first.
- Review each slice against its done-when list; run the project's own checks.
- Look for duplication across slices — the same helper written twice is the normal failure of a fan-out.
- Report: what ran in parallel, what the main agent did itself, which slices were re-run, what is still open.

Integration order, conflict rules and the review pass: `references/04-integration.md`.

## When a slice fails

Re-run **that slice** with the failure evidence; do not restart the wave. If it is blocked on something another slice owns, the main agent unblocks it or re-scopes it. A slice that keeps failing is a sign the cut was wrong — merge it back into the main's own work.

## When the harness cannot spawn subagents

Some harnesses only run separate CLI agent processes. The same plan applies; the mechanics differ: log per agent, track session ids, monitor, clean up. See `references/05-external-cli-agents.md`.

## Boundaries

| Not this | Go instead |
|---|---|
| Deciding what the work is or sequencing it | `planner` |
| Writing the per-agent brief | `subagent` |
| Pre-code grounding and toolchain checks | `implement` |
| Isolating agents in worktrees or branches | `branch` |
| Running checks inside one slice | the project's own test commands |

## Files

| Need | Load |
|---|---|
| How to cut a job into slices, dependency shapes, shared-file traps | `references/01-decomposition.md` |
| Concurrency cap, wave sizing, launching, monitoring, re-runs | `references/02-waves-and-limits.md` |
| Which work the main keeps, and how it works alongside waves | `references/03-main-agent-work.md` |
| Merge order, conflicts, review pass, final report | `references/04-integration.md` |
| Harness without subagents: CLI agents, logs, sessions, cleanup | `references/05-external-cli-agents.md` |
| The plan to state in chat before launching | `assets/templates/fanout-plan.md` |
| A worked fan-out from plan to merged result | `examples/feature-fanout.md` |
