# Gates Architecture Pillar

## 1. Overview & Philosophy

Every project already has hundreds of rules. They live in architecture documents, style guides,
`AGENTS.md`, review checklists, and the memory of the person who last fixed the incident. The
failure is rarely that a rule is unknown. It is that the rule is **optional in practice**: it
competes with a deadline, a model's habit, a warning nobody reads, and a gate that can be edited
by the change it is supposed to reject.

A gate is the part of the architecture that makes a rule non-optional. It is a checkpoint at a
boundary — commit, pull request, merge, release, deploy — that observes an artifact and returns a
binary decision. The rule says what must be true. The gate says who finds out, when, at what cost,
and what happens when it is false.

Left undesigned, enforcement decays into six familiar shapes:

- a repository with 400 type errors where everyone has learned to ignore the output;
- a 90-second pre-commit hook that the team bypasses with `--no-verify`;
- a scanner that exits 0 on findings, wired into a pipeline that only reads the exit code;
- a gate that passes because the report file was never produced;
- a baseline that was generated once and has never shrunk;
- an agent that "fixes" a red gate by editing the check, deleting the test, or adding `any`.

Each is an enforcement design failure, not a discipline failure. This pillar decides the
enforcement ladder, the tier boundaries and budgets, the gate register, the failure and exception
policy, and the evidence that each gate exists and works.

The pillar's doctrine:

- **A rule without a gate is a preference.** Documents and prompts are instructions, and
  instructions are non-deterministic: they work until attention, context, or time runs out. A gate
  is deterministic or it is not a gate. Both are useful; only one is enforcement.
- **Every gate answers four questions.** Which rule, at which boundary, at what cost, with what
  evidence and escape hatch. A gate that cannot answer all four is a script someone runs sometimes.
- **The blocking list is short and absolute.** Five checks that always block beat twenty that
  sometimes warn. Every additional blocking check spends trust; spend it on the failures that
  actually reach production.
- **Enforce at the earliest rung that can see the fact completely.** Types before lint, lint before
  a custom check, a custom check before a test, a test before review. Climbing higher than necessary
  pays human attention for a mechanical fact; staying lower than necessary leaves an escape hatch.
- **Gate on risk, not counts.** Severity, exploitability, reachability, and blast radius decide what
  blocks. A gate that blocks on "any medium finding in any transitive dependency" is overridden
  within a week.
- **Fail closed.** A missing report, a crashed scanner, a timeout, a skipped job, or an empty file
  scope is a failure, not a pass. The only safe default at a boundary is "no".
- **Protect the gate from the gated.** Check definitions, pipeline configuration, baselines,
  fixtures, and thresholds live behind stricter review than the code they judge. An agent asked to
  make the build pass will make the build pass; if it can edit the check, that is a legitimate path
  to the goal as stated.
- **Baseline debt, ratchet new code.** Legacy violations get a recorded baseline with an owner, a
  count, and a reduction schedule. New violations fail immediately. A baseline that never shrinks is
  a deleted rule with extra steps.
- **A gate that has never been observed failing is presumed broken.** Configure it, inject a
  known violation, watch it go red for the right reason with the right message, then revert. Repeat
  after every change to the check, its scope, its tool, or its tier.
- **Deterministic beats instructional, especially for agents.** A prompt asks; a hook and a CI job
  decide. Put the non-negotiables in the deterministic layer and keep the prompt for intent.
- **Budgets are contracts.** Hooks above roughly 10–15 seconds get bypassed; a gate that takes
  forty minutes teaches people to batch changes. Measure p95, publish the budget, and move a check
  down a tier rather than letting it silently blow the budget.
- **Exceptions are data, not habits.** Every exception carries a reason, an owner, a ticket, a
  compensating control, and an expiry. An exception without an expiry is a permanent policy change
  nobody voted for.
- **The register is the architecture.** A binding rule that names no gate, no tier, no owner, and no
  evidence is advisory whether or not anyone admits it.

