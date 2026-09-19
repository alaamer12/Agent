---
name: subagent
description: Create high-quality professional prompts for sub-agents. Use when the main agent needs to delegate work to a specialized sub-agent or worker. Produces a structured brief with hierarchical Context, precise Goal, How, Autonomy Bounds, and Output Contract so the sub-agent stays focused, never decides, and returns full raw results instead of summaries. Triggers include sub-agent, subagent, delegate, spawn worker, professional brief, task handoff, isolated prompt.
---

# Professional Subagent

Generate a complete, self-contained brief that a main agent can hand to a sub-agent. The brief enforces isolation, clear boundaries, full evidence return, and zero decision-making authority.

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
3. Only after all raw material is shown, end with this exact structure:

### Raw Evidence
(all evidence already shown above)

### Findings
- ...

### Open Questions / Blockers
- ...

### Suggested Next Actions for Parent
- ...
```

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

## Optional Forked Mode

Use only when the sub-agent must continue the exact same conversational thread. In that case the brief may be shorter (Goal + How + Autonomy Bounds + Output Contract) and the runtime inherits recent parent messages. Isolation remains the default and safer choice.
