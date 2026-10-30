---
name: document
description: Generate Markdown documents that exactly match the user's requested purpose, audience, scope, structure, and level of detail. Supports comprehensive accounts, concise summaries, investigation histories, technical transcripts, and reconstruction of prior work. Use when the user asks to create, write, or produce a document, report, transcript, history, or Markdown file of previous work, investigations, decisions, or findings. Do not use for code, slides, spreadsheets, or non-document artifacts.
---

# Document

Create Markdown documents that fulfill the user's actual intent — not a preferred or conventional substitute.

## Includes

- Markdown documents whose purpose, audience, scope, structure, and detail level are driven by the user's explicit request
- Comprehensive accounts, concise summaries, investigation histories, technical transcripts
- Reconstruction of prior conversation / work (investigations, decisions, tool usage, errors, corrections, findings)
- Documents that preserve technical specificity and evidence when requested

## Excludes

- Code, scripts, or implementation artifacts
- Slides / presentations (`.pptx`)
- Spreadsheets (`.xlsx`, `.csv`)
- PDFs or Word documents (use the dedicated skills)
- Any artifact the user did not ask for simply because it seems more conventional or useful

## Core Principle

Write the document the user asked for. Respect the requested level of detail, recover relevant context, preserve required information, distinguish evidence from assumptions, and produce a Markdown file that matches the user's stated purpose, scope, structure, and constraints.

## Workflow (summary)

1. **Capture requirements** — purpose, audience, scope, detail level, structure, sources, language, inclusions/exclusions, output location.
2. **Clarify only when necessary** — ask a focused question only if critical ambiguity remains; explicit instructions take priority.
3. **Recover context** — reconstruct prior work / conversation when the document depends on it.
4. **Apply the requested style** — load the matching reference below.
5. **Organize around purpose** — choose structure that serves the document's goal without distorting meaning.
6. **Preserve specificity & evidence** — never invent tool calls, outputs, or sources; never sanitize history.
7. **Write the Markdown file** — filename and location follow user instructions and project conventions.

## References (load on demand)

- Full detailed guidelines (original specification) → `references/guidelines.md`
- Comprehensive style rules → `references/comprehensive.md`
- Concise style rules → `references/concise.md`

## Specialized document types

Some document types have their own skill that owns structure, evidence rules and artifacts, while this skill
keeps owning the prose. When the request matches one, load that skill first and apply this one to the writing:

| Request | Skill | What it adds |
|---|---|---|
| postmortem, incident report, RCA, bug write-up, "what went wrong" | [`postmortem`](../postmortem/SKILL.md) | 18-section template, file vs folder output, evidence levels V0–V5, blamelessness rules, artifact package with checksums |

## Final rule

Write the document the user asked for, not the document the agent would prefer to write.
