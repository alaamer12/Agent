---
name: readme-md
version: 1.1.0
author: Amr
specialized: none
description: 'Create, review, and update professional README files grounded in the actual project, never in assumptions or nonexistent features. Use when asked to write, fix, or refresh a README or project introduction. It inspects real sources (manifests, entry points, scripts, tests) before writing, separates implemented from planned, identifies the primary audience and picks a project-appropriate structure, asks the README voice/style (minimal / engineering / deep-DX / showcase / hybrid) with facts identical in any veoice, writes motivation without fabricated origin stories, uses only real commands verified against project config, refuses to fabricate badges/links/screenshots, offers motivation-phrasing options when positioning is open, asks only about intent-dependent decisions, and honestly reports what was tested vs reviewed. Preserves useful existing structure when updating; targeted edits; respects git state; draft mode. Triggers: readme, write/update the readme, README is outdated, document this project/repo.'

---

# readme-md — evidence-grounded project introductions

**The objective is not merely to write a README. It is to produce an
accurate, useful, project-specific introduction to the software.** Every
claim in the output must trace to evidence in the repository or from the
user. The README must adapt to the project's purpose, maturity, and
audience — not the project to a template.

## 1. Create or update — decide first

Inspect the project before choosing the mode.

- **No README** → create one from actual inspection. A missing README says
  nothing about what kind of project this is; find out from the files.
- **README exists** → review it against the current project (issue checklist
  in `references/review-checklists.md`), then fix. The existing README is
  evidence of *intent*, never proof that its instructions and features are
  still correct. **Targeted edits over rewrites** when targeted edits produce
  the better result; preserve useful organization and conventions unless
  changing them improves accuracy, navigation, or comprehension.
- **Verify before editing** against the real project — not the repo name,
  not an earlier summary, not the README itself.

## 2. Understand the project before writing

Investigate proportionally: a small utility needs a brief pass; a framework needs several modules, public
interfaces, and an execution path. Do **not** inspect every file - take the evidence needed to describe
accurately; the proportionate sweep is the Evidence sweep checklist in
`references/review-checklists.md`, which also carries how to apply the file safely (§11).

Two distinctions are mandatory — **what is actually implemented** (separate implemented / partial / planned /
experimental; never present planned as done; if status is uncertain and matters, investigate or qualify) and
**the primary audience** (several may exist; establish the sensible primary one and organize secondary
information around it — `references/structure-and-sections.md`).

## 2b. Voice and depth - ask once, then hold it

Voice is the project's stable personality; tone is that voice adapted to one reader and purpose. Different
README styles are **the same facts, re-ordered and re-registered** - never a license to change claims.
Before drafting, when the repo and the user's request don't already fix the register, ask the one question -
"which README do you want?" - with the five styles, their levers, trade-offs and voice-specific guardrails:
`references/voice-and-tone.md`. Skip the ask when an existing README's register, a docs-site split, or the
user's own words already answer it.

## 3. Identity and motivation

Open with what the project *is* and *why it matters*: name, category, the
problem, the intended users, the distinguishing capability — specific enough
that a reader never opens the repo. Never let the stack replace the purpose:
"a modern React/TypeScript/PostgreSQL application" names technologies and
explains nothing; technology belongs only where it supports the explanation.

Motivation statements must be true to the evidence: the problem, why it
matters, what existing approaches lack (*when supported*), what the project
improves. **Do not invent origin stories, market gaps, demand, or
limitations for persuasiveness.** If the repo doesn't establish motivation,
infer only what the implementation supports — and ask the user when their
real motivation matters but can't be established.

**Multiple motivation candidates:** when positioning is genuinely open,
propose 2–4 distinct-direction sentences (problem-solved / capability /
user-experience / engineering-exploration), briefly explain the difference,
let the user pick. Skip this when motivation is explicit or a finished
README was requested — and never offer wording-variations pretending to be
directions.

## 4. No generic AI writing

The README must sound written *for this project*. Forbidden: empty intro
statements; unsubstantiated innovation claims; "powerful / seamless /
robust / cutting-edge" without concrete meaning; vague scalability,
security, or performance claims; repetitive summaries that add nothing;
marketing filler; feature lists paraphrasing module names; template sections
that serve nothing; long explanations of the obvious. Prefer concrete
statements of actual behavior, capability, constraint, and intended use.
Professional documentation does not need promotion: clarity, specificity,
credibility.

