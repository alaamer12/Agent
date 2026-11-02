---
name: subagent
description: 'Create high-quality professional prompts for sub-agents. Use when the main agent needs to delegate work to a specialized sub-agent or worker. Produces a structured brief with hierarchical Context, precise Goal, How, Autonomy Bounds, and Output Contract so the sub-agent stays focused, never decides, and returns full raw results instead of summaries. Also covers pre-delegation environment consistency checks (to prevent sub-agent drift), requirements for exhaustive slightest-detail reporting back to the main agent, detecting/mitigating race conditions between concurrently running sub-agents (e.g. shared scripts or files), and the default dispatch mode — sub-agents always run in the background unless the user explicitly asks for foreground. Triggers include sub-agent, subagent, delegate, spawn worker, professional brief, task handoff, isolated prompt, parallel agents, concurrent agents, background agents. It also carries the rulebook in the brief and clears the subagent''s authority questions with the user first.'
---

# Professional Subagent

Generate a complete, self-contained brief that a main agent can hand to a sub-agent. The brief enforces isolation, clear boundaries, full evidence return, and zero decision-making authority.

## Pre-Delegation Consistency Check

Before writing or dispatching any brief, the main agent must ensure the environment is in a known, consistent state so no sub-agent drifts from what the others assume. This is a mandatory pre-process step, not optional hygiene.

