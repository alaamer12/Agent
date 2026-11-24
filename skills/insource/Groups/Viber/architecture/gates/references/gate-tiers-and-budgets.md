# Gate Tiers and Budgets

A gate is not only a rule; it is a rule at a boundary with a time budget. The same check can be a
useful editor hint, an acceptable pre-commit hook, an intolerable merge gate, and a pointless
nightly job. The tier decides who waits, how often, and what happens when the check is slow.

## 1. The Tiers

| Tier | Trigger | Scope | Budget (p95) | Blocks? | Typical checks | Owner |
|---|---|---|---|---|---|---|
| **T0** | save / keystroke | current file | < 2 s | no | types, lint, format | tooling |
| **T1** | commit | staged files | ≤ 10–15 s | yes, audited bypass | format, staged lint, secret scan, fast contract checks, touched-file typecheck | developer |
| **T2** | push / pull request | full repo + diff | ≤ 5 min | yes | build, typecheck, full lint, unit, contract, conformance, dependency diff, SAST, license | platform |
| **T3** | merge queue / required checks | full + integration | ≤ 20–30 min | yes | integration, e2e smoke, migration/destructive change, a11y/visual, coverage ratchet, bundle budget, mutation on changed core | quality owner |
| **T4** | nightly / release | full | hours | release | full e2e, mutation, full-repo census, dependency audit, performance budgets, restore drill, cross-browser | release owner |

Small repositories collapse T2 and T3; large ones split T2 into "fast" and "full". The names matter
less than the contract: each tier has a trigger, a scope, a measured budget, and a clear answer to
"does this block?"

Two rules keep the table honest:

- **A tier's budget is a total, not a per-check allowance.** Five checks at four minutes each are a
  twenty-minute tier, not five compliant checks.
- **A check that exceeds the budget moves down a tier or shrinks its scope.** It does not silently
  slow the boundary. The budget is a design constraint, not a dashboard aspiration.

## 2. Why These Numbers

The numbers are not arbitrary; they are the points where people start working around the gate.

- **Pre-commit: 10–15 seconds.** OWASP's pre-commit guidance is explicit that hooks exceeding this
  range get bypassed or disabled. Once `git commit --no-verify` becomes normal, the hook provides no
  dependable protection, and the habit spreads to the checks that mattered.
- **Pull request: about five minutes to first signal.** A developer who waits longer context-switches,
  batches the next change, and returns to a larger diff. The first required feedback should arrive
  inside the attention window; deeper checks can follow.
- **Merge: 20–30 minutes.** A gate that takes forty minutes teaches people to batch changes, which
  makes each change larger and each failure harder to attribute. If the deep suite cannot fit, split
  it: a fast required subset at merge and the rest at nightly, with a release gate that makes the
  nightly result binding.
- **Nightly: hours are acceptable** because nobody is waiting. The trade-off is latency: a failure
  found at 02:00 is fixed the next morning, so nightly checks must not be the only enforcement for a
  rule that can corrupt data or ship a vulnerability.

Measure **p95**, not the average, over the last thirty runs. The average hides the slow tail that
actually causes bypasses. Include queue time in the report even if the budget covers execution
only; a two-minute job behind a forty-minute queue is a forty-two-minute gate to the person waiting.

## 3. Ordering Inside a Tier

Run checks in this order:

1. **Parse / compile.** Nothing downstream is meaningful if the code does not parse.
2. **Typecheck.** Fast relative to tests and catches a large class of defects.
3. **Lint and format.** Format first if it rewrites; then lint the result.
4. **Project contract checks.** Cheap source/AST scans.
5. **Unit tests.** The fastest behavioral signal.
6. **Conformance tests.** Cross-file and catalog checks.
7. **Build.** The artifact the later stages will exercise.
8. **Integration / e2e.** The expensive behavioral signal.
9. **Security and dependency scans.** Often parallelizable; do not serialize them behind e2e.
10. **Budgets and measurements.** Performance, bundle size, accessibility, visual diffs.

Two ordering rules:

- **Deterministic before probabilistic.** A flaky e2e test should not decide whether the typecheck
  runs. Put the stable checks first so a red result is trustworthy.
- **Auto-fix before report.** If a formatter or codemod can fix the finding, run it and re-check.
  Reporting a fixable style issue spends the author's attention for no reason.

## 4. Incrementality — and Its Lies

Every fast tier uses a subset: staged files, changed files, or a cache. Every subset can lie.

