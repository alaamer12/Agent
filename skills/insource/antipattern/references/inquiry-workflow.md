# Inquiry workflow (Mode C)

Use `/inquire` when neither the user nor the project defines which anti-patterns to document.

## Contents
- Before asking
- Prepare the candidates
- Question design
- Running the inquiry
- After the answers
- Selecting by editing a marked list
- If `/inquire` is unavailable

## Before asking

1. Locate the `/inquire` skill: check the available-skills list first, then common locations (`.claude/skills/inquire/SKILL.md`, `~/.claude/skills/inquire/SKILL.md`, `/mnt/skills/*/inquire/SKILL.md`).
2. Read its SKILL.md completely. Follow its real interface, limits, and report workflow. Do not assume a format from memory.
3. Finish the investigation first. Questions must rest on evidence, not generic preferences.

## Prepare the candidates

- Reduce findings to a short, ranked list (aim for 5 to 12), grouped by theme.
- Each candidate gets one line of project evidence and a confidence level.
- Remove anything the project already settles, and record it instead of asking:
  - A lint or type config already forbids it.
  - An ADR documents the trade-off as intentional.
  - The code shows a single clear answer (one library is used everywhere).
  - The anti-pattern is unambiguous and low-risk to document.
- Do not make the user decide what you can resolve from the code or docs.

## Question design

Prefer multiple choice, with multi-select wherever several answers can be true, and always leave room for free-text context. Typical questions:

| Purpose | Shape |
|---|---|
| Which findings become rules | Multi-select per theme; each option names the pattern and its evidence |
| Required versus optional | For the selected set, mark each Required or Recommended |
| Architectural concerns to include | Multi-select of layer/boundary concerns found |
| Constraints that change a recommendation | Multi-select plus free text (legacy modules, upcoming migration, compliance) |
| Ambiguous project intent | Single-select between the readings the evidence supports |

Rules of thumb: keep the set small (around six questions at most), keep options concrete and mutually distinct, describe each option in project terms (file, module, number), and include a "none of these / other" path. Examples: [../examples/inquiry-questions.md](../examples/inquiry-questions.md).

## Running the inquiry

1. Build the HTML report through `/inquire` using its documented workflow, with sections A to D from [documentation.md](documentation.md) filled from your evidence.
2. Present the questions in the way `/inquire` specifies.
3. Wait for the answers. Do not write the spec, edit project docs, or start any fix before they arrive.

## After the answers

1. Record the selections as section E: what was chosen, what was declined, and any free-text context.
2. Keep only selected recommendations. Apply the user's required/optional labels. Adjust rules for stated constraints.
3. Produce section F, the final specification, in the project's format (usually `ANTIPATTERN.md`, or the existing section). If `/inquire` can update its report with E and F, do that. Otherwise state the selections in your summary.
4. If an answer reveals a gap (user chose "other" with new scope), investigate that item before writing its rule.

## Selecting by editing a marked list

Some users would rather mark a list than answer questions. Same contract, different medium — and the marked list
lives **in chat or in scratch space outside the repository** (e.g. `/tmp/antipattern/candidates.md`), never as a
new file in the project, which the boundaries forbid.

- One bullet per candidate: `- [ ] **Name** (impact: High; confidence: High) — src/path.py:42-49 — one-line why`.
- Ask them to change the ones they want into `[-]` — a hyphen between the brackets — and state that unmarked items
  are not selected. Never preselect.
- Re-read the list after their reply. Treat only `[-]` as selected; `[ ]`, `[x]`, and `[X]` are not selections here.
- Match a selection by title plus evidence reference, not by line number alone. If an item was renamed, duplicated,
  or marked ambiguously, ask instead of guessing.
- No item marked → no rules written. Confirm nothing is needed rather than documenting assumed choices, and never
  read silence as approval.

## If `/inquire` is unavailable

Say so plainly in your reply instead of silently improvising. Then:
- Present the evidence-based candidates in chat with a numbered multi-select list and ask the user to reply with their picks and constraints.
- Write the report as one self-contained HTML file with sections A to F in the same order.
- Mention in the final summary that `/inquire` was not available and which parts were done manually.