Boundary map. Every other pillar states the rule; this pillar states where it is enforced. `language`
owns types and compiler flags — the first rung. `error` owns failure payloads — runtime guards and
gate messages use them. `testing` owns test design and conformance tests — this pillar owns where
they run, what failing means, and how long they may take. `db` owns schema and constraints — this
pillar gates migrations and destructive changes. `plugin` owns the extension contract — this pillar
gates the Open/Closed growth check. `cross-platform` owns platform seams — this pillar gates the
shared-code rules. `media` owns asset policy — this pillar gates brand-mark sourcing and byte
budgets. `ui`, `accessibility`, and `display` own their contracts — this pillar gates CLS, contrast,
RTL, and locale rules that can be measured. This pillar owns the enforcement ladder, the tier
budgets, the register, the fail-closed policy, the baseline and exception machinery, and the
evidence trail — nothing else.

## 2. What a Gate Is — and What It Is Not

The vocabulary matters because the three mechanisms fail differently.

| Mechanism | Question it answers | Where it lives | Fails by |
|---|---|---|---|
| **Guard** | May this operation proceed with this input or state? | in the code path, at the point of use | throwing or returning early; a missing guard is a runtime bug |
| **Gate** | May this change cross this boundary? | outside the artifact: hook, CI, merge queue, release job | blocking or passing a change; a missing gate is a process bug |
| **Sentinel** | What state is the system in? | telemetry, health checks, canaries | alerting or staying silent; a missing sentinel is a detection bug |

A guard clause protects a function; an auth guard protects a route; a gate protects a boundary; a
sentinel reports. A gate may run a runtime check, but a runtime check is not a gate unless it
decides passage at a boundary. A dashboard is not a gate, because nobody decides when it turns red.

A gate has three properties. It runs **automatically** on every change it claims to cover. Its
result is **binary**. And when it says no, the change **does not merge** through a cheap override
that a busy person can take at four on a Friday. That third property is the one teams get wrong: a
check with an override is overridden precisely when pressure is highest, which is when the gate
mattered most. If a gate genuinely must be bypassable, the bypass requires a second person and
leaves a record.

Every gate card answers four questions:

| Question | A weak answer | What it costs |
|---|---|---|
| **Which rule?** | "clean code", "use the design system" | nothing testable, so nothing can fail for the right reason |
| **Which boundary?** | "somewhere in CI" | feedback arrives after the change is expensive to fix |
| **What cost?** | unmeasured | the gate is bypassed, or the pipeline becomes the bottleneck |
| **What evidence and escape?** | "we will see if it fires" | a gate that has never failed, or an escape that has become a habit |

## 3. Directory Structure & Assets

```text
gates/
├── method.md                                            # this file — doctrine, workflow, DoD
├── assets/templates/
│   └── gates-architecture-template.md                   # binding document skeleton
├── references/
│   ├── enforcement-ladder.md                            # types → lint → contract check → test → runtime → review
│   ├── gate-tiers-and-budgets.md                        # T0–T4, latency budgets, incrementality, fail-closed
│   ├── writing-a-gate.md                                # gate card, detection, report contract, evidence, protection
│   ├── baselines-ratchets-and-exceptions.md             # legacy debt, violation identity, suppression syntax
│   ├── gates-for-agent-written-code.md                  # deterministic enforcement, temptations, token economics
│   ├── inventory-and-governance.md                      # register, census, metrics, incident loop, deprecation
│   └── discovery-interview.md                           # targeted questions + the decision each drives
└── examples/
    └── gates-walkthrough.md                             # one pass: classify, tier, card, baseline, agent loop
```

## 4. Workflow

1. **Recon (read first, never ask what the repo answers).** Inventory the binding rules in the
   architecture docs and `AGENTS.md`; every CI workflow and hook; the checks that already exist and
   the ones that are configured but never run; the suppression count and the baseline files; the
   bypass paths (`--no-verify`, `continue-on-error`, an editable config); recent commits where an
   agent touched a check, test, or threshold; and the last few incidents. Count the rules with no
   gate and the gates with no owner.
