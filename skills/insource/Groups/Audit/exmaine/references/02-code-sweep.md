# The static code sweep

Reading the code the way the docs taught you to read it — with names, purposes, and pointers
already known. Everything here is provable from files alone; anything that needs execution is
recorded as a runtime unknown, not a conclusion.

## Sweep map

1. **Entry points.** From manifests: declared scripts/binaries, main modules, app bootstrap
   ([package.json "scripts"/"bin"], [composer.json], [Program.cs / MauiProgram.cs], [main.dart],
   [src/main.ts]). Read the bootstrap and follow what it wires — the wiring is the truth of the
   runtime graph, statically.
2. **Module inventory.** List the real directories/modules and diff against the docs' units
   catalog: code with no doc claim = **orphan**; doc claim with no code = **unimplemented**.
3. **Import/wiring check.** For each ledger claim about structure, scan imports/references:
   layer rules ("UI never touches DB"), single-owner services ("only module X writes table Y"),
   dead modules (imported nowhere), circular pulls. Patterns, not judgment: quote file:line for
   every violation found.
4. **Configuration surface.** Env var names (`.env.example`, config classes, read sites) —
   presence and consumers only. Secret *values* are never opened or reported; if a real secret
   file sits in-tree, that is itself a finding (leak risk), recorded by path only.
5. **Dependency manifests.** What the project declares it runs on; obvious drift signals
   (declared-but-unused candidates, referenced-but-undeclared imports) are findings *with the
   static-evidence caveat* — "no import found in tree" is proof, "unused" needs more.
6. **CI/CD as written.** Read workflow definitions: what the project *intends* to run for
   tests/build/deploy. Their presence is evidence of intent; never evidence of passing. (The
   passing question is a runtime unknown unless a run artifact exists in-tree, e.g. reports.)
7. **Tests as written.** Inventory test files, what they claim to cover, and whether the
   code-under-test exists with the names the tests import. A test importing a removed module is
   a certain break found statically. Never run the suite.

## Evidence levels (static-only ladder)

For every "does it work/hold" question reached during the sweep, record the level reached:

```text
E0  doc claims it            (nothing else seen)
E1  file exists              (the named module/route/function is present)
E2  wired                    (bootstrap/router/registry actually pulls it in)
E3  used / reachable         (call sites or routes reference it; consumers exist)
E4  statically consistent    (inputs/outputs, types, config keys all line up across files)
E5  —                        (execution would be needed to go further: runtime unknown)
```

E1 without E2 is the classic "file existing is not proof" case. The overview reports levels; it
never upgrades a level by assumption. "Passes" in an exmaine report means E4-consistency,
explicitly *not* green tests.

## What counts as a finding

- Contradiction between a doc claim and quoted code (both sides cited).
- Broken/stale pointers carried from the doc chain.
- Wiring gaps: module exists but nothing imports it; route declared but handler absent.
- Consistency hazards: same constant defined twice with different values; config name read
  nowhere / used but never declared.
- Secrets or ignore-file mismatches (file tracked in git that .gitignore claims to exclude).

Not findings: style opinions, refactor suggestions, "would be better" — exmaine reports facts
and leaves judgment to the user or other skills.

## Runtime-unknowns list

Anything only execution can settle — does the test suite pass, does the server boot, does the
migration run, real API behavior — goes into one honest list with the command *the project
declares* for it (from manifests/CI, quoted, not run). `/exmaine full` ends by handing that list
to the user, and stops there: no offering to run it, no guessing outcomes.