| Mode | What it sees | Good for | Lies when |
|---|---|---|---|
| **Staged** | files in the index | pre-commit lint/format/secret scan | a cross-file rule needs an unchanged file; a rename is staged as delete+add |
| **Changed vs base** | files touched by the branch | PR fast checks | a rule depends on an unchanged dependency; a generated file changed indirectly |
| **Cached** | files whose content hash matches the last run | repeated local runs, CI cache | the rule, config, tool, or platform changed; the cache key omits one of them |
| **Full** | the whole repository | merge, nightly, release | never; it is the ground truth |

Design rules:

- **The cache key includes content, rule version, config version, and tool version.** A cache keyed
  only on file mtime or content will serve a stale "pass" after the rule changes. A tool upgrade that
  adds a rule but reuses the old cache is a silent regression.
- **A large diff disables incrementality.** Above a threshold, scan everything. The reference
  implementation in chekr defaults `largeDiffThreshold` to 20 files: above it, the runner warns,
  counts down, invalidates the cache, and forces a full scan; `--keep-on` skips the warning but the
  design point stands. Agents produce large diffs routinely, so a changed-only gate under-scans
  exactly when risk is highest.
- **Zero files in scope is a failure, not a pass.** A path move, a glob typo, or an empty diff must
  not produce a green gate. Assert a sanity floor ("scanned at least N files") in the runner.
- **Count deletions and renames.** A gate that only sees additions misses a deleted favicon, a
  removed test, or a renamed migration. Compare the file set, not just the added lines.
- **Exclude generated and vendor code explicitly, and gate the generator.** An exclusion that
  nobody reviews becomes a hiding place. The generator's output should be checked once, in the job
  that generates it.

## 5. Fail Closed

A blocking gate has four possible outcomes:

| Status | Meaning | Blocks? | Message |
|---|---|---|---|
| **PASS** | the check ran and found nothing above threshold | no | summary and duration |
| **FAILED** | the check ran and found violations | yes | rule, file, line, impact, fix |
| **ERROR** | the check could not run (crash, missing report, timeout, unparsable output) | yes | what failed, where the log is, who owns it |
| **SKIPPED** | the check did not run (condition false, dependency absent, quota) | yes, unless a recorded waiver | why it skipped, and the waiver id |

`ERROR` and `FAILED` are different: one is a product finding, the other is a broken gate. Both block,
but the owner and the fix differ, and conflating them hides a pipeline outage as a code problem.

Concrete rules:

- **A missing report is an error.** OWASP's example is explicit: if the scanner did not produce
  `semgrep.json`, exit non-zero with "the scanner did not run" before parsing anything.
- **A timeout is an error.** A hung job is not a pass, and a retry that eventually succeeds is not a
  fix.
- **Do not trust the tool's exit code; parse the report.** Some scanners exit `1` when findings
  exist and `0` when clean; some exit `0` regardless of findings; some exit non-zero on a tool
  failure. Normalize per tool into PASS/FAILED/ERROR, then decide. The exit-code trap is the most
  common way a gate becomes cosmetic.
- **Never `continue-on-error` on a blocking gate.** If the pipeline continues, the gate is advisory
  with extra steps. If a check must be non-blocking, put it in the advisory tier and say so.
- **A skipped required job is a failure.** "The workflow only runs on `main`" is how a pull request
  merges without the check.

A useful runner shape:

```text
run the tool → capture output and exit code
  report missing?         → ERROR
  exit code says crash?   → ERROR
  report unparsable?      → ERROR
  findings above policy?  → FAILED
  otherwise               → PASS
```

## 6. Blocking vs Advisory

The blocking list is short and absolute. A reasonable default, adapted from the five gates that
carry most of the value in an AI-native pipeline:

1. **Build and typecheck.** It compiles, type-checks, and starts.
2. **Tests that encode the acceptance criteria.** Not merely "tests pass"; the tests written from
   the specification pass.
3. **Secret scanning.** Nothing that looks like a credential is committed.
4. **Dependency policy.** New dependencies are reviewed, licensed, and free of known critical
   vulnerabilities.
5. **Migration and destructive-change detection.** Schema changes, data deletion, and changes that
   cannot be reversed by a redeploy get a human.

Then add the project-specific gates that protect its actual failure modes: design-token contract,
component substitution, conformance census, render health, accessibility budget, performance budget.
Keep the total small enough to remember. Five that always block beat twenty that sometimes warn.

What should warn rather than block:

- style and formatting (apply the formatter instead);
- complexity scores and most static-analysis suggestions;
- coverage percentages **as a target** (an agent asked to raise coverage will raise coverage, often
  with tests that assert the code does what it does). A changed-lines floor is a different gate: it
  ratchets the new code rather than the repository average, and it may block — see
  [baselines-ratchets-and-exceptions.md](baselines-ratchets-and-exceptions.md);
- bundle-size drift, unless a declared budget is exceeded;
- TODO/FIXME counts and documentation coverage;
- anything whose false-positive rate at the blocking tier is not near zero.

