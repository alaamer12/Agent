# Fatal-termination analysis: <app> <version> - <date>

## 1. Bottom line (3 sentences max)
<What died, why (with confidence), what to do. Use the grade words: Observed / Inferred / Untested.>

## 2. Classification
Class: <A deliberate abort | B hard fault | C unhandled exception | D resource | E external kill | F hang-kill | G clean | H loader | I system>
Basis: <exit code / exception code / dump present? / event log> (grade E1/E2)

## 3. Timeline
| time | source | event |
|---|---|---|
Last sign of life: <time, source>  ·  Time of death: <time, source>  ·  Gap: <duration> -> <covered / instrumentation hole>

## 4. Evidence ledger (key rows; full ledger in evidence-ledger.md)
| ID | Fact | Grade | Source | Rules in / out |
|---|---|---|---|---|

## 5. Causal chain (each link graded)
1. <trigger> [E?] -> 2. <mechanism> [E?] -> 3. <fatal event> [E?] -> 4. <symptom> [E?]
Weakest link: <which, why>
Alternatives considered: <alt> - <what evidence separated it>

## 6. What is proven / inferred / untested
- Proven: ...
- Inferred (because ...): ...
- Untested (test: ...): ...
- Could not read: <artifact, reason>

## 7. Fix
| Layer | Change | Verification rung reached | Status (Observed / Reasoned / Untested) |
|---|---|---|---|
| Remove cause | | | |
| Contain | | | |
| Observe | | | |

## 8. If it happens again, collect
<files/commands>

## 9. Plain-language explanation (for the user)
<Analogy first, then precise statement. Mention any term they asked about.>
