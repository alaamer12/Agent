# Authoring a New Powerup (`*up`)

A Powerup is a nested skill under `powerup/` whose name ends with `up`.

## Naming

- One or two descriptive words + the suffix `up`
- Examples: `typeup`, `errorup`, `performanceup`, `backend-performanceup`
- The name itself must make the single purpose obvious

## Required shape of `*up/SKILL.md`

```yaml
---
name: <name>up
description: <one-line purpose and when the orchestrator should select it>
---
```

Body must contain:

1. **Purpose** — one clear sentence
2. **Goal** — the concrete outcome that means “done”
3. **Fixed procedure** — numbered steps the subagent follows without branching into user questions
4. **Out of scope** — explicit list of things this Powerup must not touch
5. **Output expectations** — what the subagent must leave behind (changed files, report section, etc.)

## Discipline (non-negotiable)

| Rule | Why |
|------|-----|
| Single purpose | Prevents scope creep into other ups |
| Direct goal | Subagent never has to interpret intent |
| No user inquiry | User already chose the Powerup |
| Fixed procedure | No modes, no open decision trees |
| Improvement-oriented | Works on existing code only |
| Lightweight | Keep under ~150 lines; no reference sprawl unless essential |

## What never belongs in a Powerup

- “Ask the user which approach they prefer”
- Multiple unrelated objectives
- General architecture redesign
- Feature work
- Interactive clarification loops

## Relationship to ordinary skills

Ordinary skills may have modes, questions, and multi-step interactive flows.  
Powerups intentionally strip that away so the subagent can execute immediately.