## 5. Structure chosen from the project

Potential sections are a menu, never mandatory, and the reader-need priorities differ by project type
(library, end-user app, CLI, research). The menu, the per-audience ordering, the no-section-for-the
template's-sake rule and what never to fabricate for completeness:
`references/structure-and-sections.md`.

## 6. Feature accuracy

Describe meaningful capabilities from implementation evidence; prioritize
what readers can *accomplish*. Explain what each significant feature does
and why it's useful when relevant — never enumerate files/classes/modules
without their role. Distinguish features from internals: include architecture
where the audience needs it to evaluate, use, or contribute; deep internal
design belongs in dedicated docs, not the README entry point. Before
claiming a capability, establish it exists (implementation, tests, config) —
a dependency that could theoretically provide it is not support.

## 7. Commands, examples, and verification honesty

Install/usage instructions must match the actual project. Verify when
relevant: runtime versions, package manager and install commands, build/dev
server commands, env vars, config files, database/migration steps,
credentials, test commands, deployment. Evidence = the project's real
scripts, manifests, config, docs — **never invent a command because the
framework conventionally has it** (not every JS project uses the same
package manager or defines `dev`/`build`/`test`).

- Where practical, **run** what you document; where credentials/services
  block it, note the limitation instead of claiming a successful test —
  distinguish "reviewed as plausible" from "tested".
- Never force an install to succeed via unrelated project changes.
- Examples: minimal, real, consistent with the actual public interface; no
  nonexistent functions, endpoints, or options; mark every placeholder the
  reader must replace.

## 8. Stack, visuals, links, badges

- **Stack**: identify from manifests/config/implementation; separate core /
  dev / build / optional / external services / test-only. Don't dump
  dependencies for comprehensiveness; for complex systems a short
  architecture overview beats a package list. Invented rationale for a
  technology choice is forbidden — state its role or ask.
- **Visuals**: screenshots/diagrams/demos only when they materially help;
  verify every referenced asset exists at the stated path; never invent
  screenshots, logos, hosted URLs. A missing visual that would help:
  consider creating it only within the user's ask — never imply it exists.
- **Links/badges**: verify internal paths and anchors; never invent URLs;
  badges only when real (no fabricated build status, coverage, version,
  downloads). A README does not need badges to be professional.
- **Cross-document relationships**: when the repo has several doc files and
  the README's role among them is unclear *and material*, ask (primary
  explanation linking out? short entry point? existing nav preserved?). If
  conventions or the user already made it clear, don't ask.

## 9. Language and multilingual docs

Language comes from the user's instruction and the project's convention;
never assume every project needs multiple languages. Existing localized
structure: inspect and preserve. When multilingual need is unclear and
material, ask (single language / separate files / primary linking to
localized / project's own pattern). If multiple versions requested: same
substantive content across all, no drift in claims, and never translate
identifiers, commands, API names, or config keys into something incorrect.

## 10. Coordinate genuinely user-owned decisions

Ordinary documentation decisions are yours. Ask — concisely — only about
choices depending on intent, positioning, or established preference: actual
motivation; primary audience when evidence is split; the README voice/depth
(§2b) when nothing fixes it; desired emphasis;
whether to offer motivation options; language/multilingual structure;
cross-document relationships; other requirements the repo cannot establish.
**Never ask the user for facts you can reliably read from the project; never
interrupt for minor style calls a judgment resolves.** If the user already
gave the information, follow it without re-asking. Non-essential + sufficient
evidence → pick the reasonable default and proceed.

## 11. Apply the file safely

Inspect git state, confirm the intended path, preserve unrelated user modifications, and decide full
rewrite vs targeted edit on evidence; keep the Markdown integrity checks (heading hierarchy, closed fences,
relative paths, no duplicate sections) honest to the implementation. The pass list - and **draft mode**, when
the user wants the document and no repo changes - is in `references/review-checklists.md`
(§Applying the file safely).

## 12. Review, then report

Before declaring done, run the final review passes and completion criteria
in `references/review-checklists.md` (accuracy, clarity, structure,
completeness, verification honesty), fix in-scope issues found, and state
honestly what was tested vs reviewed vs blocked. Completeness is judged
against the README's purpose and audience — not its section count.
