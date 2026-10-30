# Testing, and telling the truth about it

You are the only agent who can test this asset cheaply: the setup, the data and the failure are still in your
context. A future agent inherits whatever you claim. That is why the rule is blunt: **tested means run, and
unverified means said out loud.**

## 1. Define correct behaviour before running anything

One line per asset, in the card's own words:

```text
Given <input>, it produces <output> and exits <code>.
Given <bad input>, it fails with <message> and exits 2, changing nothing.
```

If you cannot write that sentence, the asset is not ready to test — and probably not ready to store.

## 2. The case matrix

| Case | Why it exists | Minimum |
|---|---|---|
| **Original** | the asset still does what the session needed | 1 run, same input as the session |
| **Variant** | the behaviour is general, not fitted to one example | ≥ 2 runs with different inputs (different file, date, size, table) |
| **Edge** | empty, malformed, missing optional, very large | ≥ 1 (empty or malformed is the cheapest) |
| **Dependency missing** | the failure is clear, not a traceback wall | 1 run with the tool deliberately unavailable |
| **Destructive guard** | nothing is written/deleted without the explicit flag | 1 run in default mode, confirming no side effect |

Skipping a row is allowed; skipping it **silently** is not — the card lists what was not tested.

## 2a. What "test" means per asset form

The case matrix below still applies; what changes is how a case is executed.

| Form | Original case | Variant | Failure/edge case |
|---|---|---|---|
| Script | run it on the session's input | different file, size, date, flag | malformed input, missing dependency, no-write default |
| Command sequence | run the sequence in a sandbox | run it on a second target (different service/branch) | stop midway — does the documented abort condition hold? |
| Procedure | walk the steps in a throwaway environment | walk it with one precondition absent (should refuse, not proceed) | follow the rollback path once |
| Config / template | apply it to a scratch copy and start the service | one placeholder changed to a second valid value | leave a required placeholder unreplaced — the start must fail loudly, not silently |
| Query | run read-only, compare row count/shape to a known answer | different date range / filter | insufficient privileges: clear error, no partial write |
| Pattern / constraint | run the check on code that violates it | run it on compliant code | check on an unrelated file: must not false-positive |

A procedure is verified when its **end state** is observed, not when the steps "look right". A config template is
verified when the service starts with it. A query is verified when its answer matches an independently known
one. "It ran without errors" is not a test for any of them.

## 3. How to test without wrecking the machine

- Run inside a throwaway directory (`mktemp -d` / `$TEMP\bequeath-test-…`), never in the project tree.
- Prefer assets that are read-only by default; if not, use a copy of the input and a `--out` you own.
- For network/API assets: if no sandbox exists, test the argument parsing and the error path, and mark the live
  path `unverified` — do not hit production to "confirm".
- Keep the test inputs with the asset (`tests/fixtures/…`) so the next agent can re-run exactly what you ran.

## 4. Verification status — exactly four values

| Status | Requires | Wording in the card |
|---|---|---|
| `verified (automated)` | a test command that runs the matrix and passes now; its output recorded | `python tests/test_find_slow.py` → `4 passed` (2026-10-28) |
| `verified (manual)` | you ran the matrix by hand; each command and its observed output listed | `--input a.json` → 3 rows; `--input empty.json` → 0 rows, exit 0 |
| `partially verified` | some rows ran; the missing ones are named | tested original + variant; edge and missing-dependency not tested |
| `unverified` | anything less — and a sentence saying why | no Docker here, so the container path was not executed |

Rules:

- **Never invent a higher status.** "Ran once, looks right" is `partially verified` at best.
- A fix made after a failing test requires re-running **that** test and recording the new result. The old result
  is history, not evidence.
- If the user asked you not to run something, the status is `unverified (not run at user's request)` — that is
  an honest outcome, not a failure.
- Do not claim "works across environments" from one machine. Say which environment you used.

## 5. Record it where the next agent looks

In the card, a short block — command, input, observed result, date:

```text
Verification: verified (manual)
  python find_slow.py --input tests/slow.json      -> 3 rows, exit 0
  python find_slow.py --input tests/empty.json     -> 0 rows, exit 0
  python find_slow.py --input tests/broken.json    -> "error: invalid JSON at line 4", exit 2
  python find_slow.py --threshold-ms 0             -> all rows, exits 0   (variant: threshold is honoured)
Not tested: inputs larger than ~100 MB; Windows path handling.
```

The "Not tested" line is the part that saves a future agent from trusting the wrong thing.

## 6. When the test fails

Fix the asset, not the test — unless the test itself was wrong, in which case say so and why. If the fix
changes behaviour that another asset depends on, bump and note it in the final report. Never delete a failing
test to reach green, and never mark a partially fixed asset `verified`.
