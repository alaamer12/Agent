# Job A — Write a document

The full procedure for producing a Markdown document that does not exist yet. Self-sufficient: this file needs nothing else from the skill.

Create Markdown documents that fulfill the user's actual intent — not a preferred or conventional substitute. Respect the requested level of detail, recover relevant context, preserve required information, distinguish evidence from assumptions, and match the stated purpose, scope, structure, and constraints.

## Style (mode) references — load one

| Mode the user asks for | File |
|---|---|
| Normal (the default when no style is named) | `references/guidelines.md` |
| Comprehensive, full account, exhaustive | `references/comprehensive.md` |
| Concise, brief, summary-length prose | `references/concise.md` |

## Procedure

1. **Capture requirements** — purpose, audience, scope, detail level, structure, sources, language, inclusions/exclusions, output location.
2. **Clarify only when necessary** — one focused question, and only if critical ambiguity remains. Explicit instructions take priority.
3. **Recover context** — reconstruct the prior work or conversation the document depends on.
4. **Apply the requested style** — the mode table above; the user's named mode outranks the default.
5. **Organize around purpose** — the structure serves the document's goal without distorting meaning.
6. **Preserve specificity and evidence** — never invent tool calls, outputs, or sources; never sanitize the history.
7. **Write the file** — name and location follow the user's instructions and the project's conventions.

## Includes

- Documents whose purpose, audience, scope, structure and detail come from the user's request
- Comprehensive accounts, concise summaries, investigation histories, technical transcripts
- Reconstruction of prior conversation or work (investigations, decisions, tool usage, errors, corrections, findings)
- Documents that keep technical specificity and evidence when asked

## Excludes

- Code and scripts, slides, spreadsheets, PDF or Word output (dedicated skills)
- Any artifact the user did not ask for because it seems more conventional

## Specialized document types

Some types have their own skill owning structure, evidence rules and artifacts, while this job keeps owning the prose. When the request matches one, load that skill first and apply this job to the writing:

| Request | Skill | What it adds |
|---|---|---|
| postmortem, incident report, RCA, bug write-up, "what went wrong" | [`postmortem`](../../postmortem/SKILL.md) | 18-section template, file vs folder output, evidence levels V0–V5, blamelessness rules, artifact package with checksums |

## Final rule

Write the document the user asked for, not the one the agent would prefer to produce.