2. **Interview** ([references/discovery-interview.md](references/discovery-interview.md)): ask only
   what the code cannot answer — which failures are unacceptable, who may accept risk, which
   environments are hermetic, what the merge budget is, and which rules are taste rather than
   contract.
3. **Classify every rule on the ladder,** reading
   [enforcement-ladder.md](references/enforcement-ladder.md). Name the earliest rung that can see
   the fact completely, and the escape hatch that would defeat it.
4. **Tier every check,** reading
   [gate-tiers-and-budgets.md](references/gate-tiers-and-budgets.md). Assign T0–T4, a scope, a p95
   budget, a blocking status, and a command.
5. **Write one gate card per gate,** reading
   [writing-a-gate.md](references/writing-a-gate.md). The card is the unit of review: rule,
   boundary, cost, evidence, exception, owner.
6. **Baseline the legacy and define the ratchet,** reading
   [baselines-ratchets-and-exceptions.md](references/baselines-ratchets-and-exceptions.md). Decide
   suppression syntax, exception approval, and the reduction schedule before the gate starts
   blocking.
7. **Make each gate fail on purpose.** Inject the canary violation, confirm the right rule fires
   with the right file, line, and message, then revert and confirm green. Record the date and method
   in the register. A gate nobody has watched fail is a gate nobody has built.
8. **Wire, protect, and govern.** Put the checks in the pipeline from a protected configuration,
   protect the check definitions and baselines, write the agent contract
   ([gates-for-agent-written-code.md](references/gates-for-agent-written-code.md)), and start the
   register and review cadence
   ([inventory-and-governance.md](references/inventory-and-governance.md)).

## 5. The Enforcement Ladder (summary)

| Rung | Mechanism | What it can see | Relative cost | Typical use |
|---|---|---|---|---|
| **0** | Type system | values and states the language can distinguish | cheapest at authoring time | illegal states, exhaustiveness, branded ids |
| **1** | Compiler flags and lint | syntax, AST shape, imports, unused names | seconds | zero warnings, no `any`, no raw `<button>` where lint can see it |
| **2** | Project contract check | project-specific patterns, tokens, component names, boundaries, whole-repo text | seconds | raw colors, forbidden primitives, import direction, Unicode icons in docs |
| **3** | Conformance test | cross-file facts, catalogs, counts, executable documentation | seconds–minutes | every route has a page, every table has a reference row, docs match code |
| **4** | Runtime guard | the values that actually arrive in production | request time | schema validation, permission checks, invariant assertions |
| **5** | Review | judgment, taste, architecture, intent | minutes–hours | naming, abstraction, "is this the right feature" |

Rules that make the ladder useful:

- **Earliest complete rung wins.** A regex cannot understand types; a type cannot see a design
  token; a unit test cannot prove a catalog is complete; review cannot reliably check 400 files.
- **A lower rung that can be escaped needs a higher rung for the escape, not for the rule.** `any`
  defeats the type system; a file-level disable defeats lint; a generated file defeats a source
  scan; a doc outside the linter's include defeats a "no Unicode icons" rule. Gate the escape.
- **Use two rungs for the important things:** a fast local check for the author (T0/T1) and an
  authoritative full check at the boundary (T2/T3). The local check is a courtesy; the boundary
  check is the gate.
- **Review is the last rung, never the first.** Spending review on a mechanical fact is how teams
  run out of review before they reach the judgment that only a person can supply.

Details, decision table, and worked examples:
[enforcement-ladder.md](references/enforcement-ladder.md).

## 6. The Tier Table (summary)

| Tier | Trigger | Scope | Budget (p95) | Blocks? | Typical checks |
|---|---|---|---|---|---|
| **T0** | save / keystroke | current file | < 2 s | no | types, lint, format |
| **T1** | commit | staged files | ≤ 10–15 s | yes, audited bypass | format, staged lint, secret scan, fast contract checks |
| **T2** | push / pull request | full repo + diff | ≤ 5 min | yes | build, typecheck, full lint, unit, contract, conformance, dependency diff, SAST |
| **T3** | merge queue / required checks | full + integration | ≤ 20–30 min | yes | integration, e2e smoke, migration/destructive change, a11y/visual, coverage ratchet, bundle budget |
| **T4** | nightly / release | full | hours | release | full e2e, mutation, full-repo census, dependency audit, performance budgets, restore drill |

