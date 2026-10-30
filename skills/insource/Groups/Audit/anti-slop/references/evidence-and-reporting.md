# Evidence contract and finding decisions

## Evidence fields

- **Structural:** source-backed signature, path, line/column, snippet, and detector limitation. Structural matches remain candidate evidence.
- **Visual:** rendered observation with screenshot or route, region, viewport, theme, state, and observable behavior.
- **Contextual:** task, user need, semantic role, design/brand decision, workflow, or other explanation that changes the interpretation.
- **Counterevidence:** visible or source-backed facts that weaken the candidate or support a legitimate use.
- **Coverage:** which routes/files/states were actually inspected and what was unavailable.

Do not replace one kind of evidence with another. A CSS match is not a screenshot; a screenshot is not proof of source implementation; a design document is not proof of runtime rendering.

## Status vocabulary

| Status | Use when | Minimum reporting |
| --- | --- | --- |
| `candidate` | A pattern signal is observed, but intent, harm, or scope is unresolved | Signal, evidence reference, missing check/context, next verification |
| `confirmed` | The defining condition and its material problem are demonstrated in this context | Direct evidence, specific impact, context checked, actionable fix |
| `false-positive` | A superficial match has an evidenced legitimate explanation | Match plus documented/rendered reason it is appropriate |
| `not-observed` | No signal appears in the reviewed scope | Coverage boundary; never imply unreviewed areas are clear |

Confidence is about evidence strength for the stated status, not severity or priority. Do not convert a low-confidence candidate to confirmed based on a numeric score or visual resemblance.

## Reconciliation table

| Structural pass | Visual/context pass | Synthesis |
| --- | --- | --- |
| Candidate | Confirms material harm | May confirm only when contextual checks support the conclusion; retain both trails |
| Candidate | Legitimate use / false positive | Report false-positive with the structural signal preserved and the reason stated |
| Candidate | Not observed or unavailable | Keep candidate/unresolved; inspect the right render/state or ask for context |
| No supported detector | Strong visual evidence | Keep visual finding; static detector absence does not veto it |
| No signal | No signal within reviewed scope | `not-observed` with scope limits, not a guarantee that the project is clean |

When scouts disagree, report the disagreement and its missing evidence. Do not silently let either modality overrule the other.

## Report shape

When JSON is requested, validate against `report.schema.json`. Every finding should include:

- stable `patternId`, catalog `name`, `status`, and `confidence`;
- separate `structuralEvidence` and `visualEvidence` arrays;
- a `contextualAssessment`, `exceptionsChecked`, and `counterevidence`;
- `recommendations`, `verification`, and an explicit unresolved-disagreement value when applicable.

The prose summary should state scope and coverage, prioritize material impacts, and distinguish a candidate from an actionable confirmed issue. Do not create unsupported accessibility claims: identify the relevant rendered condition and criterion or phrase it as a risk to verify.