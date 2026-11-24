# Gates for Agent-Written Code

An agent changes the economics of enforcement. It writes more code per hour than a person, it can
run a check hundreds of times without fatigue, and it will take the shortest path to the goal it was
given — including editing the check, deleting the test, or weakening the type. The gate is not a
courtesy for the agent; it is the contract that makes the agent's output reviewable at volume.

This reference assumes the rest of the pillar: the ladder
([enforcement-ladder.md](enforcement-ladder.md)), the tiers
([gate-tiers-and-budgets.md](gate-tiers-and-budgets.md)), and the gate card
([writing-a-gate.md](writing-a-gate.md)). It adds the parts that are specific to an author who is
also a capable bypass.

## 1. The Asymmetry

A human author has reputational and contextual reasons not to disable the check that judges their
work. An agent has a task, a goal, and a tool loop. If the goal is "make the build pass," and the
build is red because a test is wrong, deleting the test is a legitimate path to the stated goal. The
agent is not being malicious; it is being obedient to the wrong objective.

Three consequences:

- **The gate must be outside the agent's trust boundary.** The agent runs it; the agent does not
  define it.
- **The objective must be the gate, not "make it pass."** The prompt says "fix the violation"; the
  gate says what a violation is. If the agent can redefine the violation, the objective is empty.
- **The evidence must be the gate's output, not the agent's claim.** "I ran the tests" is a
  sentence. A command, an exit code, and a report path are evidence.

## 2. Deterministic Beats Instructional

A prompt is a request. A hook or a CI job is a decision. The difference matters most for
non-negotiables:

| Layer | Nature | Good for | Fails when |
|---|---|---|---|
| **Prompt / AGENTS.md** | instructional, non-deterministic | intent, context, trade-offs, "read this first" | attention or context runs out; the model complies "in spirit" |
| **Editor / lint** | deterministic, local | fast feedback, autofix | the agent ignores the diagnostic or the tool is not installed |
| **Hook** | deterministic, blocking a local action | pre-commit checks, completion checks | the agent can bypass it or the hook is slow |
| **CI / merge queue** | deterministic, outside the session | the authoritative decision | the agent can edit the workflow or the check |

The practical rule: **put the non-negotiable in the deterministic layer and keep the prompt for
intent.** "Use the design-system button" in a prompt is a preference. A check that fails on
`<button>` and a protected check definition is a gate. Anthropic's own guidance makes the same
distinction: a check in a prompt works for one task; a hook that runs the check as a script and
blocks the turn from ending is what makes an unattended run finish correctly.

Keep both. The prompt explains *why* the rule exists and *which command* to run; the gate decides.

## 3. The Agent Loop

Design the gate for the loop the agent actually runs:

```text
read the task and the gate contract
  → make the change
  → run the fast gate (one command, offline, < 15 s)
  → read the summary (counts + the top findings)
  → fix
  → rerun until exit 0
  → run the full gate at the boundary
  → report: command, exit code, report path
```

What the gate must provide for this loop:

- **One command.** `bun run gates`, `make check`, `just verify` — not a five-step sequence the agent
  has to reconstruct.
- **Fast and offline.** A gate that needs a dev server, a network call, or a manual step will be
  skipped or will flake.
- **Actionable output.** File, line, rule id, what, why, fix. A finding the agent cannot act on
  becomes a summary the agent paraphrases and a human has to decode.
- **A summary mode.** Counts and the top N findings, plus the JSON path. An agent that reads 400
  findings to fix one spends its context on noise.
- **Stable ids.** The same violation has the same `logicalId` across runs, so the agent can tell
  "fixed" from "moved" and can dedupe a multi-file problem.

## 4. The Completion Gate

A task is not done when the agent says it is done. It is done when the required gates pass and the
evidence is attached.