The advisory tier is not a graveyard. Every advisory check has an owner, a reason, and a review
date; a check that has been advisory for a year without a promotion decision is a deleted check.

## 7. Flake Policy

A flaky gate is a broken gate. Treat it as an outage, not an annoyance.

- **Remove it from the blocking tier, fix it, put it back.** Leaving it in place teaches everyone
  that a red pipeline might mean nothing, which is the same as having no pipeline.
- **Quarantine with an owner and an expiry.** A quarantined check reports to a non-blocking lane,
  names its owner, and has a date. A nightly job fails when the quarantine expires.
- **Retries only in non-blocking lanes.** Report the retry rate as a metric. A retry that hides a
  race is a bug with a green badge.
- **Volume multiplies flake.** A test that fails one run in fifty is a curiosity at ten merges a
  week and a daily interruption at a hundred. The agent-written code volume makes this worse, not
  better.

## 8. The Cost Model

Every gate spends one of three currencies:

- **Developer minutes:** waiting at T1/T2, context-switching, batching changes.
- **CI minutes:** parallel runners, cache storage, queue time.
- **Agent tokens:** the report the agent must read, the retries it performs, the context it spends
  on a 400-finding output.

A simple calculation keeps the design honest:

```text
annual cost ≈ (waiting minutes per run) × (runs per developer per day) × (developers) × (days)
```

A two-minute check run twenty times a day by ten developers is about 6.7 hours a day of waiting. A
ten-second check is about 33 minutes. The difference is worth paying only if the slower check finds
something the faster one cannot — which is exactly the tier question.

For agents, cap the report: a summary with counts and the top N findings, plus a path to the full
JSON. An agent that reads 400 findings to fix one spends context on noise; an agent that reads a
count and a file can drill down.

## 9. A Worked Budget (web application)

| Tier | Check | Budget | Notes |
|---|---|---|---|
| T1 | format staged | 1 s | auto-fix, re-stage |
| T1 | lint staged | 3 s | changed files only |
| T1 | secret scan | 1 s | full diff, verified secrets |
| T1 | contract checks (tokens, primitives) | 4 s | changed files |
| T1 | typecheck touched | 3 s | project references or `tsc --noEmit` on the touched project |
| **T1 total** | | **≤ 12 s** | above 15 s, move a check to T2 |
| T2 | install (cached) | 20 s | lockfile key |
| T2 | typecheck | 60 s | full project |
| T2 | lint | 40 s | `--max-warnings=0` |
| T2 | unit tests | 60 s | hermetic |
| T2 | conformance tests | 20 s | census + docs |
| T2 | build | 60 s | production artifact |
| T2 | SAST / dependency diff | 40 s | parallel with build |
| **T2 total** | | **≤ 5 min** | p95, including queue |
| T3 | integration | 4 min | database + API |
| T3 | e2e smoke | 8 min | critical journeys + render health |
| T3 | a11y / visual | 3 min | representative pages |
| T3 | migration check | 30 s | destructive-change detector |
| T3 | bundle budget | 1 min | gzip, per route |
| T3 | coverage ratchet | 30 s | changed lines only |
| **T3 total** | | **≤ 18 min** | nightly owns the rest |
| T4 | full e2e | 30 min | all journeys |
| T4 | mutation (changed core) | 40 min | score threshold + surviving mutants report |
| T4 | dependency audit | 5 min | full tree, licenses |
| T4 | performance budgets | 10 min | p75 field or lab |
| T4 | restore drill | 5 min | backup → restore → verify |
| **T4 total** | | **≤ 90 min** | nobody is waiting |

## 10. Tier Anti-patterns

| The shortcut | The documented cost |
|---|---|
| Everything at pre-commit | 90 seconds, then `--no-verify`; the gate is gone |
| The full e2e suite on every commit | batching, larger diffs, slower attribution |
| The same check at T1, T2, T3, and T4 | cost without signal; one authoritative tier is enough |
| A seven-minute "fast" PR lane | the first signal arrives after the context switch |
| Incremental scan with no large-diff escape | the riskiest change gets the least coverage |
| Cache keyed on mtime | a stale pass after a rule edit |
| Empty scope treated as success | a path typo disables the gate silently |
| `continue-on-error` on a required job | a gate that cannot fail |
| Retrying a flaky check at merge | the signal dies; the flake stays |
| A blocking coverage percentage | measures compliance with the gate, not correctness |
| Nightly as the only security gate | a vulnerability ships for a day |
| Budget measured as an average | the slow tail is what causes bypasses |
| Queue time excluded from the report | the developer experiences 42 minutes, the dashboard says 2 |
