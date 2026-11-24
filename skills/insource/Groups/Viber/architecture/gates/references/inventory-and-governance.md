# Inventory and Governance

A gate is infrastructure. Infrastructure needs an owner, a register, a review date, and a
decommissioning path. Without them, gates accumulate: some are duplicates, some have not run since
the CI migration, some block a rule nobody remembers, and one is still guarding a module that was
deleted. The inventory is how the enforcement layer stays small enough to trust.

## 1. The Register

One row per rule. The register is the single source of truth for "what is enforced, where, by whom,
and how do we know it works."

| Field | Meaning | Required |
|---|---|---|
| `id` | stable rule id used in reports, suppressions, and docs | yes |
| `rule` | one testable sentence | yes |
| `source` | doc section or incident that justifies it | yes |
| `status` | `active`, `advisory`, `deprecated` | yes |
| `rung` | 0–5 from the enforcement ladder | active only |
| `tier` | T0–T4 | active only |
| `command` | the exact command that runs it | active only |
| `scope` | files and exclusions | active only |
| `budget` | p95 duration and measurement date | active only |
| `failure` | block / warn / report; tool-error behavior | active only |
| `exception` | suppression syntax, approver, register path | active only |
| `owner` | one role accountable | yes |
| `evidence` | date last observed failing, and how | active only |
| `reviewed` | date of the last signal-quality review | yes |
| `replacement` | the gate that supersedes this one | deprecated only |

Example rows:

| id | rule | rung | tier | command | failure | owner | evidence |
|---|---|---|---|---|---|---|---|
| `design/no-raw-color` | no literal color outside `tokens/**` | 2 | T1/T2 | `bun run gates:colors` | block | design-system | 2026-11-18 |
| `ui/no-raw-button` | no raw `<button>` outside the primitive module | 2 | T1/T2 | `bun run gates:primitives` | block | design-system | 2026-11-18 |
| `repo/no-unicode-icons` | no emoji in any tracked text file | 2 | T2 | `bun run gates:icons` | block | docs | 2026-11-20 |
| `app/render-health` | every route renders with zero console errors | 3 | T3 | `bun run test:e2e:smoke` | block | web | 2026-11-19 |
| `types/no-new-any` | no new `any` or `@ts-ignore` | 1 | T2 | `bun run gates:types` | block (ratchet) | platform | 2026-11-17 |
| `tests/full-seed` | every required table is seeded before e2e | 3 | T3 | `bun run test:seed:check` | block | qa | 2026-11-19 |
| `ux/filter-ownership` | every widget reads the filter store | 3 | T3 | `bun run test:conformance:filters` | block | web | 2026-11-15 |
| `ux/micro-interactions` | transitions, RTL skeletons, modal depth | — | — | — | advisory | design | 2026-11-10 |

The advisory row is not a failure. It is the honest classification of a rule that cannot be
measured objectively; it still has an owner and a review date.

## 2. The Census Meta-Gate

The crown gate is a check on the register itself. It enforces the pillar's first invariant: every
binding rule names a gate or is explicitly advisory.

Recommended shape:

```text
gates/rules.yaml            # the manifest: one entry per rule id
docs/architecture/*.md      # binding rules link to ids: `[design/no-raw-color]`
gates/register.md           # the human table, generated or checked against the manifest
```

The census check asserts:

1. Every manifest entry has `status`, `owner`, and `reviewed`.
2. Every `active` entry has `rung`, `tier`, `command`, `scope`, `budget`, `failure`, `exception`,
   and `evidence`.
3. Every `advisory` entry has a reason and a review date.
4. Every `deprecated` entry has a replacement or a written "no replacement" reason.
5. Every rule id referenced in the architecture docs exists in the manifest.
6. Every manifest entry is referenced by at least one doc section (or by an incident record).
7. No duplicate ids; no empty commands; no gate that is not in a pipeline unless it is marked
   manual with a reason.
8. Every active gate's evidence date is newer than its last change.

The check itself has a sanity floor: if it discovers zero rules or zero docs, it fails. A census
that passes over an empty scan is worse than no census.

## 3. Orphan Hunt

Run these queries monthly. Each one is a finding with an owner, not a cleanup ticket nobody reads.

| Query | What it means |
|---|---|
| Rules in the docs with no register row | unenforced binding rule (or a doc that should be advisory) |
| Active gates with no command or no CI job | a gate that exists only in the register |
| Gates with no observed failure since the last change | unverified gate; run the canary |
| Gates with zero findings in 90 days | either a solved problem or a rule that never fires; investigate |
| Gates with a suppression rate above the threshold | the rule, the code, or the exception process is wrong |
| Gates slower than their budget | move tier or shrink scope |
| Gates with no owner or a departed owner | orphan; assign or deprecate |
| Baseline entries with no owner/ticket | debt with no plan |
| Exceptions past expiry | policy that renewed itself |
| Baselines that have not shrunk | ratchet not ratcheting |
| Duplicate gates for one rule | cost without signal; keep the authoritative one |

## 4. Ownership

One named role per gate, not a team alias nobody reads. The owner is accountable for:

- **Signal quality:** sampling false positives, tuning scope, and deciding when the rule is wrong.
- **Budget:** the p95 stays inside the tier; the scope stays honest.
- **Failure response:** a red gate is triaged, not muted.
- **Evidence:** the canary is current after every change.
- **Review:** the row is reviewed on the schedule, not when it breaks.
- **Deprecation:** the gate is removed with a replacement when the rule retires.

The owner may delegate the work; the accountability does not move. A gate with no owner is
deprecated by default at the next review.

## 5. Metrics