The budget numbers are defaults, not laws: they come from the point where people start working
around the gate. A pre-commit hook that exceeds roughly 10–15 seconds is bypassed or disabled; a
merge gate that takes forty minutes teaches people to batch changes, which makes every failure
harder to attribute. Measure the real p95 and publish it. Full tier mechanics, incrementality,
cache keys, exit-code semantics, flake policy, and a worked budget:
[gate-tiers-and-budgets.md](references/gate-tiers-and-budgets.md).

## 7. The Gate Register

The register is this pillar's primary artifact. One row per gate; one owner; one evidence date.

| Field | Meaning |
|---|---|
| `id` | Stable name used in reports, suppressions, and the doc (`design/no-raw-color`). |
| `rule` | One testable sentence, with a counterexample if the boundary is unclear. |
| `source` | The binding document section or the incident that justifies it. |
| `rung` | 0–5 from the enforcement ladder. |
| `tier` | T0–T4. |
| `command` | The exact command that runs the gate. |
| `scope` | Files and exclusions; generated and vendor code named explicitly. |
| `budget` | p95 duration and the measured date. |
| `failure` | Block, warn, or report; and what a tool error means. |
| `exception` | The suppression syntax, who approves, where it is recorded, expiry. |
| `owner` | One role accountable for signal quality and review. |
| `evidence` | The date the gate was last observed failing, and how. |
| `reviewed` | The date of the last signal-quality review. |
| `status` | Active, advisory, or deprecated (with replacement). |

The register is also the census. If a binding rule from any architecture document does not appear
here — as an active gate or as an explicit advisory row — the rule is not enforced. The meta-gate
that checks this is described in
[inventory-and-governance.md](references/inventory-and-governance.md).

## 8. Anti-patterns (the easy paths, each observed in real pipelines)

| The shortcut | The documented cost |
|---|---|
| "It is documented, so people will follow it" | a preference with good typography; the first busy week deletes it |
| Blocking on 400 legacy findings | the gate is bypassed, disabled, or ignored; the baseline exists to prevent exactly this |
| A pre-commit hook that takes 90 seconds | `--no-verify` becomes the workflow; the gate now protects nothing |
| A scanner that exits 0 on findings | a cosmetic gate; the pipeline is green and the product is not |
| Treating a missing report as a pass | fail-open; the gate is strongest when the tool is broken |
| Letting the change edit its own check | self-certification; the agent or author will take the shortest path to green |
| Auto-refreshing the baseline on every run | debt laundering; the ratchet never ratchets |
| Blocking on warnings | warning fatigue; one study found 35–91% of static-analysis warnings non-actionable, and people learn to ignore the rest |
| Retrying a flaky check to green | the dashboard improves, the signal dies; a flaky gate is a broken gate |
| Using coverage as a blocking gate | it measures compliance with the coverage gate, not correctness |
| Running the same check at five tiers | cost without signal; one authoritative tier plus one fast local tier is enough |
| A dashboard nobody must read | a report, not a gate; no decision is attached |
| An exception without an expiry | a permanent policy change nobody approved |
| A gate with no owner | an orphan; it rots silently and is deleted in the next cleanup |
| A gate that has never failed | presumed broken; nobody knows whether it can fire |
| One giant regex over the whole repo | false positives, no context, and a suppression habit |
| Formatting enforced as a blocking check | an argument that a formatter should have ended automatically |

## 9. Core Invariants

1. **A rule without a gate is a preference.** Every binding rule names its gate, tier, owner, and
   evidence, or is explicitly marked advisory with a reason.
2. **The blocking list is short and absolute.** Each blocking gate runs automatically, returns a
   binary result, and cannot be overridden by the author alone.
3. **Enforce at the earliest rung that can see the fact completely.** Gate the escape hatch when a
   lower rung can be bypassed.