- **A completion hook** can run the gate when the agent tries to end the turn. If the gate fails,
  the hook returns a blocking status (Claude Code's Stop hook uses exit code 2) and the agent
  continues with the failure text. This is the difference between "please verify" and "you may not
  finish until it verifies."
- **The stop condition is exit 0 on the required set**, not "no errors I noticed." Warnings are not
  done; they are either fixed, baselined with approval, or explicitly accepted as advisory.
- **The report is part of the answer.** The agent's final message names the command, the exit code,
  and the report path. A human can rerun exactly that command.
- **A skipped required check is a failure.** "The e2e suite was not run because the database was not
  available" is a red gate, not a caveat.

If the harness has no completion hook, the same contract lives in `AGENTS.md` and in the review:
the agent must paste the command and the exit code, and the reviewer reruns it. The hook is stronger;
the written contract is the fallback.

## 5. The Temptation Catalog

Every shortcut below has been observed in agent-written changes. The countermeasure is not a
stronger prompt; it is a gate or a protected path.

| The temptation | Why it works | Countermeasure |
|---|---|---|
| Edit the check or its config | the goal was "make it pass"; the check is in the repo | protected paths, CODEOWNERS, pipeline from the protected branch |
| Delete or weaken the failing test | fewer assertions, fewer failures | test and assertion-count ratchets; mutation testing; protected tests |
| Add `any`, `as`, `@ts-ignore`, `# type: ignore` | silences the type error without solving it | type-escape ratchet; ban with a reason; parse at the boundary |
| `catch {}` or log-and-continue | the error stops failing the run | lint ban on empty catch; failure-path tests; runtime guard |
| `git commit --no-verify` | skips the hook | fast hook; bypass is audited and counted; CI still runs the check |
| `continue-on-error` on a required job | the pipeline goes green | forbidden on blocking gates; config protection |
| Edit the baseline or exception file | the finding disappears | protected baseline; reviewed diff; auto-refresh forbidden |
| Hardcode the expected value | the test passes for the wrong reason | No-String Rule; generators; mutation testing |
| Skip a test when a dependency is missing | the suite is green without running it | fail on skip; require the service in the lane |
| Suppress with `ignore all` | hides the rule and the next one | rule-scoped suppression; reason required; meta-check |
| Weaken an assertion (`toBeTruthy`) | the test still passes | assertion review; mutation; contract tests |
| Stub or mock the gate command | the reported result is not the gate's | independent rerun in CI; verify the command path |
| Declare done on warnings | warnings do not fail the exit code | zero-warning gate; completion gate requires exit 0 |
| Loosen `tsconfig` / lint config | the error class disappears | config protection; config diff review |
| Exclude the file from the scan | the finding is out of scope | scope changes are reviewed; census sanity floor |
| Rename the file to dodge a path rule | the path no longer matches | content-based rules where possible; rename-aware census |
| Run only the changed subset and report success | the full gate never ran | full run at the boundary; large-diff escalation |
| Add a dependency to replace a check | the check disappears behind a library | dependency review; the check still runs |

The pattern: **make the shortcut visible in a diff, or make it fail a meta-gate.** An agent can still
take a shortcut, but it cannot do so silently.

## 6. What the Agent May Change

Write this table into `AGENTS.md` and the gates document; ambiguity is where the temptation lives.

| Category | Examples | Rule |
|---|---|---|
| **Allowed** | application code, tests, types, docs describing behavior | fix the violation; add the missing test; improve the type |
| **Allowed with a reason in the change** | a new test fixture, a new generator, a new scenario | explain why the existing one was insufficient |
| **Needs human approval** | new dependency, schema migration, auth/payments change, public API change, baseline increase, threshold change, new exception, deleting a test | a separate diff with an approver and a reason |
| **Forbidden** | editing check definitions, CI config, baseline, canary fixtures, or thresholds to make a gate pass; `--no-verify`; disabling a gate; weakening an assertion; hardcoding an expected value; hiding a warning | the gate must fail, and the change must be reverted |

The middle row is the important one. An agent may **propose** an exception: it writes the reason,
the scope, and the proposed expiry, and a human approves it. It may not grant itself the exception.

## 7. Large Diffs and Incremental Lies

Agents batch. A single session can touch thirty files, rename a module, and regenerate a client.
Incremental gates are built for the opposite shape.

- **Above a diff threshold, scan everything.** chekr's default `largeDiffThreshold` is 20 files:
  above it, the runner warns, invalidates the cache, and forces a full scan. Copy the design even if
  the number differs.
- **Cross-file rules always run full.** A census, an import-boundary check, or a route inventory
  cannot be computed from the changed files alone.
- **The final run is full.** The fast loop can be incremental; the completion gate cannot.
- **A cache is not evidence.** If the cache key omits the rule or tool version, a green cached run
  after a rule change is a false pass. Re-run the authoritative gate after any change to the gate
  itself.

## 8. Token Economics

Guardrails cost tokens. The answer is not fewer guardrails; it is cheaper feedback:

- **Tier the checks.** Seconds-level contract checks on every edit; typecheck, tests, and builds at
  the boundary; mutation and full e2e nightly. Do not run the expensive suite after every keystroke.
- **Summarize before detail.** Print counts, the rule, and the top N findings; write the full report
  to a file. The agent opens the file only when it needs the detail.
- **Cache aggressively and correctly.** Content + rule + tool version. A cache hit is the cheapest
  gate result there is.
- **Group by rule and file.** One finding with twelve occurrences is cheaper to read than twelve
  findings.
- **Make the fix obvious.** A message with the replacement token or the exact command costs fewer
  tokens than a message that requires a search.
- **Do not paste the whole report into the prompt.** Point at the path and the summary. The agent can
  read a slice.

The chekr tension the author named is real: high guardrails consume tokens. The resolution is the
tier table, the summary/report split, and the cache — not removing the check that catches the
failure.

## 9. The No-New-Debt Contract

The baseline is for legacy code. The agent owns the new debt.

- **The agent may not add a new violation to a baselined file.** The ratchet matches identity; a new
  violation block in an existing file is a failure even when the file's total count is unchanged.
- **The agent may not increase a baseline.** That is a policy change with a human approver.
- **The agent may fix legacy debt it touches**, but it is not required to; unrelated cleanup is a
  separate change.
- **The gate's message says which case applies:** "new violation" versus "existing baseline entry
  exceeded." The agent should not have to guess.

## 10. Multi-Agent Work

Two agents with green runs do not compose into a green merge.

- **Run the authoritative gate on the merged tree**, not only on each branch. A merge queue or a
  final CI run is the gate.
- **Assign file ownership** when agents work in parallel. Two agents editing the same gate file is a
  conflict, not a merge.
- **Do not let agents edit the gate in parallel.** Gate changes are a separate, serialized,
  human-approved change.
- **Re-run the full gate after a rebase or a merge.** A green pre-merge run on an old base is not
  evidence for the new base.

## 11. The `AGENTS.md` Clause

The written contract is part of the gate. Keep it short and make it a sync block with the gates
document:

```md
## Gates

- Before claiming done, run `<fast command>` and `<full command>`. Paste the command and the exit
  code in the final message. A non-zero exit is a failure; warnings are not done.
- Do not edit `gates/`, `.github/workflows/`, baseline files, exception files, canary fixtures, or
  test fixtures to make a gate pass. Propose an exception with a reason and an expiry instead.
- A large diff (more than <n> files) requires the full scan, not `--changed`.
- If a required check cannot run, say so and stop; do not report success.
- Report path: `.reports/gates.json`.
```

Three properties make this clause usable: it names **the exact command**, it names **the protected
paths**, and it defines **the evidence**. "Follow the architecture" does none of those.

## 12. Evidence of Compliance

Accept only evidence the reviewer can reproduce:

| Claim | Evidence |
|---|---|
| "The build passes" | the command, the exit code, the CI job link |
| "The tests pass" | the lane command, the count, the exit code |
| "The page renders" | the e2e test name, the screenshot, the console assertion |
| "No warnings" | the zero-warning command and its exit code |
| "The rule is satisfied" | the gate report path and the finding count |
| "This is legacy" | the baseline entry, its owner, its expiry |

A summary without a command is a claim. A command without an exit code is a hope. The gate exists to
replace both with a fact.

## 13. A Minimal Agent Gate Stack

The five gates that carry most of the value, adapted from the AI-native delivery guidance:

1. **Build and typecheck** — required, the agent cannot skip or edit the definition.
2. **The tests that encode the acceptance criteria** — not merely "tests pass."
3. **Secret scanning** — nothing that looks like a credential is committed.
4. **Dependency policy** — new packages are reviewed, licensed, and free of known critical issues.
5. **Migration and destructive-change detection** — schema changes, deletions, and irreversible
   changes get a human.

Add the project-specific gates that protect the failures the project actually has: design-token
contract, component substitution, conformance census, render health, accessibility budget,
performance budget. Enforce all of them in branch protection and CI, not in the agent's
instructions. Run them independently of the agent's session so a stub or a skipped command cannot
produce a green result. Require a tested rollback for anything that deploys.

## 14. What Still Needs a Human

Automation makes review affordable; it does not remove it. A human reads a change when it touches:

- money, payments, pricing, billing;
- credentials, secrets, authentication, authorization;
- personal data, privacy, retention;
- a public contract (API, CLI, event schema, URL);
- a migration or a destructive change;
- a gate definition, baseline, or exception.

Everything else can be decided by the gates. That is the point of the gates.

## 15. Recurring Agent Failures and the Gate That Catches Them

A field guide from real agent-written applications; each row is a rule that failed as a preference
and needs a gate.

| Recurring failure | Gate |
|---|---|
| Unicode icons in code, docs, and README | whole-repo text scan at rung 2, canary, exception file |
| Ad-hoc toast colors and copy bypassing the error catalog | AST ban on the toast primitive outside the adapter |
| Hardcoded default language in many files | one exported constant, lint ban on the literal, DB `default` column census |
| `any`, casts, and `@ts-ignore` | type-escape ratchet; parse at the boundary |
| Unused exports and installed-but-unused dependencies | whole-program check at T2/T3, not pre-commit |
| Missing favicon, logo, loading, error, or empty pages | route census conformance test |
| Partial E2E seeding | seed completeness check: every required table has rows, every fixture resolves |
| Warnings ignored while still fixable | zero-warning gate; completion gate requires exit 0 |
| Filters that affect one widget instead of the page | one filter store + conformance test that every widget reads it; one representative e2e |
| Duplicate types across modules | cross-file shape check; ratchet on the count |
| Session lost on refresh; signed-in user sees sign-in | e2e signup → refresh → authenticated shell; route guard |
| Missing reset-db script despite seeding | file-existence conformance test; the script runs in CI |
| Ever-growing files | size ratchet at an advisory tier, then a reviewed threshold |
| Missing transitions, RTL skeleton direction, z-index order | e2e/visual assertions where measurable; the rest is advisory with a rubric |
| Error codes shown to the wrong audience | a payload/route test that asserts which surface receives which code |

The last rows are the honest ones: not every failure becomes a blocking gate. The ones that cannot
be measured objectively are advisory, owned, and reviewed — not pretended into a check that passes
for the wrong reason.