**Do this before delegating:**
1. **Snapshot the ground truth.** Re-read (don't rely on memory of) the exact files, configs, schemas, or interfaces every sub-agent will depend on. If two sub-agents touch overlapping surfaces, both briefs must be built from the *same* snapshot taken at the *same* moment.
2. **Freeze or version the shared state.** Where possible, pin sub-agents to a specific commit hash, file version, or timestamped snapshot rather than "the current state of the repo" — the repo can change mid-delegation.
3. **Normalize environment assumptions.** Confirm working directory, branch, installed dependencies, environment variables, and tool availability are identical across sub-agents unless the task explicitly requires divergence.
4. **Resolve ambiguity centrally, once.** If a convention, naming scheme, or architectural choice is unclear, the main agent decides it *once* before spawning anyone — never let two sub-agents independently interpret the same ambiguity, or their outputs will silently diverge.
5. **State the snapshot in the brief.** Every Domain section should reference the exact snapshot/version used ("as of commit X" / "file read at Y") so drift is detectable after the fact if the environment changes underneath the sub-agent.

If the main agent cannot guarantee a consistent starting point (e.g., a live system actively being edited by something else), it must say so explicitly in the brief's Domain section and instruct the sub-agent to re-verify the specific facts it depends on before acting.

## AGENTS.md travels with the brief — and authority is asked by the parent

A subagent inherits nothing: not the rulebook, not the conversation, not the user's authority grants. Two duties follow, both mandatory before dispatch.

**1. The brief carries the rulebook.** Read the project's AGENTS.md before writing the brief. Copy in the slice the task touches: the compressed baseline block (mandatory context, skills, shell, env, units, reports — per `agents-md` §10), the Privacy paths the task could write into, the Resourceful rule (project-local installs), and the Authority settings. Instruct the subagent plainly: *these rules bind you exactly as if you had read AGENTS.md; your report must name the rules that shaped your decisions and every action you took under an authority grant.* A subagent that has never seen the rulebook is not "independent" — it is unconstrained.

**2. The parent asks on the subagent's behalf.** A subagent cannot ask the user mid-task. So before dispatch, enumerate every action the task requires that AGENTS.md §13 marks *ask-per-session* — installing a binary outside the project, running an external process (emulator, daemon), writing to an existing database, touching credentials, changing machine config — and ask the user up front, in one batch:

> "The subagent will need to <action> to complete <task>. Do you grant authority for it?"

Record each answer in the brief's Autonomy Bounds as an explicit grant or denial. A denial is not a suggestion: re-scope the task, or drop the blocked step and report it. Never let the subagent meet the limit mid-task and improvise around it.

**3. Autonomous mode overrides the asking.** When the user has already put the agent in an anonymous, autonomous state — a skill like `iwts` ("I want to sleep", "take over", "finish it while I'm away") — the agent and its subagents hold **full authority** for the delegated work unless the user carved something out. Skip the batch question; state in each brief: "Autonomous session: full authority for this task within the project; anything the user excluded stays out, and the rulebook's hard constraints (privacy paths, never-sacrifice commitments) remain in force; destructive or out-of-project actions are still reported." Hard constraints are not authority grants — they stay binding even here.

## Mandatory Brief Structure

Always produce exactly this structure:

```markdown
# Sub-Agent Brief

## 1. Context

### Root
[shared project rules and non-negotiable constraints — keep to 20–50 lines]

### Role
[instructions specific to this type of sub-agent]

### Domain
[only the files, excerpts, prior findings, or package-level rules required for this exact task]

## 2. Goal
[one precise sentence stating exactly what must be produced]

## 3. How

**Allowed tools / skills**
- ...

**Required process**
1. ...
2. ...

**Hard boundaries**
- You may only operate inside: ...
- You must not: ...

## 4. Autonomy Bounds
You are an executor, not a decision-maker.
- If a choice appears, surface the options and stop.
- Do not expand scope. Do not start related work.
- Do not invent requirements, architecture, or product decisions.

**Authority (per the parent's pre-delegation ask):**
- Granted for this task: [actions the user approved, or "none beyond project-local work"]
- Denied / unavailable: [actions to avoid - report instead of executing]
- Session mode: [normal - ask-per-session rules carry over to the parent, not to you; or AUTONOMOUS - full authority within the project, hard constraints still apply]

## 5. Output Contract
1. Emit every raw search result, tool output, and intermediate finding in full inside the conversation.
2. Do not summarize or omit evidence.
3. The final report to the parent must be exhaustive, not a digest. It must let the main agent fully reconstruct what happened without re-running anything:
   - Every file touched, with exact paths, and what changed (not "updated the config" — the actual before/after or diff).
   - Every command run and its exact output, including failures, retries, and warnings — not just the successful final one.
   - Every assumption made along the way, even small ones, and why.
   - Every decision point that came up, even if it seemed trivial, and how it was resolved (or that it was surfaced instead of resolved, per Autonomy Bounds).
   - Anything unexpected encountered (unexpected file state, missing dependency, stale data, conflicting instruction) — report it even if it didn't block the task.
   - Nothing is "too minor to mention." The parent cannot ask follow-up questions mid-task, so the report is the sub-agent's only chance to transfer context — err toward over-including detail rather than trimming for brevity.
4. Only after all raw material is shown, end with this exact structure:

### Raw Evidence
(all evidence already shown above)

### Findings
- ...

### Open Questions / Blockers
- ...

### Suggested Next Actions for Parent
- ...
```

## Concurrent Sub-Agents & Race Conditions

Whenever the main agent delegates to **more than one sub-agent that may run at the same time**, it must explicitly think through whether they can collide — before dispatching, not after something breaks.

**Checklist the main agent must run through:**
1. **Identify shared mutable resources.** Do any sub-agents read *and write* the same file, script, database row, branch, port, cache, lock, or external API resource? Read-only sharing is safe; concurrent writes (or read-while-write) are the danger zone.
2. **Identify shared scripts/tools that hold state.** A shared script is not inherently risky — but if it writes to a fixed output path, mutates a temp file, appends to a shared log, or is not re-entrant, concurrent invocations can corrupt each other's output or interleave writes.
3. **Choose a concrete mitigation** and write it into the brief's "Hard boundaries" — don't just note the risk and hope. Options, roughly in order of simplicity:
   - **Isolate per sub-agent:** each sub-agent gets its own copy of the script/file/working directory (e.g., a per-agent temp dir or branch) and writes only there. Simplest and usually preferred when feasible.
   - **Shard the work:** partition the task so no two sub-agents touch the same resource at all (different files, different key ranges, different branches).
   - **Serialize:** if true parallelism isn't needed, run sub-agents sequentially instead of concurrently, or queue them so only one touches the shared resource at a time.
   - **Lock the resource:** if concurrent access to one shared resource is unavoidable, have the sub-agent acquire a lock file (or equivalent mutex) before writing and release it after, and instruct it to retry/back off on contention rather than overwrite.
   - **Make the operation atomic/idempotent:** write to a unique temp path then atomically rename/move into place, or design the write so repeated/interleaved execution can't corrupt state (e.g., append-only with unique IDs instead of in-place mutation).
4. **State the chosen strategy explicitly in the brief.** The sub-agent should not have to guess whether it's safe to write to a shared path — the "Hard boundaries" section must say exactly which resources are exclusive to it, which are shared read-only, and what locking/copying/isolation discipline to follow if it must touch something shared.
5. **When in doubt, isolate.** If the risk or mitigation is unclear, default to giving each sub-agent its own copy of anything it needs to write to, rather than inventing a locking scheme on the fly.

## Background by Default

Sub-agents run **in the background** — every spawn, unless the user
explicitly says not to (which is rare and lasts only for that ask).
Foreground execution blocks the conversation and buys nothing the parent
needs while the worker is digging, so background is the normal state, not
the exception:

- **Dispatch every sub-agent in background mode.** If the user says "run
  it in the foreground" / "wait for it" / "not in background", honor it for
  the named task(s) only; the next delegation is background again.
- **Never poll or wait on a running background agent.** Completion arrives
  as a notification — while agents run, the parent continues genuinely
  independent work or answers the user; it does not sleep-loop on status.
- **Results are claims on arrival, not facts mid-flight.** Nothing about a
  background agent's outcome is known until its completion report lands;
  the parent must not describe, assume, or fabricate its progress or results
  to the user before then.
- **Ordering matters when a later step consumes an earlier agent's output.**
  If work truly cannot proceed until agent A returns, say so to the user
  ("blocked on X, will continue when it lands") instead of silently
  foregrounding A out of anxiety — or run the dependent step as its own
  agent dispatched after A's completion notification.
- **Background is concurrency, so the race checklist above applies to
  every batch, not just "parallel" ones** — N background agents touch the
  environment at the same real time.
- **Keep the user's view honest:** when dispatching, state what was sent,
  in the background, and what will be reported back when each lands.

## Rules the Main Agent Must Follow

1. **Hierarchical context only**  
   Inject Root + Role + Domain slice. Never dump the full conversation history or entire codebase.

2. **Single precise Goal**  
   One sentence. State the exact artifact or result that must be produced. Vague goals are forbidden.

3. **Explicit How**  
   List the tools/skills the sub-agent may use, the required process steps, and hard boundaries.

4. **Autonomy Bounds are non-negotiable**  
   Copy the block above into every brief. The sub-agent is forbidden from making decisions or expanding scope.

5. **Full raw evidence first**  
   The sub-agent must surface every tool output and finding in the conversation. A short structured summary is allowed only at the very end.

6. **Treat output as claims**  
   The parent must inspect the raw evidence before accepting any conclusion.

7. **Run the Pre-Delegation Consistency Check first**  
   Never spawn a sub-agent against a snapshot that might already be stale, and never let two sub-agents independently resolve the same ambiguity — resolve it once, centrally, before dispatch.

8. **Demand exhaustive reporting**  
   Every brief's Output Contract must require full, slightest-detail reporting per the Output Contract rules above — the main agent's understanding of what happened is only as good as what the sub-agent chose to report, so nothing gets left out as "not worth mentioning."

9. **Think through race conditions before parallel dispatch**  
   Before running sub-agents concurrently, walk the Concurrent Sub-Agents & Race Conditions checklist and bake the chosen mitigation (isolation, sharding, serialization, locking, or atomic writes) into the brief's Hard boundaries — don't discover the collision after it happens.

10. **Dispatch in background, never poll**  
    Background is the default for every spawn; foreground happens only on the user's explicit, per-ask instruction. No sleep-looping or progress-guessing while agents run — treat each completion report as the first moment its results are knowable (see Background by Default).

11. **Subagents obey AGENTS.md**  
    The brief carries the rulebook slice the task touches (baseline block, privacy paths, resourceful rule, authority settings); the report names which rules shaped decisions and every granted action taken. A subagent operating without the rulebook is unconstrained, not independent.

12. **Ask authority before dispatch, on the subagent's behalf**  
    Enumerate the ask-per-session actions the task needs (external installs, external processes, existing-DB writes, credentials, machine config) and get the user's grant or denial in one batch before spawning; record it in Autonomy Bounds. In an autonomous session (e.g. `iwts`), the agent and its subagents hold full authority unless the user carved something out — the brief says so, and hard constraints still apply.

## Optional Forked Mode

Use only when the sub-agent must continue the exact same conversational thread. In that case the brief may be shorter (Goal + How + Autonomy Bounds + Output Contract) and the runtime inherits recent parent messages. Isolation remains the default and safer choice.