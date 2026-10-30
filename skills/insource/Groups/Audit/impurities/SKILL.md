---
name: impurities
description: 'Project-wide defect discovery and remediation through self-designed iterations — never a fixed checklist. Assess the actual project (runtime, resources, dependencies, assets, build, CI, config, platforms), then design and run as many focused investigate-and-remediate iterations as its specific risks warrant: investigate, document findings with evidence, root-cause, fix preserving intended behavior, verify, commit traceably on an isolated branch. Core discipline — absence of an obvious reference is evidence to investigate, not proof of unused: build tooling, plugins, reflection, codegen, and CI consume what imports never show. Findings classified confirmed/suspected/optimization/unresolved, never beyond their evidence; the plan adapts mid-work; sub-agents take independent scopes, the parent owns integration. Completes on responsible coverage, not "defect-free". Use for hidden defects, waste, unsafe patterns, deep tech-debt sweeps. Triggers: impurities, defect hunt, find what''s wrong, deep cleanup.'
---

# impurities — evidence-driven project defect remediation

> Do not follow a fixed checklist blindly. Understand the project, determine
> where its impurities are likely to exist, design the iterations needed to
> investigate them, fix what the evidence establishes, and preserve a
> traceable record of every result.

A defect may originate anywhere: runtime behavior, memory/CPU/disk/network
lifecycle, concurrency, dependency configuration and compatibility, build
systems and tooling, assets and resource loading, config and environment
drift, platform specifics, component interactions. **These are examples, not
the plan** — the plan is derived from *this* project (§1). Candidate areas
and worked examples of how iterations get derived:
`references/investigation-areas.md`. Copyable report skeletons:
`assets/report-templates.md`.

## Core principles

1. **Project-wide, project-specific.** Never assume every project has the
   same problems; the assessment decides the investigation areas.
2. **Discover AND remediate.** The full cycle is investigate → document →
   root-cause → fix → verify → record/commit. A report of problems without
   action on the actionable ones is not this skill.
3. **Adaptive iterations.** No universal count, sequence, or minimum. The
   plan is revised mid-work on evidence — added, split, merged, reordered,
   revisited — with each change recorded and justified. No padding
   iterations to look comprehensive; no merging unrelated areas into one
   unreviewable iteration.
4. **Preserve intended behavior.** Removing defects ≠ removing implicit
   requirements. A pattern that looks unnecessary is not automatically an
   impurity — investigate its purpose before touching it (§2).
5. **Traceability.** Every iteration has its own findings and remediation
   reports, verification record, and identifiable commits. The final state
   must explain what changed, why, and how it was validated.

## 1. Assess before planning

Inspect proportionally (brief for a small library, extensive for a
multi-platform app): repository structure; languages/frameworks;
architecture; supported platforms/environments; dependency manifests +
lockfiles; build/packaging systems; CI workflows; dev/deploy scripts; asset
directories and resource-loading paths; existing tests and validation tools;
runtime entry points and lifecycle behavior; **git state and existing user
modifications**; documentation and known constraints. Do not plan a reliable
investigation on top of an assumed picture.

## 2. Explicit vs implicit requirements — the central discipline

Before declaring anything unused/unnecessary, inspect the mechanisms that
could consume it invisibly: direct imports · transitive dependency
requirements · build/bundler config · CI workflows · dev scripts · plugins
and extension mechanisms · reflection and dynamic loading · code generation
· runtime resource discovery · packaging requirements · platform-specific
integration · environment-dependent behavior.

The procedure, applied to every "looks unused" candidate:

1. Identify its **declared role** (manifest scope, package type, location).
2. Inspect the manifests, configs, scripts, and workflows around it.
3. Determine usage type: direct / indirect / build-time / dev-time / runtime.
4. Check whether its function is provided elsewhere.
5. Verify the consequences of removing or changing it.
6. Change it only once role and removal-safety are **established**.

> **Absence of an obvious reference is evidence to investigate, not proof
> that something is unused.**

(The `packages` skill is the deep version of exactly this for dependency
graphs — a dependency-integrity iteration may delegate to it.)

## 3. Design the iterations

Group related risks into focused cycles. Each iteration is defined by:
**objective** (impurity type sought) · **scope** (components/behaviors) ·
**investigation strategy** · **expected evidence** (what would establish a
finding) · **remediation approach** · **verification strategy** ·
**dependencies** (prereqs, ordering). Choose iteration count from project
size, subsystem count, platform/language diversity, runtime complexity,
dependency/tooling sprawl, discovered categories, expected depth, and time
— with earlier findings feeding later design (a memory investigation that
lands in asset loading justifies its own follow-up).

