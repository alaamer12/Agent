---
name: powerup
description: Orchestrate lightweight single-purpose improvement skills (any nested directory ending in up) against an existing project. Lists available powerups, validates the user request, and independently delegates each selected powerup to a subagent via professional-subagent. Use when the user invokes /powerup or asks to powerup or apply focused ups to existing code. Never invent new powerups on the fly — only those present as nested directories ending in up. Persona and behavior live in UP.md.
---

# Powerup

Lightweight single-purpose improvement agents. The main agent only discovers, validates, and delegates. Each nested `*up` skill defines a fixed improvement and executes it without asking the user what to do.

**Persona and full behavioral specification:** read `UP.md` before acting.

## Core Rules

1. **Single purpose per up** — each nested skill improves one defined aspect.
2. **Direct goal** — the up itself already states what “done” means.
3. **No user inquiry** — subagents never ask “what should I improve?” or “which approach?”.
4. **Independent delegation** — every requested up runs as its own subagent task.
5. **Improvement only** — operate on existing implementation; do not build new features.
6. **Lightweight** — no modes, no open decision points, no interactive workflows inside an up.

## Directory Contract

```
powerup/
├── SKILL.md              # this file (orchestrator entry)
├── UP.md                 # persona + behavior definition for the main agent
├── references/
└── <name>up/             # zero or more powerup skills (name must end in up)
    └── SKILL.md
```

Every nested directory whose name ends with `up` is a powerup. Discover them by listing this skill’s directory. If none exist, the available set is empty — report that and do not invent work.

## Mandatory Workflow (Orchestrator)

### 1. Load persona
Read `UP.md`. Adopt the professional reasoning style defined there.

### 2. Discover available powerups
List the immediate subdirectories of this skill that end with `up`.  
Record the set of valid names. The set may be empty.

### 3. Parse the user request
Extract the requested powerup names from the invocation.  
Accept short forms and map them to the full `*up` name when unambiguous given the current set.

### 4. Validate
- If a requested name has no matching nested `*up` directory → report the missing name and list the available powerups. Stop for that name.
- If the request is empty or contains only unknown names → report insufficiency and list available powerups. Do not invent work.

### 5. Delegate independently
For each valid requested powerup:

1. Load that powerup’s `SKILL.md`.
2. Build a professional-subagent brief using the template in `references/delegation-brief.md`.
3. Hand the brief to a subagent (via the professional-subagent skill).
4. Collect the subagent’s full raw output.
5. Surface the result to the user under a clear heading for that powerup.

Never merge multiple powerups into one subagent. Never perform the improvement work yourself in the orchestrator role.

### 6. Report
After all delegations finish, give a short summary of which powerups ran and any that were rejected.

## Progressive disclosure

| Need | Load |
|------|------|
| Persona and behavior of the main agent | `UP.md` |
| Exact subagent brief shape | `references/delegation-brief.md` |
| Powerup skill authoring rules | `references/up-authoring.md` |

## Hard constraints

- Do not create or invent a powerup that does not exist as a nested directory.
- Do not ask the user to further define an already-selected powerup.
- Do not let one powerup’s subagent perform another powerup’s work.
- Keep the orchestrator thin: discover → validate → delegate → report.
