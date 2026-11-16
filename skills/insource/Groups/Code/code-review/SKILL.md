---
name: code-review
version: 1.0.2
author: Amr
specialized: none
description: 'Review the changes since a fixed point (commit, branch, tag, merge-base) on two separated axes run as parallel subagents and aggregated side by side, never cross-reranked: Standards (does the diff follow the repo''s documented rules plus a Fowler code-smell baseline that the repo always overrides, skipping what tooling enforces?) and Spec & Quality (is the spec faithfully implemented, judged on correctness, readability, architecture, security, performance?). Carries the Google gate: approve when it definitely improves code health, not perfection; severity labels (Critical/Required/Nit/Optional/FYI); tests reviewed first; change sizing ~100/300/1000 lines; named structural remedies instead of "this is complex"; dependency discipline; dead-code ask-before-delete; no-LGTM honesty rules; never accept "fix it later". Use before merging, evaluating agent-written code, or when asked "is this ready". Not for fixing bugs a review finds (dbug, fix), commit messages (commit), or full-repo security scans (security-scan).'
when_to_use: 'The user says review / is-this-ready / look at my diff, before any merge or PR, after a feature lands or an agent produced code, or after a bug fix when the regression test needs reviewing too.'
argument-hint: "[fixed point: commit | branch | tag | 'main']"
---

# code-review — two axes, one gate

The change under review is `git diff <fixed-point>...HEAD` (three-dot:
merge-base comparison) plus its commit list. Everything else follows
from two deliberate separations:

- **Standards axis**: does the diff conform to *this repo's* documented
  rules, with a portable smell baseline underneath that the repo always
  overrides → `references/smells.md`
- **Spec & Quality axis**: does the diff faithfully implement what was
  asked, and is what it implements good code on five axes (correctness,
  readability, architecture, security, performance) → `references/axes.md`

**Why two axes and no reranking**: code that follows every standard but
implements the wrong thing, and code that does exactly what was asked
but breaks the project's shape, are different failures. Reported
together, one masks the other; aggregated side by side, both stay
visible. Never pick a single winner across axes.

**The approval standard** (holds everywhere): approve a change that
*definitely improves overall code health*, even if imperfect. Perfect
code does not exist; do not block a change because it isn't how you
would have written it.

## The loop

1. **Pin the fixed point.** Whatever the user named (SHA, branch, tag,
   `main`). Ask if absent. Confirm it resolves
   (`git rev-parse <fp>`) and the diff is non-empty **here** — a bad ref
   should not fail inside two parallel subagents.
2. **Find the spec source**, in order: issue references in commit
   messages (`#123`, `Closes`, tracker syntax) → a path the user passed
   → a spec file under the project's docs/specs folders matching the
   branch or feature. Nothing found: ask; if there is genuinely no spec,
   the Spec subagent skips and reports *"no spec available"* — an
   honest absence, not a silent pass.
3. **Find the standards sources**: documented coding rules
   (`CODING_STANDARDS.md`, `CONTRIBUTING.md`, `AGENTS.md`, style
   configs' intent). The repo's word wins over the baseline; skip
   anything tooling already enforces — linting's job is not review's.
4. **Review.** For anything non-trivial, spawn both axes as **parallel
   subagents** so they don't pollute each other's context. Each prompt
   gets: the exact diff command + commit list, its own source material
   (standards files list **plus the smell baseline pasted in full** for
   Standards; the spec contents for Spec), the report brief, and the
   under-400-words cap. The briefs are written out in full in
   `references/axes.md` §Subagent briefs. Solo review of small diffs is
   fine — keep the same two headings either way.
5. **Aggregate.** Present under `## Standards` and `## Spec & Quality`,
   lightly cleaned, **not merged or reranked**. Every finding carries a
   severity label. End with one summary line: totals per axis and the
   worst issue *within each axis*. Template:
   `assets/review-report-template.md`.

## Severity labels — required vs optional, said visibly

| Label | Meaning | Author action |
|---|---|---|
| **Critical:** | blocks merge — vuln, data loss, broken function | must fix |
| *(no prefix)* | required change | must address before merge |
| **Nit:** | cosmetic, style preference | may ignore |
| **Consider:** / **Optional:** | worth weighing, not required | author decides |
| **FYI** | context, no action | none |

**Order by leverage**: correctness and security first, then structural
problems and missed simplifications, then everything else. If there is
one structural problem and ten nits, the structural problem *is* the
review — don't bury it.

## Deeper files — load per need

| Need | Read |
|---|---|
| the five axes' concrete checks, tests-first, verification, red flags, presumptive blockers | `references/axes.md` |
| the smell baseline (12 Fowler smells + binding rules) | `references/smells.md` |
| structural remedy for a named problem; change sizing/splitting; commit descriptions; dependency & dead-code rules | `references/remedies.md` |
| how to comment honestly; disagreement; speed; "fix later" refusals; multi-model review | `references/conduct.md` |
| the report skeleton | `assets/review-report-template.md` |
