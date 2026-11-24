# Writing a Gate

A gate is a small product. It has a user (the person or agent who must fix the finding), a contract
(what it checks and what it ignores), a failure mode (what happens when it cannot run), an owner, and
a maintenance cost. Writing one is mostly deciding those things; the detection code is the easy
part.

## 1. The Gate Card

Every gate gets one card. The card is what a reviewer reads, what the register stores, and what the
next maintainer inherits.

```text
Gate:        design/no-raw-color
Rule:        No literal color value may appear outside tokens/**.
Why:         A rebrand and a dark theme missed 41 hardcoded colors; the contrast audit failed.
Rung:        2 — project contract check (source scan), plus Stylelint if available.
Tier:        T1 on staged files; T2 full repository.
Command:     bun run gates:colors --changed
Scope:       src/**/*.{ts,tsx,css,html}, docs/**/*.md; exclude tokens/**, **/*.generated.*
Budget:      p95 2.1 s at T1 (measured 2026-11-18, 214 files)
Failure:     FAILED on any occurrence; ERROR if the report is missing or the scan finds zero files.
Report:      JSON to .reports/no-raw-color.json; human summary to stderr.
Evidence:    2026-11-18 — injected #ff0000 into src/ui/Button.tsx:12; gate red with rule id and
             nearest token; reverted; green. Canary fixture: gates/fixtures/no-raw-color/.
Exception:   // gates-ignore-next-line design/no-raw-color -- <reason>; file-level needs design-system
             approval; expiry 90 days; recorded in gates/exceptions.yaml.
Owner:       design-system
Docs:        <docs>/gates-architecture.md §4.1
```

If a field is unknown, the gate is not designed yet. "We will figure out the exception later" is how
a gate becomes a habit.

## 2. Writing the Rule Statement

A gate rule is one sentence that a stranger can evaluate against a file:

- **Testable:** "No literal color value appears outside `tokens/**`."
- **Scoped:** it names the universe ("outside `tokens/**`") and the exception ("generated themes are
  excluded by path").
- **Counterexampled:** the card includes one input that must fail and one that must pass.

Weak statements and what they hide:

| Weak statement | Why it cannot be a gate |
|---|---|
| "Use the design system" | no observable condition; every reviewer disagrees |
| "Keep components clean" | no counterexample; no scope; no fix |
| "Do not duplicate types" | duplication of what — shape, name, fields, semantics? |
| "Handle all states" | which states, on which components, verified how? |
| "Be accessible" | a rubric, not a test; split into contrast, labels, focus, motion |
| "Write tests" | a count, not a property; specify the behavior or the invariant |

The rewrite is always the same move: **replace the adjective with an observable fact and a scope.**
"Be accessible" becomes "every interactive control has an accessible name and a visible focus ring,
verified by the a11y scan on the routes in the page inventory."

## 3. Choosing the Detection

Use the earliest mechanism that can see the fact without being fooled (see
[enforcement-ladder.md](enforcement-ladder.md)). Within a rung, choose the cheapest detector that
keeps false positives rare at the blocking tier.

| Fact | Detector | Note |
|---|---|---|
| a literal outside an allowlist | source scan | include docs/config/SQL if the rule says "everywhere" |
| a JSX element name or prop | AST | a regex also matches comments and strings |
| an import crossing a layer | dependency graph / AST | resolve specifiers, not raw text |
| a catalog is complete | conformance test | enumerate the source of truth; assert a sanity floor |
| a runtime payload shape | schema parse | produce a typed value; do not cast |
| a performance budget | measurement | p75/p95 in metric units; pin the environment |
| a visual property | screenshot/DOM assertion | pin viewport, fonts, and data |

Precision versus recall is a tier decision:

- **At a blocking tier, precision wins.** A false positive teaches suppression and costs more trust
  than a missed finding costs risk. Narrow the rule until the current repository produces zero or
  near-zero false positives; baseline the true positives.
- **At an advisory tier, recall can be higher.** A noisy report is acceptable if a human triages it,
  but it still needs an owner and a review date.

Test the detector against a small corpus before shipping it: at least one positive, one negative,
one edge case (comment, string, generated file), and one file outside the usual extension. The
corpus is also the gate's regression test.

## 4. Designing the Message

The finding is the gate's user interface. A good one lets a stranger fix the problem without opening
the rule's source:

```text
src/ui/Button.tsx:12:18  error  design/no-raw-color
  Raw color "#ff0000" outside the token module.
  Impact: breaks the dark theme and the contrast budget.
  Fix: use tokens.color.action.danger (nearest match: danger.500).
  Docs: docs/gates-architecture.md#no-raw-color
```

Required parts:

- **Location:** file, line, column. A finding without a location is a lecture.
- **Rule id:** stable, used by suppressions and the register.
- **What:** the observed value or pattern, quoted and shortened.
- **Why:** the consequence in one line. "Breaks the dark theme" is actionable; "violates policy" is
  not.
- **Fix:** the replacement, the command, or the next step. If the tool can auto-fix, say so and do
  it.
- **Docs:** the section that explains the rule, for the cases the message cannot cover.

Additional rules:

- **Stable logical id.** Group related findings under one id (`arch/boundary`) so a multi-file
  violation reads as one problem with occurrences, not twelve unrelated errors.
- **Occurrences, not duplicates.** When a violation has related locations (the import and the
  forbidden module, the duplicate types), report one finding with occurrence locations.
- **No noise in the blocking message.** Do not print the whole file, the full AST, or a stack trace.
  Put the detail in the JSON report and link it.
- **Deterministic ordering.** Sort by file, line, rule. A report whose order changes between runs is
  hard to diff and hard for an agent to consume.

## 5. The Report Contract

The exit code decides; the report explains. Both are part of the gate.

A minimal JSON shape that works for humans, CI, and agents:

```json
{
  "gate": "design/no-raw-color",
  "status": "failed",
  "rule": "design/no-raw-color",
  "toolVersion": "1.4.0",
  "startedAt": "2026-11-18T10:12:03Z",
  "durationMs": 2140,
  "scope": { "files": 214, "excluded": 37 },
  "findings": [
    {
      "file": "src/ui/Button.tsx",
      "line": 12,
      "column": 18,
      "severity": "error",
      "rule": "design/no-raw-color",
      "logicalId": "design/no-raw-color:src/ui/Button.tsx:12",
      "message": "Raw color \"#ff0000\" outside the token module.",
      "impact": "Breaks the dark theme and the contrast budget.",
      "fix": "Use tokens.color.action.danger (nearest match: danger.500).",
      "occurrences": []
    }
  ],
  "summary": { "findings": 1, "suppressed": 0, "bySeverity": { "error": 1 } }
}
```

Contract rules:

- **`status` is one of `passed`, `failed`, `error`, `skipped`.** A report with `status: "failed"` and
  exit code 0 is a bug in the gate, not a pass. `skipped` blocks unless a recorded waiver names it,
  because a required check that did not run is not a green check.
- **`scope.files` is present.** Zero files is an error, not a clean run.
- **`toolVersion` and `rule` are present.** A finding must be attributable to the rule set that
  produced it. This is also what makes a baseline or cache key safe.
- **`findings` are stable and sorted.** The same input produces the same report, byte for byte,
  except for timestamps and durations.
- **`error` carries a message and a log path** when the gate could not run. Never encode a tool
  failure as an empty findings list.
- **The human summary is derived, not hand-written.** Counts, the top findings, and the report path
  are enough. A 400-line terminal dump is not a summary.

For agents, add a `--report` path and a `--summary` mode that prints counts plus the first N
findings. The agent reads the summary, fixes, and reruns; it opens the JSON only when it needs the
detail. This is a token budget decision as much as a UX one.

## 6. Exit Codes

Pick one convention and enforce it in the runner:

| Code | Meaning |
|---|---|
| `0` | the gate ran, the scope was non-empty, and no finding exceeded the threshold |
| `1` | the gate ran and found violations above the threshold |
| `2` | the gate could not run (tool crash, missing report, timeout, unparsable output, empty scope) |

Do not assume a third-party tool follows this. Normalize it:

- a scanner that exits `1` on findings is `FAILED`, not `ERROR`;
- a scanner that exits `0` on findings is not a gate until a wrapper parses its report;
- a scanner that exits non-zero on a crash is `ERROR`, not `FAILED`;
- a test runner that exits `0` with a skipped required suite is `SKIPPED`, which blocks.

The wrapper owns the mapping. The CI step checks the wrapper's code, not the tool's.

## 7. Evidence — Make It Fail

A gate is not built until someone has watched it fail for the right reason. Keep the evidence in
three layers:

1. **A canary fixture.** A directory with one input that must fail and one that must pass:

   ```text
   gates/fixtures/no-raw-color/
   ├── positive/Button.tsx     # contains #ff0000 → must fail
   ├── negative/Button.tsx     # uses tokens.color.action.danger → must pass
   └── expected.json           # rule id, file, line
   ```

   A meta-test runs the gate against the fixture and asserts the failure, the rule id, and the
   location. The fixture is part of the test suite, so the gate cannot silently stop working.

2. **A recorded observation.** The register stores the date, the command, the output line, and the
   commit that was reverted. "We tested it once" without a date is folklore.

3. **A re-verification trigger.** Re-run the canary after any change to the rule, its scope, its
   dependencies, its tier, the report schema, or the CI image. A rule that passed its canary two
   years ago and has changed twice since is unverified.

Test the test, too. Temporarily break the detector (remove the pattern, invert the condition) and
confirm the canary goes green — if it does, the canary was not exercising the detector. A gate whose
test cannot fail is the same problem as a test with no assertion.

## 8. Protection — Keep the Gate Out of the Gated's Reach

The gate is only as strong as its isolation from the change it judges.

- **Check definitions live in a protected path.** `gates/`, `.tool/checks/`, or the equivalent, with
  a CODEOWNERS entry and a required human approval.
- **Pipeline configuration runs from the protected branch.** A workflow that executes the pull
  request's own config can be edited by the pull request. Use required workflows, a merge queue, or a
  protected configuration source.
- **Baselines and exception files are protected too.** A baseline that the author can regenerate is
  a mute button. A baseline change is its own reviewed diff with a reason.
- **Fixtures and tests are protected.** Deleting the test that fails is the oldest way to make a gate
  pass. A test-count or assertion-count ratchet catches the quiet version.
- **Approvals come from the platform, not a variable.** `APPROVED_BY=alice` proves nothing; a
  protected environment with a restricted approver list records the identity. The same applies to
  branch protection and required reviewers.
- **The agent's environment is read-only for gate files.** The agent may run the gate, read the
  report, and fix the code; it may not edit the check, the baseline, the threshold, or the workflow.
  If the environment cannot enforce that, the review must, and the diff must make the change obvious.

A useful test: open a pull request that edits only the gate config and see what happens. If it can
merge without a human, the gate is advisory.

## 9. Performance

A gate that is slow is a gate that is bypassed. Before shipping:

- **Scope it.** Scan the files the rule can actually apply to. Excluding `node_modules`, build
  output, and vendor code is table stakes; excluding the docs when the rule says "everywhere" is a
  hole.
- **Cache correctly.** Content + rule version + config version + tool version. Never mtime alone.
- **Parallelize independent work.** Per-file checks are embarrassingly parallel; the runner should
  not serialize them.
- **Fail fast where it is safe.** A parse error can stop the run; a missing report should stop it
  before any parsing.
- **Keep it offline.** A network call inside a gate is a flaky dependency and a privacy surface.
- **Measure p95.** Profile the slowest rule, not the average. A single regex that backtracks on a
  generated file can dominate the tier.

If the gate cannot fit its tier, move it down a tier or narrow its scope. Do not "optimize later" by
raising the budget; the budget is the contract.

## 10. Review Checklist for a New Gate

1. Is the rule one testable sentence, with a counterexample and a scope?
2. Is this the earliest rung that can see the fact completely?
3. Does the scope include the files that actually fail — docs, SQL, config, templates, scripts?
4. What is the false-positive rate on the current repository? Sample at least twenty findings.
5. Does every finding name file:line, rule id, what, why, and a fix?
6. Is there a canary fixture, and has the gate been observed failing for the right reason?
7. What is the measured p95, and does it fit the tier budget?
8. What happens on a tool error, a missing report, a timeout, and an empty scope? (All must block.)
9. Who owns the gate, where is the exception recorded, and when does it expire?
10. Can the gated change edit the check, the baseline, or the workflow? If yes, fix that first.
11. Does the cache key include the rule and tool version? Does a large diff force a full scan?
12. Is the gate in the register and the census, with an evidence date?

## 11. Reference Implementation: chekr

The author's `chekr` project is a worked example of the rung-2 contract checker; the design lessons
transfer to any stack.

- **Rules are plain functions over source.** A check receives `(source, filePath, context)` and
  returns violations or calls `context.report`. No DSL, no framework coupling.
- **The report is a first-class contract.** `context.report` carries `message`, `impact`, `severity`,
  `logicalId`, `data`, and `occurrences`, so a violation can group related locations and explain its
  consequence.
- **Suppression is scoped and typed.** `// @chekr-ignore <selector>` suppresses a named step on one
  line; selectors can be step ids, numbers, `all`, or combinations. Legacy start/end blocks still
  work but are deprecated and report migration warnings. The lesson: the suppression names the rule,
  so it cannot silently hide a future rule.
- **The runner is built for the boundary.** `--changed` diffs `HEAD`, `--staged` reads the index,
  the cache is content-hash based, and a diff above `largeDiffThreshold` (default 20 files) warns,
  invalidates the cache, and forces a full scan; `--keep-on` skips the warning. Agents produce large
  diffs, so this is not a corner case.
- **Runs leave evidence.** The analysis record stores step id, status, timestamp, duration, files
  checked, pass/fail/ignore counts, total violations, the resolved config, and child records. A gate
  whose history nobody can inspect is a gate nobody can tune.
- **The roadmap names the next two rungs.** A safe-violations database with context-block identity
  (F-09) is the baseline/ratchet form; severity levels with an `--level` threshold (F-10) are the
  blocking/advisory form. Neither is required to adopt the design: the point is that a rule engine
  becomes a gate only when identity, severity, baseline, and reporting exist.

The transferable pattern: **the rule is twenty lines; the gate is the identity, budget, report,
exception, protection, and evidence around it.**

## 12. A Polyglot Skeleton

The shape is the same in every language: a detector, a report, a status, an exit code. The three
skeletons below report the **first** match per line for brevity; a real detector loops with a global
regex and reports every occurrence.

```ts
// gates/checks/no-raw-color.ts
export type Finding = {
  file: string; line: number; column: number; rule: string;
  message: string; impact: string; fix?: string;
};

export function check(source: string, file: string): Finding[] {
  const findings: Finding[] = [];
  source.split("\n").forEach((text, i) => {
    const m = /#[0-9a-fA-F]{6}\b/.exec(text);
    if (m) findings.push({
      file, line: i + 1, column: m.index + 1, rule: "design/no-raw-color",
      message: `Raw color "${m[0]}" outside the token module.`,
      impact: "Breaks the dark theme and the contrast budget.",
      fix: "Use a tokens.color.* value.",
    });
  });
  return findings;
}
```

```python
# gates/checks/no_raw_color.py
import re
from dataclasses import dataclass

@dataclass
class Finding:
    file: str
    line: int
    column: int
    rule: str
    message: str

HEX = re.compile(r"#[0-9a-fA-F]{6}\b")

def check(source: str, path: str) -> list[Finding]:
    return [
        Finding(path, i, m.start() + 1, "design/no-raw-color",
                f'Raw color "{m.group(0)}" outside the token module.')
        for i, line in enumerate(source.splitlines(), 1)
        if (m := HEX.search(line))
    ]
```

```go
// gates/checks/norawcolor.go
package checks

import (
    "regexp"
    "strings"
)

type Finding struct {
    File, Rule, Message string
    Line, Column        int
}

var hex = regexp.MustCompile(`#[0-9a-fA-F]{6}\b`)

func NoRawColor(source, path string) []Finding {
    var out []Finding
    for i, line := range strings.Split(source, "\n") {
        if loc := hex.FindStringIndex(line); loc != nil {
            out = append(out, Finding{path, "design/no-raw-color",
                "Raw color outside the token module.", i + 1, loc[0] + 1})
        }
    }
    return out
}
```

The runner around these functions is where the gate lives: scope resolution, exclusions, cache,
report assembly, status mapping, and `os.Exit(0|1|2)`. Do not let the detector own the exit code; the
runner owns the decision.