Measure the gate, not the team. The point is to tune the system, never to rank people.

| Metric | Question | Healthy |
|---|---|---|
| p50 / p95 duration | does it fit the tier? | p95 under budget |
| violation count | is the rule firing on real code? | stable or down |
| false-positive sample | is the signal trusted? | near zero at blocking tier |
| suppression count | are people working around it? | flat or down |
| exception count and age | is risk acceptance temporary? | small and young |
| bypass count | is the gate too slow or noisy? | zero, or each reviewed |
| baseline trend | is the debt shrinking? | down to target |
| flake rate | is the gate reliable? | zero at blocking tier |
| time-to-fix | is the feedback actionable? | days |
| evidence freshness | is the gate still verified? | newer than the last change |
| rule coverage | how many binding rules have a gate? | 100% or explicit advisory |

Vanity metrics to avoid: number of rules, number of checks, coverage percentage as a proxy for
correctness, "scans passed" counts. They reward activity, not protection.

## 6. The Incident Loop

Every incident gets one extra question in the postmortem: **which gate would have caught this?**

The answer is one of three:

1. **A gate that exists but did not run** — fix the scope, the trigger, or the skip.
2. **A gate that does not exist** — add it, with a canary and an owner, or write down why it cannot
   be gated and what the compensating control is.
3. **A gate that exists and ran but was wrong** — fix the rule, the threshold, or the exception that
   let it through.

Link the incident to the register row. A gate with no incident history is not suspicious; a gate
whose incident was closed without the question is a missed lesson. The "cannot be gated" notes are
as valuable as the gates: they keep the advisory list honest.

## 7. Rollout and Promotion

Do not flip a legacy codebase to blocking in one release. The phased rollout is the difference
between a gate and a mass disable:

| Phase | Behavior | Promotion criterion |
|---|---|---|
| Observe | report only, no baseline | volume measured; false positives sampled |
| Warn | visible, non-blocking | false positives near zero at the intended tier |
| Block new | baseline legacy; new violations fail | baseline reviewed, owner named, target set |
| Ratchet | baseline decreases on schedule | target reached or debt re-scoped |
| Steady | new violations fail; exceptions only | expiry jobs green; review current |

Announce the promotion date. Publish the command and the message. Give one sprint of warning before
a new blocking gate. If the rollout produces a flood, the rule is too broad or the baseline is
missing — do not "temporarily" disable and forget.

## 8. Deprecation

Deleting a gate is a change like any other:

- **Reason:** the rule retired, the tool was replaced, the module was deleted, or the signal was not
  worth the cost.
- **Replacement:** name the gate that supersedes it, or state explicitly that nothing does.
- **Date and owner:** when and who decided.
- **One change:** remove the check, the CI job, the baseline, the exception entries, the fixtures,
  and the register row together. A leftover baseline or canary is an orphan the next audit will find.

Never leave a "zombie gate" — configured, failing occasionally, and ignored. It trains everyone to
ignore red.

## 9. Change Management for Gates

A gate change is a code change with a higher blast radius:

- **Version it.** Rule set, config, and report schema have versions; the register records the
  version that produced a baseline.
- **Test it.** Positive and negative fixtures, plus the canary. A rule change that is not tested
  against the canary is unverified.
- **Observe it failing.** After any change to the check, scope, tool, tier, or report, inject the
  violation and watch it fail for the right reason.
- **Protect it.** CODEOWNERS, required review, protected workflow, and a separate diff from the code
  it judges.
- **Announce a behavior change.** Tightening a blocking gate mid-sprint without notice produces a
  bypass; loosening one without review produces a quiet policy change.
- **Update the evidence date.** The register should never show an older verification than the last
  change.

## 10. Multi-Repo and Monorepo

- **Shared rule pack, versioned.** A platform team publishes the checks and the report schema; each
  repository pins a version and owns its config and baseline.
- **Per-repo baselines.** A central baseline hides ownership and creates cross-repo coupling. Share
  the rule, not the debt.
- **Monorepo: per-package scope, root aggregate.** Each package owns its checks and budgets; the root
  runs the aggregate census and the cross-package boundary checks.
- **One merge queue per target branch.** Two packages with green independent runs do not compose; the
  merged tree is the gate.
- **A shared report schema.** Different languages and runners still produce the same status, finding,
  and summary shape, so the dashboard and the agent loop work everywhere.

## 11. Audit and Evidence Retention

For regulated or high-risk projects, the gate's output is evidence:

- retain JSON/SARIF reports for the required period (for example, 90 days for operational debugging,
  longer for compliance);
- record who approved each exception and when, with the platform identity rather than a typed name;
- keep the baseline and exception history in version control;
- link incidents to the gate that caught them (or the note explaining why none could);
- keep the canary fixtures and their last passing run;
- record the tool and rule versions that produced each report.

The audit question is not "did you have a gate?" It is "show me the run, the rule version, the
finding, the approval, and the fix." A register without retained reports answers none of those.

## 12. The Quarterly Review

One hour, once a quarter, with the gate owners:

1. Stale gates: no findings, no incident, no owner — deprecate or re-justify.
2. Expired exceptions and baselines: renew with a new reason, or remove.
3. Budget violations: which checks exceed their tier, and what moves.
4. Bypass incidents: why, and what the gate should change.
5. False-positive samples: which rules are losing trust.
6. New incident candidates: what should become a gate this quarter.
7. Advisory list: anything now measurable, or anything that should be deleted.
8. Register census: every binding rule has a gate or an advisory row.

The output is a short list of changes with owners and dates. A review that produces no changes is
either a very healthy quarter or a review that did not look.
