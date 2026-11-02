---
name: antipattern
description: Investigates a software project, researches the engineering anti-patterns that matter for its stack, gathers evidence from code, architecture, business rules and dependencies, and documents which anti-patterns agents must avoid (usually as ANTIPATTERN.md). Use whenever the user asks about anti-patterns, code smells, AI slop, "what should we avoid in this codebase", wants project rules against bad patterns, wants an anti-pattern audit or report, or asks to create or update ANTIPATTERN.md, even if they never say "anti-pattern". Findings are rated for impact and confidence separately, kept to what project evidence supports, and a clean audit is a valid result. Identifies, investigates, recommends and documents only. Do NOT use to fix, refactor or enforce rules, for general code review, or to change application behavior.
when_to_use: The user asks what anti-patterns, code smells, or bad practices to avoid in a project; requests an anti-pattern audit, report, or rules document; mentions AI slop in a codebase; or asks to create or update ANTIPATTERN.md.
argument-hint: "[a pattern, an area, or 'audit this repo']"
---

# Antipattern

Investigate a project, find the anti-patterns that genuinely threaten *this* codebase, and document what agents and contributors must avoid. The deliverable is evidence-backed documentation. This skill never changes application code.

## Boundaries

One job: **identify, investigate, recommend, document.**

- Allowed: read files, run analyzers read-only, search the web, ask the user, write the report and the anti-pattern spec.
- Not allowed: fix or refactor code, change dependencies or project config, enforce the rules (lint rules, CI gates, hooks), alter application behavior.
- Run analyzers without autofix flags. Keep scratch output outside the repository (e.g. `/tmp/antipattern/`).
- **Never reproduce a secret.** For a suspected credential, name the location and the type; keep the value out of
  the report, the spec, and any search query. Web searches use pattern concepts, not code excerpts or details that
  identify the project.
- Respect repository instructions, and generated, vendored, fixture, and excluded areas. Do not scan or quote them
  as if they were the project's own code.
- Writes are limited to `ANTIPATTERN.md` (or the existing anti-pattern section being updated) and, in Mode C, the report.
- If the user also asks for fixes or enforcement, finish the documentation first, then say those steps are outside this skill and offer to hand off with the finished spec as input. The spec is what later work gets judged against, so it must exist before anyone starts fixing.

## Workflow

Copy and track:

```
- [ ] 1. Determine mode (A, B or C)
- [ ] 2. Understand the project
- [ ] 3. Research candidate anti-patterns
- [ ] 4. Investigate with evidence
- [ ] 5. Inquire with the user (Mode C only)
- [ ] 6. Document
- [ ] 7. Self-check
```

### 1. Determine mode

Run `python scripts/discover_scope.py <project-root>`. It reports existing `ANTIPATTERN.md` files, anti-pattern sections in docs, and agent instruction files (AGENTS.md, CLAUDE.md, ...). Combine with the user's request:

| Situation | Mode | Action |
|---|---|---|
| User named anti-patterns or an area | **A** | Investigate exactly that scope. |
| Nothing named, but ANTIPATTERN.md or anti-pattern sections exist | **B** | Read them first. Look for evidence. Propose additions only where evidence warrants. |
| Neither | **C** | Research, investigate, ask via `/inquire`, report, specify. |

The user's request outranks existing docs. If both exist, investigate the requested scope and write into the existing document instead of creating a second one. Never widen a focused request into a full audit. Edge cases: [references/scope-and-modes.md](references/scope-and-modes.md). Worked examples: [examples/mode-selection.md](examples/mode-selection.md).

### 2. Understand the project

Understand before judging: purpose and domain, stack, layers, modules, data contracts, business rules, integrations, existing conventions and ADRs. Follow real execution paths and imports; directory names alone do not explain architecture. Scale depth to project size and to the mode (Mode A needs only the parts relevant to the requested patterns). Method and scaling table: [references/project-understanding.md](references/project-understanding.md).

### 3. Research

- **Mode C:** research broadly using the candidate topics in [references/anti-pattern-catalog.md](references/anti-pattern-catalog.md), filtered by the project's stack and domain.
- **Modes A and B:** research only what is needed to define the named patterns precisely or to check them against current guidance.

