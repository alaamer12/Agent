---
name: subagent
description: Create high-quality professional prompts for sub-agents. Use when the main agent needs to delegate work to a specialized sub-agent or worker. Produces a structured brief with hierarchical Context, precise Goal, How, Autonomy Bounds, and Output Contract so the sub-agent stays focused, never decides, and returns full raw results instead of summaries. Also covers pre-delegation environment consistency checks (to prevent sub-agent drift), requirements for exhaustive slightest-detail reporting back to the main agent, and detecting/mitigating race conditions between concurrently running sub-agents (e.g. shared scripts or files). Triggers include sub-agent, subagent, delegate, spawn worker, professional brief, task handoff, isolated prompt, parallel agents, concurrent agents.
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

## Optional Forked Mode

Use only when the sub-agent must continue the exact same conversational thread. In that case the brief may be shorter (Goal + How + Autonomy Bounds + Output Contract) and the runtime inherits recent parent messages. Isolation remains the default and safer choice.