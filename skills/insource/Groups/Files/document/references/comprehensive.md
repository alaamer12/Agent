# Comprehensive Documentation Style

A comprehensive document covers the requested subject thoroughly, including relevant details, context, explanations, and supporting evidence. It fully addresses the requested scope without omitting relevant material and without adding unrelated content or unnecessary repetition.

## What comprehensive may include (depending on the request)

- Background and initial conditions
- The original problem or objective
- The complete sequence of important events
- Investigation methods
- Tools and commands used (with relevant arguments and purpose)
- Files inspected or modified
- Errors encountered and diagnostic output
- Incorrect approaches and why they failed
- Corrections: what changed, why it was appropriate, how it addressed the cause, alternatives considered, trade-offs
- Verification procedures and results (tests, reproduction steps, observed outcomes, confirmation of the fix, remaining limitations)
- Technical discoveries and findings
- Sources consulted, why they were consulted, what they contributed, and any limitations or uncertainty
- Decisions and their rationale
- Unresolved issues and limitations
- Final outcomes and resulting state

## Resource and evidence rules

Document usage of resources at the requested level of detail:

- Tool or command names, relevant arguments, purpose of each operation
- Important outputs and errors returned
- What each operation established and how results influenced subsequent actions

For external research:

- Which sources were consulted and why
- Relevant information obtained
- How that information affected investigation or decisions
- Limitations or uncertainty in the sources
- Source links when available and useful

Never invent commands, outputs, URLs, citations, or tool operations. Only claim actions that available evidence supports.

## Structure guidance

Prefer chronological sections for investigation histories. Use topic-based or problem-evidence-resolution structures when they better serve the purpose. For long documents, employ clear headings and subsections so detailed information remains navigable.

Preserve technical specificity. When the request involves debugging, dumps, symbols, observability integrations, configuration, or similar, retain the concrete details rather than abstracting to generic lessons.

## Boundaries

Comprehensive does not mean:

- Adding material outside the requested scope
- Repeating the same information unnecessarily
- Expanding a concise request into an exhaustive report
- Forcing every possible section into documents that do not need them