## 4. Findings → remediation → verification → record

**Findings report first, fixes second.** Each finding: id, description,
affected components/files, observed behavior, root cause (if established),
conditions, impact/severity, supporting evidence, confidence, recommended
remediation — classified honestly as **confirmed defect / suspected
defect / optimization opportunity / unresolved question**. Speculative
issues are never presented as confirmed bugs; working code is never
destabilized to inflate a report.

**Remediation** prefers: underlying-cause correction, preserved behavior,
architecture fit, minimal unrelated change, no unneeded dependencies,
maintainability, works across supported environments, regression protection.
Shared root causes get one coherent fix, not scattered workarounds. Broad
refactoring only when required to correct or prevent the issue.

**Verification** matched to the finding: tests, static analysis, build/
packaging checks, runtime reproduction, profiling and resource measurement
(baseline *before* a perf change, compare after), stress/repeat/concurrency
tests, dependency/config validation, asset/path checks, per-platform. Not
every method for every issue; when a problem can't be reproduced or the
environment is unavailable, document the limitation instead of claiming
complete verification.

**Final state per finding** (in the remediation report): fixed-and-verified ·
fixed-incompletely-verified · investigated-not-reproducible ·
confirmed-unresolved · deferred (scope/authorization) · determined-not-a-defect
— with reason and evidence.

Reports live in the project's convention if one exists, else the example
layout (`impurities/iteration-NN/{findings,remediation}.md + summary.md`)
from `assets/report-templates.md` — concise enough to review, complete
enough to understand the work.

## 5. Git isolation and history

- **Branch:** all remediation work isolated from the original working branch.
  Inspect current repo state first; preserve user changes; never overwrite
  unrelated work.
- **Commits:** identifiable per iteration (and per sub-agent scope where
  sensible) so history answers *which iteration, which area, what fixed,
  how it relates to findings*. Separate commits for independent fixes when
  review gains from it. Messages describe the actual change
  (`fix: prevent repeated resource allocation`, `fix: repair missing theme asset`).
- **Parallel work:** isolated worktrees (or equivalent safe workflow) so
  concurrent agents cannot overwrite each other; explicit integration
  commits; re-run relevant verification after merging — parallel execution
  never waives integration testing.
- **Commit safety:** no unrelated user changes included · no rewriting
  shared history without authorization · no force-push without
  authorization · a commit's existence is not proof it was verified ·
  reports stay consistent with the real history.

## 6. Sub-agent orchestration

Delegation expands coverage or cuts time; it is not mandatory. Give each
sub-agent a focused brief (the `subagent` skill's shape): exact scope,
investigation objective, relevant context, expected findings/remediation
reports, shared-file rules, verification and commit requirements. A
sub-agent never redesigns the overall plan unless explicitly told to.
**The parent owns** strategy, iteration boundaries, conflict resolution, and
integration: dedupe findings, resolve overlapping responsibilities,
coordinate shared-file edits, review fix quality, validate change-to-change
interactions, keep reports and commits truthful.

## 7. Prioritize; hold scope

Order by severity, likelihood, affected functionality, resource impact,
data/security stakes, platform coverage, confidence, fix risk, and
verification cost — stability/correctness/resource-lifecycle defects first,
low-impact cleanup after. Stay within the user's objective: no infinite
chase of theoretical perfection; when time/resources/scope run short,
prioritize and **document what remains**. Unrelated improvements get
recorded, not started — unless they materially affect correctness,
security, maintainability, or completion.

## 8. Safety constraints — non-negotiable

Never: delete possibly-required deps/assets without sufficient investigation ·
remove functionality to silence a failing test · silently change intended
product behavior · weaken validation to hide failures · suppress errors
without understanding them · invent runtime evidence · do unrelated
architectural rewrites · add a dependency without justified need · assume
unusual code is defective · assume every "optimization" helps · overwrite
user modifications · claim the project is defect-free.

When a correction needs a consequential product decision, a destructive
action, or missing authorization: **stop that action, ask, continue the
independent work** meanwhile.

## Completion — responsible coverage, not perfection

Done when: assessed · project-specific plan executed · findings documented ·
actionable defects addressed in scope · verification performed appropriately ·
changes committed and traceable · reports truthful · remaining findings and
limitations identified · final summary reflects the actual state. Completion
never means "no other defect could exist" — it means the planned work was
carried out responsibly and the remaining uncertainty is reported honestly.
