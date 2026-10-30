# Documentation

## Contents
- Report structure (Mode C)
- Finding fields
- Impact and confidence
- Rule fields and quality bar
- The specification file
- Updating an existing document
- Modes A and B output

## Report structure (Mode C)

HTML, produced through `/inquire` using its documented workflow for layout and delivery. This table fixes content and order.

| Section | Content |
|---|---|
| A. Project overview | Purpose and domain, stack, architecture and layers, integrations and infrastructure, existing conventions and ADRs |
| B. Investigation methodology | Areas and levels inspected, tools with versions and commands, measurements, excluded paths, limitations, sources researched (title, link, one-line takeaway) |
| C. Findings and evidence | One entry per finding (fields below), ordered by consequence in this project, grouped by theme |
| D. Recommended anti-pattern rules | One entry per recommendation (rule fields below), with a proposed Level |
| E. User selections | Filled after the user answers: included, declined, required versus recommended, free-text constraints |
| F. Final anti-pattern specification | The agreed content in the `ANTIPATTERN.md` format, or the updated section of the existing document |

## Finding fields

Template: [../assets/finding.template.md](../assets/finding.template.md).

- Anti-pattern name
- Description of the problematic approach
- Affected files, functions, modules, layers or integrations
- Evidence: short code excerpts, metrics, references (label measured vs interpreted)
- Why it is problematic **in this project**
- Potential consequences
- Impact (severity) and confidence, rated separately

Keep excerpts short (a few lines). Point to the location for the rest. Never reproduce a secret value: for a
suspected credential, name its location and type and leave the value out of the report, the findings, and any web
search.

## Impact and confidence

Two different axes. **Impact** is what the pattern costs this project; **confidence** is how sure you are that it
is really there. Familiar or ugly code is not automatically high-impact, and a metric is not proof of consequence.

| Impact | Meaning |
|---|---|
| High | Correctness, security, data loss, or a cost a user or the business actually feels |
| Medium | Real maintenance or reliability drag, contained to a module or a slow path |
| Low | Local clarity or consistency; worth a rule, not worth an urgent fix |

| Confidence | Meaning |
|---|---|
| High | Directly observed in code or config, consistent across occurrences, consequence follows plainly |
| Medium | Observed, but intent or impact depends on context not fully verified |
| Low | Suggestive signal (a metric, a naming smell) that needs human judgment |

Always add what would raise or lower confidence. **Low-confidence items do not become findings or rules** — resolve
them, or keep them in the report as open questions the user can settle. A finding needs both a justified impact and
a justified confidence; say so even when the honest answer is "impact high, confidence medium".

## Rule fields and quality bar

Each rule has these fields. The validator `scripts/check_spec.py` checks them.

- **Avoid:** the behavior to stop.
- **Instead:** the behavior to follow.
- **Applies when:** the scope and conditions.
- **Why it matters:** the consequence in this project.
- **Exceptions:** valid exceptions and trade-offs.
- **Compliance check:** how to verify (a grep pattern, a linter rule, a review question, a test).
- **Example** (optional): a small before/after pair that shows the change, fenced as a diff or two short snippets.
  Include it when the rule is easy to state but easy to misapply — the pair settles the case a sentence cannot.
  Base it on the project's own code where possible; otherwise label it **illustrative** and do not claim it was
  applied. Keep it language-idiomatic, minimal, and free of unrelated cleanup. Do not put angle-bracket
  placeholders inside it; the validator reads them as unfinished text.
- **Level** (optional): `Required` or `Recommended`, when the user made that choice.

Quality bar:

| Weak | Strong |
|---|---|
| "Avoid overengineering." | "Do not add an interface or factory with a single implementation unless a second implementation or test double is needed in the same change." |
| "Handle errors properly." | "Outbound HTTP calls must set a timeout and map failures to the typed `IntegrationError`; never `except Exception: pass`." |
| "Don't duplicate code." | "Discount rules live only in `pricing.rules`. Do not re-implement thresholds elsewhere; call the shared function." |

A rule is good when another agent could apply it to a diff without asking questions, and a reviewer could check it.

## The specification file

Use [../assets/ANTIPATTERN.template.md](../assets/ANTIPATTERN.template.md). Layout: title, one-paragraph purpose, how agents use it, rules grouped by theme with IDs (`AP-001`, ...). Rules are imperative and short. Findings and long evidence stay in the report; the spec may link to it but must stand alone. A full sample is in [../examples/ANTIPATTERN.example.md](../examples/ANTIPATTERN.example.md).

## Updating an existing document

1. Follow the document's current format, heading style and ID scheme. Do not reformat or renumber.
2. Make minimal edits: add rules at the end of the relevant group, or amend a rule only when evidence shows it is wrong or unverifiable.
3. Never silently delete or weaken an existing rule. Raise it in your summary.
4. Do not create a second anti-pattern file beside an existing one.

## Modes A and B output

- The spec (new or updated) is the deliverable.
- In chat, give a short summary: what was investigated, key evidence, rules added or proposed, and anything left out of scope.
- Mode B: list violations of existing rules and proposed additions separately. Edit the document only with the
  user's agreement or request.
- **Zero findings is a result.** If the scope was inspected and nothing survived verification, say what was
  inspected, which candidates were checked and rejected (and why they were fine), and write no placeholder rules.
  A clean report is a deliverable, not a failure — inventing a finding to justify the run is.
