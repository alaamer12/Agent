# Baselines, Ratchets, and Exceptions

The hardest moment in a gate's life is the day it meets a legacy codebase. The rule is right, the
check works, and it finds four hundred violations that predate the gate. Blocking on all of them
does not produce four hundred fixes; it produces a bypass, a disabled rule, or a team that learns
that red means "someone else's problem." The baseline is the mechanism that lets a gate start
without lying about the debt.

This reference covers three related mechanisms:

- **Baseline:** a recorded set of accepted existing violations, with an owner, a count, and a
  reduction schedule.
- **Ratchet:** the rule that the baseline may only shrink; new violations fail immediately.
- **Exception:** a time-boxed, approved acceptance of a specific risk that the gate would otherwise
  block.

They are not the same thing, and conflating them is how a project ends up with a permanent mute
button.

## 1. What a Baseline Is — and Is Not

A baseline is **debt with a payment plan**. It says: "these violations existed before the gate, we
have reviewed them, we own them, and here is when and how the count goes down." It is not a
permission slip, a TODO list, or a substitute for fixing the rule.

A baseline is appropriate when:

- the rule is correct and worth keeping;
- the existing violations are real but too numerous to fix in one change;
- the code owning them has an owner who accepts the debt;
- there is a credible reduction path (rewrite, migration, deletion, scheduled cleanup).

A baseline is not appropriate when:

- the rule is wrong, too broad, or produces false positives — fix the rule instead;
- the violations are security or correctness defects that should block now;
- nobody owns the code;
- the "reduction plan" is "someday." That is a deletion with extra steps.

## 2. Baseline Anatomy

```yaml
# gates/baselines/no-raw-color.yaml
rule: design/no-raw-color
tool: gates@1.4.0
created: 2026-11-01
owner: design-system
target: 0
expires: 2027-02-01
reduction: "-25% per sprint; report every Monday"
entries:
  - file: src/legacy/Chart.tsx
    fingerprint: "sha256:9f2c1a…"     # normalized context, not a line number
    count: 12
    reason: "legacy chart port; replaced by the TanStack chart in Q1"
    ticket: DS-412
  - file: src/features/reports/Export.tsx
    fingerprint: "sha256:41ab7e…"
    count: 3
    reason: "PDF export uses a vendor color table"
    ticket: DS-418
```

Required fields:

| Field | Why it exists |
|---|---|
| `rule` | identity; a baseline for one rule must never suppress another |
| `tool` | a rule or tool upgrade can change the finding; the baseline must be re-justified |
| `created` | age is a signal; an old baseline with no movement is a finding |
| `owner` | one role accountable for the reduction |
| `target` | the number the baseline is ratcheting toward; usually zero |
| `expires` | the date the baseline must be renewed or removed |
| `reduction` | the schedule, not a wish |
| `entries[].file` | scope; per-area baselines beat one central file |
| `entries[].fingerprint` | identity that survives line drift |
| `entries[].count` | the ratchet compares against this |
| `entries[].reason` / `ticket` | why this debt exists and where the work is tracked |

Optional but useful: `severity`, `scope` (a glob), `approved_by`, `last_reviewed`.

## 3. Violation Identity — the Hard Part

A baseline is only as honest as its identity. If the identity is "file + line number", the baseline
becomes a permanent mute: insert one line at the top of the file and every acceptance shifts to the
wrong violation, or stops matching and floods the gate.

Identity options, weakest to strongest:

| Identity | Survives | Breaks when | Verdict |
|---|---|---|---|
| file + line | nothing | any line shift | never use for a baseline |
| file + rule + violation text | line shifts | formatting, a rename of the value, a message change | acceptable for simple rules |
| file + rule + **context block** (3 lines before/after) | line shifts, nearby edits | the surrounding code changes | strong default |
| normalized AST node hash | formatting, comments, line shifts | a real structural change | strongest where a parser exists |
| whole-file hash | line shifts | any edit anywhere in the file | too coarse; hides new violations |

The context-block model is the one used by chekr's planned safe-violations database (F-09): a safe
record stores the violating line plus up to three lines before and after, and matches only when the
file path, check id, and the entire block are identical. If the surrounding code changes — even one
line — the acceptance lapses and the violation surfaces for review. That is the right bias: the
thing that was reviewed was a specific block of code, not a coordinate.