4. **Fail closed.** Missing, crashed, timed-out, skipped, or empty-scope means failed — or an
   explicit, recorded waiver, never a silent pass.
5. **A gate the gated can edit is not a gate.** Check definitions, configuration, baselines,
   fixtures, and thresholds are protected paths with human approval.
6. **Every gate is observed failing before it is trusted.** Keep a canary fixture and a date; repeat
   the observation after any change to the gate.
7. **New code ratchets; legacy debt is baselined with an expiry.** A baseline without a reduction
   schedule is a deleted rule.
8. **Exceptions are data.** Reason, owner, ticket, compensating control, expiry — or the exception is
   a habit.
9. **Budgets are contracts.** A check that exceeds its tier budget moves tier or shrinks scope; it
   does not silently slow the boundary.
10. **The register is the census.** A gate with no rule, a rule with no gate, an ownerless gate, and
    an expired exception are all findings, not background noise.

## 10. Definition of Done

`gates-architecture.md` exists and names: the enforcement ladder with the rung chosen per rule
class; the tier table with commands, scopes, p95 budgets, and blocking status; the gate register
with one row per rule and an owner; the baseline and ratchet policy with violation identity; the
suppression syntax and exception approval path; the fail-closed and exit-code contract; the agent
contract (what it must run, what it may not edit, how it proves completion); the bypass policy
(who, how, record, expiry); the evidence that each gate has been observed failing; the census that
ties every binding rule to a gate or to advisory; the metrics and review cadence; and open
decisions listed — never defaulted silently. Shared gate units (checks, runners, fixtures, report
schemas) are registered in UNITS.md; sync points between this document and the CI configuration are
declared with their same-change duty.

## 11. Sources & Further Reading

The doctrine in this pillar was checked against these sources in November 2026. Links and numbers
age; re-check before quoting a figure in a generated document.

- **OWASP DevSecOps Guideline — Security Gates.** Risk-based thresholds, baselines, fail-closed
  reports, exception registers with expiry, the exit-code trap, and phased rollout.
  <https://owasp.github.io/DevSecOpsGuideline/2-Process/2-3-Build/2-3-5-Security-Gates/>
- **OWASP — Pre-commit.** The 10–15 second hook budget and the bypass failure mode.
  <https://github.com/OWASP/DevSecOpsGuideline/blob/master/current-version/2-Process/2-2-Develop/2-2-1-Pre-commit/2-2-1-1-Pre-commit.md>
- **Reveneau — The quality gates that should block a merge.** The three properties of a gate, the
  five blocking checks, protected gate definitions, bypass by a second person, and flaky = broken.
  <https://reveneau.com/guides/ai-native-delivery/quality-gates-that-block-a-merge>
- **Ford, Parsons, Kua, and Sadalage — Building Evolutionary Architectures / fitness functions.**
  The objective, automated measure of an architectural characteristic, and phase-appropriate
  strictness. <https://evolutionaryarchitecture.com/> ·
  <https://www.infoq.com/articles/fitness-functions-architecture/>
- **Anthropic — Claude Code best practices.** Deterministic hooks versus instructional prompts, the
  completion-check pattern, and the Stop hook's blocking exit code.
  <https://code.claude.com/docs/en/best-practices>
- **Heckman and Williams; the 2025 Scientific Data dataset.** The 35–91% non-actionable warning
  range, and the case for error-or-nothing over tolerated warnings.
  <https://www.nature.com/articles/s41597-025-06154-7>
- **ContextQA — AI coding agent quality gates.** The independent rerun, evidence, human approval
  for money/auth/migrations, and tested rollback.
  <https://contextqa.com/blog/ai-coding-agent-quality-gates-how-to-stop-agents-shipping-regressions>
- **Amr — What Are Guards in Programming?** The guard/gate/sentinel vocabulary (companion article,
  2026; no stable public URL at the time of writing).
- **chekr** — the author's local reference implementation of the rung-2 contract checker: report
  contract, selector-scoped suppressions, content-hash cache, and large-diff escalation. See
  [writing-a-gate.md](references/writing-a-gate.md) §11.
