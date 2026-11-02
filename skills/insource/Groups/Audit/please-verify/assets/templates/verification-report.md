# Verification report — template

```markdown
# Verification report — <project / scope>

**Verdict:** COMPLETE & VERIFIED | INCOMPLETE | UNVERIFIED | BROKEN
**Verified against:** <baseline source: conversation / IDEA.md / plan / AGENTS.md - with dates>
**Scope:** <what was in scope> · **Not reached:** <what was not>
**Environment:** <where the runs happened - OS, runtime versions, device/emulator>
**Time box:** <budget spent, or "not set">

## The bar (definition of done used)

1. <requirement> — evidence level required: <L1..L4>
2. …

## Evidence table

| # | Requirement | Artifact / where | Evidence (command + result) | Level | Status |
|---|---|---|---|---|---|
| 1 | App builds | repo root | `[build]` -> exit 0, log line … | L1 | PASS |
| 2 | App launches | … | `[run]` -> boot log …, screenshot … | L3 | PASS |
| 3 | Add-item flow | … | … | L4 | PASS |
| 4 | Empty-state copy | … | not run | - | UNVERIFIED |

## Blockers

- <what stops "done", each with the evidence that shows it>

## Missing proofs

- <claim still unproven, what would prove it, who can produce it>

## Risks and unverified assumptions

- <what the verdict rests on that could change - environment gaps, sampled areas, stale data>

## Outside the baseline (observations, not verdict input)

- <things noticed that the bar did not require>

## Next actions, in order

1. <smallest action that raises the weakest deciding level>
2. …
```

## Writing rules

- The verdict line is one of the four labels - no adjectives, no "mostly". Mixed evidence narrows the
  verdict, it does not soften the label.
- Every PASS row quotes a command and its result; every non-PASS row says what is missing.
- Findings outside the baseline are listed but never decide the verdict.
- No fixes, no refactor suggestions beyond the minimum action needed to reach evidence. The report is the
  deliverable.
