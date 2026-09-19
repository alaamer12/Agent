---
name: planner
description: Enforce rigorous, systematic, language-agnostic planning before implementation. Captures the full request, first clarifies vague or slang-heavy language if needed, then generates structured hypotheses that surface explicit requirements plus professional reading-between-the-lines concerns, gathers local and web context, iterates with the user until hypotheses are approved, and finally produces a solid plan. Use in planning-mode or quest-mode, or whenever the user asks for a plan, architecture outline, implementation roadmap, or disciplined decomposition of a complex task. Triggers include planner, planning mode, quest mode, make a plan, rigorous plan, hypothesis-driven planning.
---

# Planner

Enforce a disciplined, hypothesis-driven, **universal** planning process. The skill is language-agnostic and technology-neutral (polyglot principles). It adapts to the current project and forces thorough coverage of both stated requirements and the professional concerns a senior engineer would notice between the lines.

## What a Hypothesis Is (and Is Not)

A hypothesis is **not** “I did not understand your query.”

A hypothesis is:  
**“I think your query could mean that <precise professional interpretation>.”**

It is a proposed reading of the request that makes implicit expectations, constraints, and engineering judgment explicit so the user can confirm, correct, or reject it.

## Core Principle

Never jump to implementation or a final plan.  
First capture the request → clarify any vague or slang language if needed → surface both explicit and implicit requirements through hypotheses → gather context → obtain explicit user approval on the hypotheses → only then produce the plan.

## Mandatory Workflow

### 1. Capture the Request

- Create `.planner/` at the project root (or current working directory).
- Write the complete original user prompt, unedited, into `.planner/request.md`.
- Record any immediately available context in `.planner/context-snapshot.md`.

### 2. Pre-Hypothesis Clarification (Mandatory Gate)

**Before writing any hypothesis**, check whether the request (or any key term in it) is vague, ambiguous, or uses slang / informal language that could be misinterpreted.

If yes:

- Stop.
- Ask the user short, precise clarifying questions.
- Do **not** invent interpretations yet.
- Wait for answers.
- Only after the language is clear enough to interpret professionally, proceed to hypothesis generation.

Examples of when to ask first:
- Weird slang or highly informal phrasing whose meaning is unclear
- Overloaded or undefined terms (“make it fast”, “make it nice”, “handle the scale”, “do it the right way”)
- Contradictory or incomplete statements

If the request is already clear enough, skip this gate and move on.

### 3. Deep Analysis & Hypothesis Generation

Treat the (now clarified) request as still incomplete from a professional standpoint. Explicitly search for:

- Stated requirements
- Implicit success criteria and unstated assumptions
- Hidden constraints (performance, security, compatibility, maintainability, scalability, operability)
- Non-functional and evolutionary needs
- Edge cases, failure modes, ownership boundaries
- Relevant engineering best practices and sound judgment

**Professional “between the lines” thinking** is required.  
See `references/professional-thinking.md` for the full technique, hypothesis categories, and phrasing style.

Write each distinct hypothesis as its own file under `.planner/hypothesis/` using sequential zero-padded numbering and short descriptive names:

```
.planner/hypothesis/
├── 01-core-requirement.md
├── 02-implicit-constraint.md
├── 03-scalability.md
└── ...
```

### 4. Hypothesis File Template (Mandatory)

Every hypothesis file must follow this structure:

```markdown
# Hypothesis N — Short Title

## User Requirement Statement
[Direct quote or precise paraphrase of the (clarified) request]

## Interpolation
[Enriched professional interpretation — see references/professional-thinking.md.
This is the “I think your query could mean that …” part.
Stay at the level of principles and architecture. Do not lock into a single language or framework.]

## Supporting Evidence
- Local: [files, config, existing patterns]
- Research: [sources or key facts]
- Assumptions made: [list explicitly]

## Open Questions
- [Honest remaining ambiguity]
```

### 5. Context Gathering

Before finalizing hypotheses:

- Read local project documentation, README, architecture notes, and dependency manifests. Prefer versions and patterns already declared in the project.
- Examine existing code structure and conventions the plan must respect.
- Perform web research for current best practices and primary sources. Prefer official docs. When available, leverage deeper research skills (`search-deeply`, etc.).
- Record key findings in `.planner/research-notes.md`.

### 6. User Review Loop

Present **all** hypotheses in a clear numbered summary.  
**Do not** generate the plan until the user explicitly approves the set (or provides corrections).

- Confirmed → proceed to plan generation.
- Rejected or amended → revise the affected hypothesis files and re-present.
- Stay focused on the hypotheses; do not start implementing or expanding scope.

### 7. Plan Generation (Only After Approval)

Produce a concrete plan that:

- Maps every approved hypothesis to work items.
- Orders work by dependency and risk (foundational / high-risk first).
- Defines clear deliverables, acceptance criteria, and verification steps.
- Surfaces remaining risks and mitigations.
- Stays strictly inside the boundaries of the approved hypotheses.
- Remains language-agnostic and technology-neutral unless the user has already chosen a stack.

Write the final plan to `.planner/plan.md` and present it.

### 8. Cleanup (Optional)

After the plan has been delivered and the user is satisfied:

- Ask the user whether they want to keep the `.planner/` folder for traceability or delete it.
- If they choose to delete it, remove the entire `.planner/` directory.
- If they choose to keep it, leave it as-is.
- Never delete it automatically.

## Directory Layout Produced by the Skill

```
.planner/
├── request.md
├── context-snapshot.md
├── research-notes.md
├── hypothesis/
│   ├── 01-....md
│   └── ...
└── plan.md                 # written only after hypothesis approval
```

## Hard Rules (Polyglot + Professional)

- Never skip the pre-hypothesis clarification gate when language is vague or slang-heavy.
- Never skip the hypothesis stage or the user review loop.
- A hypothesis means “I think your query could mean that …”, never “I didn’t understand you”.
- Never invent requirements that cannot be traced to the original request, local context, or explicit research.
- Prefer versions and patterns already present in the project.
- Keep all hypotheses and the plan at the level of **principles and architecture**. Do not prescribe a single language, framework, or library unless the user has already chosen one.
- When multiple viable technical approaches exist, surface the options with pros/cons and let the user decide (polyglot principle).
- The `.planner/` folder is optional after the plan is delivered — ask the user whether to keep or delete it.
- If the request is trivial or the user explicitly asks to skip planning, note the exception and still capture the request in `.planner/` for traceability.

## Supporting References

- `references/professional-thinking.md` — how to read between the lines and generate professional hypotheses
- `references/hypothesis-template.md` — exact template + quality checklist
- `references/example-hypotheses.md` — concrete examples
- `assets/plan-template.md` — structure for the final plan

## When to Prefer Other Skills

- Pure deep architecture research without an implementation plan → `search-deeply`
- Creating a sub-agent brief → `professional-subagent`
- Designing language-agnostic skills or coding standards → `polyglot`
---