Use credible sources (official docs, established engineering literature, post-mortems, issue trackers). Record each source with a one-line takeaway so the report can cite it. Candidates are hypotheses, never automatic violations.

### 4. Investigate with evidence

Examine the levels the candidates touch: code, business, application, system/architecture, resource. See [references/investigation-levels.md](references/investigation-levels.md). Run `python scripts/detect_tooling.py <project-root>` to find analyzers that already exist, and prefer them over writing new ones. See [references/static-analysis.md](references/static-analysis.md). A tree too large to trace in one pass is split into non-overlapping, read-only passes whose conclusions you re-verify yourself: [references/scope-and-modes.md](references/scope-and-modes.md).

### 5. Inquire (Mode C only)

Read the `/inquire` skill's own SKILL.md in full before building anything, then follow its real interface and workflow. Base the questions on the project's evidence, use multiple choice with multi-select where practical, and never ask what the code or docs already answer. Details and fallback: [references/inquiry-workflow.md](references/inquiry-workflow.md).

### 6. Document

- Mode C: HTML report through `/inquire` (sections A to F), then the final spec.
- Modes A and B: the spec only, plus a short findings summary in chat.

Structure, field definitions and the update procedure for existing docs: [references/documentation.md](references/documentation.md). Copy the blank skeletons in [assets/](assets/) (`ANTIPATTERN.template.md`, `finding.template.md`). Use [examples/](examples/) only to calibrate detail and tone, never as text to copy.

### 7. Self-check

Run `python scripts/check_spec.py <path-to-ANTIPATTERN.md>` and walk [references/checklist.md](references/checklist.md) before reporting back.

## Evidence rules

- Each finding states location, measured facts, interpretation, and confidence (High / Medium / Low) plus what would change it.
- **Impact and confidence are separate axes.** Ugly or unfamiliar code is not high-impact; a metric is not proof of
  consequence. Rate both, and keep low-confidence items as open questions rather than findings or rules
  ([references/documentation.md](references/documentation.md)).
- **A clean audit is a valid result.** State the scope inspected and the candidates you rejected, with the reason.
  Never invent a finding to justify the run or write a placeholder rule.
- A metric is evidence, not proof. A 600-line class suggests excess responsibility; it does not establish it.
- Verbose or AI-looking code is not "AI slop" by itself. Name the concrete defect (wrong type, invented API, duplicated rule) instead.
- Check for intentional decisions (ADRs, comments, README) before flagging something. A documented trade-off is context, not a finding.
- Prefer a handful of well-evidenced findings over a long shallow list. Prioritize by consequence in this project.

## Writing rules

Every recommended rule has: what to avoid, what to do instead, when it applies, why it matters, exceptions and trade-offs, and how compliance can be checked. A rule must be specific, scoped and checkable. "Avoid overengineering" is not a rule. Where a rule is easy to state but easy to misapply, add the optional **Example** field: a small before/after pair, labelled illustrative when it is not the project's own code. Quality bar and before/after samples: [references/documentation.md](references/documentation.md) and [examples/finding.md](examples/finding.md) and [examples/ANTIPATTERN.example.md](examples/ANTIPATTERN.example.md).

## Reference map

| Read | When |
|---|---|
| [references/scope-and-modes.md](references/scope-and-modes.md) | Request is vague, mixed, or the repo has several docs or packages |
| [references/project-understanding.md](references/project-understanding.md) | Step 2 |
| [references/anti-pattern-catalog.md](references/anti-pattern-catalog.md) | Step 3, or to define a named pattern |
| [references/investigation-levels.md](references/investigation-levels.md) | Step 4 |
| [references/static-analysis.md](references/static-analysis.md) | Choosing tools, interpreting metrics |
| [references/inquiry-workflow.md](references/inquiry-workflow.md) | Step 5 |
| [references/documentation.md](references/documentation.md) | Step 6 |
| [references/checklist.md](references/checklist.md) | Step 7 |
| [assets/](assets/) | Step 6: blank skeletons to copy into the output |
| [examples/](examples/) | Calibrating tone and detail of findings, questions, rules (filled samples, not to copy) |