Practical rules:

- **Normalize before hashing.** Trim trailing whitespace, normalize line endings, and exclude the
  volatile parts of the message (counts, durations). Otherwise the fingerprint changes for reasons
  unrelated to the code.
- **Include the rule id and a schema version in the fingerprint.** A rule that changes what it
  matches must not inherit the old acceptance.
- **Do not fingerprint generated files.** Exclude them by path and gate the generator instead.
- **Keep the fingerprint stable across renames when the content is the same** (content hash), or
  accept that a rename re-opens the review. Both are defensible; pick one and document it.

## 4. Ratchet Rules

The ratchet is a comparison, not a promise. Identity decides acceptance; counts measure the debt:

```text
for each current violation:
    identity = (rule, file, normalized context block)
    if identity matches an accepted baseline entry: accept and count it
    else: FAIL — a new violation, even in an already-baselined file

for each accepted baseline entry:
    if current count > recorded count: FAIL — the accepted block grew
    if current count < recorded count: update the entry downward (reviewed)
    if current count == 0: remove the entry (reviewed)

if total accepted > baseline total: FAIL — a policy change, not a fix
```

Rules that make it work:

- **New violations fail immediately.** The baseline protects only the reviewed entries; a new file,
  a new rule, or a new violation in an already-baselined file is not covered.
- **The baseline only moves down.** A PR that increases a baseline is a policy change, not a
  maintenance edit; it needs a reason and an approver.
- **Never regenerate the baseline automatically in CI.** `--write-baseline` on every run is how the
  baseline becomes "whatever the code does today." Generation is a reviewed command run by a person.
- **Remove entries when the violation disappears.** A baseline with stale entries is a misleading
  count and a future false negative.
- **Per-area baselines, not one central file.** A single file becomes a merge-conflict magnet and a
  place where ownership disappears. One allowlist per rollout area keeps the owner local.
- **Expire the baseline.** At `expires`, the CI job fails until the baseline is renewed with a new
  date and a new reason, or deleted. Renewal is a decision, not a calendar event.

## 5. Baseline Storage

- **Store it in the repository, versioned with the code.** A baseline on a developer's machine is
  not a team decision.
- **Store one file per rule or per area.** `gates/baselines/<rule>.yaml` is easy to review and easy
  to delete.
- **Protect it like the gate.** CODEOWNERS, required review, and its own diff. An agent or author
  who can silently edit the baseline can pass any gate.
- **Keep the schema boring.** YAML or JSON with a version field; no executable baseline files. A
  baseline that runs code is a gate with a supply-chain problem.
- **Record the tool version.** A rule upgrade can invalidate every entry; the review should be
  explicit, not a surprise flood.

## 6. Suppressions — Scope and Syntax

A suppression is a local, code-level acceptance. It is appropriate for a specific, permanent
exception that is best understood next to the code. It is not appropriate for a whole file, a whole
repository, or a class of violations that should be baselined.

Pick one syntax and teach it:

```text
// gates-ignore-next-line design/no-raw-color -- brand mark uses the official color; owner: design; exp: 2027-01-01
// gates-ignore design/no-raw-color -- same-line exception with a reason
/* gates-disable design/no-raw-color -- generated vendor table; see gates/vendor.md */
/* gates-enable design/no-raw-color */
```

Rules:

- **Name the rule.** `ignore all` is a red flag; a suppression that names one rule cannot hide the
  next rule someone adds.
- **Require a reason on the same line.** A suppression without a reason is indistinguishable from a
  mistake. A meta-check can enforce the pattern.
- **Prefer next-line over block over file.** The narrower the scope, the less it can hide. File-level
  disables need an owner and a review.
- **Never suppress the canary.** A suppression inside the gate's own fixtures or tests disables the
  evidence that the gate works.
- **Treat the suppression diff as code.** A suppression added in the same commit as the violation is
  a finding in review, especially when the author is an agent.
- **Count them.** A rising suppression count means the rule, the code, or the exception process is
  wrong.

## 7. Exceptions — Risk Acceptance with a Clock

An exception is not a suppression. It is a decision by the person who owns the risk:

```yaml
# gates/exceptions.yaml
- id: EXC-014
  rule: security/no-eval
  scope: src/vendor/pdf-renderer/**
  reason: "Third-party renderer requires eval; sandboxed in a worker with no network."
  approved_by: security-team
  ticket: SEC-221
  compensating_control: "Worker CSP, no DOM access, no network; monitored by the runtime guard."
  created: 2026-11-10
  expires: 2027-02-10
  review: 2027-01-10
```

Required fields: rule, scope, reason, approver, ticket, compensating control, created, expires,
review. Optional: severity, affected environments, evidence link.

Who approves:

- **Security** exceptions: the security owner, never the author.
- **Architecture** exceptions: the architect or the module owner.
- **Design-system** exceptions: the design-system owner.
- **Product** exceptions: the product owner.
- **Emergency bypass:** the platform's protected environment, with a ticket and a postmortem; not a
  variable the caller sets.

Time boxes:

- Default 90 days for a design or architecture exception; 30 days for a security exception unless a
  compensating control justifies longer.
- Renewal is a new approval with a new date and a fresh justification. "Still not fixed" is not a
  reason; the compensating control is.
- An expired exception is a failure, not a warning. The CI job that checks expiry is part of the
  gate.

## 8. Expiry Enforcement

An exception register without an expiry job is a diary. Add a small check to T2 or T3 (and nightly):

```text
gates exceptions --fail-on-expired --fail-on-missing-owner
```

It fails when:

- an exception is past `expires`;
- an exception has no approver or no ticket;
- a suppression has no reason;
- a baseline is past `expires`;
- a baseline entry has no owner or no ticket.

The message names the exception id, the rule, the owner, and the date. The fix is a renewal, a
remediation, or a deletion — not a silent extension.

## 9. Migration — Observe, Warn, Baseline, Ratchet, Block

Do not flip a legacy codebase to "block" on day one. A phased rollout is how the gate survives
contact with reality:

| Phase | Duration | Behavior | Exit criterion |
|---|---|---|---|
| **0. Observe** | 1–2 weeks | run the check, report only; no baseline | volume measured, false positives sampled |
| **1. Warn** | 1–2 weeks | visible in the PR, non-blocking; tune the rule | false-positive rate near zero at the intended tier |
| **2. Baseline + block new** | at the gate's start | snapshot legacy; new violations fail | baseline reviewed, owner named, target set |
| **3. Ratchet** | per sprint | baseline count decreases on schedule | target reached or debt explicitly re-scoped |
| **4. Steady** | ongoing | new violations fail; exceptions only | baseline at target, expiry jobs green |

At every phase, announce the promotion date and the owner. A gate that appears overnight with 400
red findings is a gate that gets disabled by Friday.

## 10. Metrics

| Metric | Question it answers | Healthy direction |
|---|---|---|
| baseline count | is the debt shrinking? | down to target |
| suppression count | are people working around the rule? | flat or down |
| exception count and age | is risk acceptance temporary? | small and young |
| bypass count | is the gate too slow or too noisy? | zero, or each one reviewed |
| time-to-fix | is the feedback actionable? | days, not months |
| false-positive sample | is the rule trustworthy? | near zero at blocking tier |
| baseline renewal count | is the debt being re-scoped forever? | rare, with a reason |

A baseline that grows after the gate starts blocking is a signal to investigate the rule's scope,
the review process, or the code's ownership — not to regenerate the baseline.

## 11. Anti-patterns

| The shortcut | The documented cost |
|---|---|
| Baseline keyed by line number | line drift turns the baseline into a mute button or a flood |
| `--write-baseline` in CI | the baseline becomes "today's code"; the ratchet never ratchets |
| Bumping the baseline to merge | a policy change disguised as maintenance |
| One central baseline file | merge conflicts and no local ownership |
| Baseline for a security rule | the debt is a vulnerability with a permission slip |
| Exception without an expiry | a permanent policy change nobody approved |
| Exception approved by the author | the risk owner is not in the room |
| `ignore all` suppression | hides the next rule someone adds |
| File-level disable as the default | every future violation in the file is invisible |
| Suppressing the canary | the gate's own evidence is disabled |
| Stale baseline entries | the count lies and a future violation hides behind a dead entry |
| "Fix later" ticket with no date | the backlog is not a plan |
| Renewing an exception without a compensating control | the risk was never actually managed |
| Treating the baseline as a prioritized TODO list | it is a debt record, not a roadmap |
