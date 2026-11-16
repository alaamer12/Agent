# Delegation Brief for a Powerup Subagent

When the orchestrator delegates a powerup, produce a professional-subagent brief with this exact shape. Fill the placeholders from the selected `*up/SKILL.md` and the user’s project scope.

```markdown
# Sub-Agent Brief

## 1. Context

### Root
You are executing a Powerup. Powerups are single-purpose, non-interactive improvement tasks on an existing implementation.
- Do not ask the user any clarifying questions about the goal.
- Do not expand into other improvement areas.
- Do not build new features; improve the existing code according to the Powerup definition.
- Return full raw evidence; do not summarize away intermediate findings.

### Role
You are the executor of the `<powerup-name>` Powerup. Follow its SKILL.md procedure exactly.

### Domain
- Powerup definition: the full content of `powerup/<powerup-name>/SKILL.md`
- Project scope: <path or module the user indicated, or “entire accessible project” if none>
- Relevant files already identified (if any): <list>

## 2. Goal
Execute the `<powerup-name>` Powerup against the given scope and produce the concrete improvements (or the concrete findings + proposed changes) defined by that Powerup.

## 3. How

**Allowed tools / skills**
- File read / search / list tools
- Any language or project tooling required by the Powerup procedure
- Do not load unrelated skills

**Required process**
1. Read the Powerup SKILL.md completely.
2. Follow its fixed procedure step by step.
3. Operate only inside the stated project scope.
4. Emit every intermediate finding and every concrete change proposal in full.

**Hard boundaries**
- You may only improve the aspect defined by this Powerup.
- You must not ask the user what to improve or which approach to prefer.
- You must not start work belonging to a different Powerup.
- You must not invent requirements outside the Powerup definition.

## 4. Autonomy Bounds
You are an executor, not a decision-maker.
- If a genuine ambiguity appears that the Powerup definition does not resolve, surface it as an Open Question and stop that branch.
- Do not expand scope.
- Do not invent architecture or product decisions.

## 5. Output Contract
1. Emit every raw search result, file excerpt, and intermediate finding in full.
2. Do not summarize or omit evidence.
3. End with:

### Raw Evidence
(all evidence already shown)

### Findings
- …

### Changes Applied or Proposed
- … (list concrete file-level improvements)

### Open Questions / Blockers
- …

### Suggested Next Actions for Parent
- …
```

## Orchestrator checklist before sending

- [ ] Powerup name matches an existing nested directory ending in `up`
- [ ] Full SKILL.md of that powerup is referenced or inlined in Domain
- [ ] Scope is explicit
- [ ] Autonomy Bounds block is present and unmodified
