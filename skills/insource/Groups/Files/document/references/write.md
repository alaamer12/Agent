# Job A — Write a document

The full procedure for producing a Markdown document that does not exist yet. Self-sufficient: this file needs nothing else from the skill.

Create Markdown documents that fulfill the user's actual intent — not a preferred or conventional substitute. Respect the requested level of detail, recover relevant context, preserve required information, distinguish evidence from inference, and match the stated purpose, scope, structure, and constraints.

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

## Genre children

Some document types have a genre child inside this skill owning structure, evidence rules and artifacts, while job A keeps owning the prose. When the request matches one, load that child and apply this job to the writing:

| Request | Child | What it adds |
|---|---|---|
| postmortem, incident report, RCA, bug write-up, "what went wrong" | [`postmortem`](../postmortem/SKILL.md) | 18-section template, file vs folder output, evidence levels V0–V5, blamelessness rules, artifact package with checksums |

## Living-Document Wording

- **Replace wrong living content directly.** In Draft [DR], a confirmed correction overwrites the outdated passage; do not preserve it inline as `retired`, `superseded`, or historical guidance.
- **Use ordinary references.** When content relocates, update the canonical text and link to it normally. Never add `Moved to`, `Moved from`, or a migration banner to a living document.
- **Label inference, not assumption.** Write `Inferred from <evidence>` when evidence supports a conclusion. Do not use `assume`, `assumed`, `Assumption`, or `Working assumption` as content labels.
- **Ask or use structured pending.** If a decision is missing, ask immediately; after explicit deferral use only `Pending (Drafting) — <question>. Blocks: <claims or paths>. Discovered: <step>. Close before: Draft [DR] completion.`
- **Keep history in its own home.** Preserve prior decisions only in an explicit ADR, changelog, or other historical record when the project uses one. Do not create tombstones in living docs.
- **Report the current state.** Say `updated`, `replaced`, `linked`, or `removed`; do not report living content as `moved` or `retired`.

## Living-document wording

- Replace wrong or outdated living content directly when the user asks for a fix or during Draft [DR]. Do not preserve it inline as a tombstone.
- Never write `Moved to`, `Moved from`, `retired`, `assume`, `assumed`, or `Assumption` as labels in living documents or completion reports.
- Use ordinary cross-references for relocated content: state the current owner and link it, without announcing a move.
- Write evidence-backed inference as `Inferred from <evidence>`, not as an assumption.
- For an unanswered drafting decision, ask immediately and use only the structured `Pending (Drafting)` marker after explicit deferral. Deferral opens the marker; it does not close the topic. Report drafting as incomplete until the marker is resolved.
- Preserve prior decisions only in a genuine historical record the project already owns; never create history inside living guidance.

## Final rule

Write the document the user asked for, not the one the agent would prefer to produce.
