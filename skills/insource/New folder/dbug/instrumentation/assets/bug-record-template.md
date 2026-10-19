# Bug record: <short title — what broke and why, e.g. "orders empty after deploy: cache not invalidated">

Date: <yyyy-mm-dd> · Status: resolved | mitigated-open | wontfix
Session: <who/what agent, linked PR/commit(s)>

## Symptom
- Expected vs actual: <one sentence>
- Environment: <prod/staging/local · service · version/SHA>
- Repro rate & conditions: <always | 1-in-N | only-tenant-X | since <deploy/date>>
- Reproduction: <exact steps / `tmp/repro.sh` / "not reproducible — see evidence">

## Known-good ↔ known-bad
- good: <commit/date/deploy> · bad: <commit/date/deploy> · delta: <what changed between>

## Pipeline map
```
<entry> → <hop> → <hop> → <failure point>     (this bug's actual path)
```
- First invalid state: <where actual diverged from expected — the find>

## Hypotheses

| # | Hypothesis | Prediction if true | Experiment | Result | Verdict |
|---|---|---|---|---|---|
| H1 |  |  |  |  | confirmed / refuted |
| H2 |  |  |  |  |  |

## Root cause
<defect → infection → propagation → failure, in plain words — the chain,
not just "the bug was in X.py">

## Fix
- Changed: <files/layers> — why this is root-cause-level, not symptom-level
- Made structurally impossible at layers: <entry guard / domain check / DB constraint / type>

## Regression protection
- Test: <path::test-name> (failed pre-fix, passes post-fix | why untestable instead)
- Monitoring added: <alert/log/metric | none — why not>

## Prevention / open items
- <process fix: checklist, migration guard, CI rule | none>
- Instrument promoted: <instruments/… | none>
- Procedure captured: <how-to-do entry ID | not generalizable>
