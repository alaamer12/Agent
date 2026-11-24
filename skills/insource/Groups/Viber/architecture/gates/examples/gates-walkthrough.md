# Walkthrough: Applying the Gates Pillar

One pass on a real-shaped application: a bilingual web client and admin console, a Postgres
database, an API, an existing CI pipeline, and agents writing most of the code. The point is the
sequence of decisions, not the framework.

---

## Step 0: Recon (what the agent reads before asking anything)

```text
docs/
├── architecture/
│   ├── language-architecture.md
│   ├── error-architecture.md
│   ├── ui-architecture.md
│   ├── testing-architecture.md
│   └── ...                                    ← 9 documents, 63 binding rules
├── AGENTS.md                                  ← says "follow the design system"
ci/
└── pipeline.yml                               ← lint, unit, build, 3 e2e happy paths
.husky/pre-commit                              ← 78 s: lint + typecheck + unit

findings
────────
· 63 binding rules; 4 are enforced by a check that names them
· 39 eslint-disable, 7 @ts-ignore, 2 file-level disables
· 214 raw hex colors; 61 raw <button>; 300+ emoji in docs and README
· 7 `any`; 12 exported-but-unused functions; 2 installed-but-unused dependencies
· no favicon; no loading, error, or empty pages for 11 of 19 routes
· e2e: 3 happy paths; no console-error assertion; seed covers 4 of 11 tables
· default language literal "ar" in 9 files; no `default` column on translations
· hook takes 78 s; the CI job is optional in branch protection
· 3 of the last 12 agent commits touched the lint config or a failing test
```

The recon output is the interview agenda. Nothing below is asked; it is inferred.

---

## Step 1: Classify the rules

| Rule | Rung | Why | Gate |
|---|---|---|---|
| No literal color outside `tokens/**` | 2 | a hex string is a valid string; types cannot see it | source scan, docs included |
| No raw `<button>` / `<select>` / `<input>` | 2 | AST sees the element, a regex sees comments | AST or `no-restricted-syntax` |
| No Unicode icons in any tracked file | 2 | the agent obeys in code and leaks in README | whole-repo text scan |
| No new `any` / `@ts-ignore` | 1 | the compiler sees it; the escape is the problem | ratchet |
| One default language | 1 + 3 | a literal is legal; the DB fact is cross-file | lint ban + translations census |
| Every route has loading/error/empty states | 3 | a cross-file catalog fact | route census |
| Every route renders with zero console errors | 3 | needs the app running | e2e render health |
| Seed covers every required table | 3 | a census over schema + fixtures | seed check |
| Every widget reads the filter store | 3 | an ownership fact | conformance test |
| Toast copy/severity comes from the catalog | 2 | the primitive accepts any string | AST ban outside the adapter |
| Signup → refresh → still signed in | 3 | a session round trip | e2e |
| No unused exports or dependencies | 3 | a whole-program fact | T3 whole-program check |
| A reset-db script exists and runs | 3 | a file/capability fact | existence + CI run |
| Duplicate domain types | 2 | cross-file shape, not a type error | advisory first, then ratchet |
| Transitions, modal depth, RTL skeletons | 5 | judgment and visual quality | advisory rubric |
| Filter placement makes ownership obvious | 5 | design judgment | advisory rubric |

Notice the honest rows at the bottom. Not every failure becomes a blocking gate; the ones without an
objective oracle are advisory, owned, and reviewed.

---

## Step 2: Tier the checks

| Tier | Checks | Budget |
|---|---|---|
| T1 | format staged 1 s, lint staged 3 s, secret scan 1 s, token check 2 s, primitive check 2 s | **9 s** |
| T2 | typecheck 55 s, full lint 40 s, unit 50 s, conformance 25 s, `any` ratchet 5 s, icon scan 3 s, build 60 s | **4 min** |
| T3 | integration 4 min, e2e smoke 8 min, seed check 10 s, a11y 2 min, bundle 1 min, migration 20 s | **16 min** |
| T4 | full e2e 30 min, mutation 35 min, dependency audit 5 min, performance 10 min | **80 min** |

Decisions:

- The 78-second hook is cut to 9 seconds. Typecheck and unit move to T2; the hook keeps the checks
  that are fast and local.
- The e2e smoke is T3 because it needs the full stack. The render-health test is part of it from day
  one; there is no legacy debt to baseline.
- The whole-program unused-export/dependency check is T3, not T1. It needs the whole graph and it is
  not a per-commit decision.
- Nothing blocks at T0. The editor is a courtesy.

---

## Step 3: Write the cards

### Card A — `design/no-raw-color`

```text
Rule:      No literal color value outside tokens/**.
Why:       A rebrand and a dark theme missed 41 hardcoded colors; the contrast audit failed.
Rung:      2 — source scan (+ Stylelint where available).
Tier:      T1 staged; T2 full.
Command:   bun run gates:colors --changed
Scope:     src/**/*.{ts,tsx,css,html}, docs/**/*.md; exclude tokens/**, **/*.generated.*
Budget:    p95 2.1 s on 214 files.
Failure:   FAILED on any occurrence; ERROR on missing report or empty scope.
Report:    .reports/no-raw-color.json; summary to stderr.
Evidence:  2026-11-18 — injected #ff0000 into src/ui/Button.tsx:12; red with the nearest token;
           reverted; green. Canary: gates/fixtures/no-raw-color/.
Exception: // gates-ignore-next-line design/no-raw-color -- <reason>; file-level needs
           design-system approval; 90-day expiry.
Owner:     design-system
```

### Card B — `repo/no-unicode-icons`

```text
Rule:      No emoji or pictographic Unicode in any tracked text file.
Why:       Agents obey "no icons" in source and write one in the README; 300+ found across docs.
Rung:      2 — whole-repo text scan.
Tier:      T2 (and a pre-commit fast path for changed files).
Command:   bun run gates:icons
Scope:     every tracked text file: code, Markdown, SQL, YAML, templates; binary files excluded.
Budget:    p95 3 s.
Failure:   FAILED on any pictographic character outside the approved punctuation set.
Report:    .reports/icons.json.
Evidence:  2026-11-20 — added "✅" to docs/testing.md; red at line 4; reverted; green.
Exception: none. The fix is to remove the icon or write the word.
Owner:     docs
```

The scope is the whole point. A linter that only sees `src/**/*.ts` would have passed this project
for a year while the README accumulated decoration.

### Card C — `app/render-health`

```text
Rule:      Every route renders with zero console errors, zero unhandled rejections, one h1, and
           no horizontal overflow at 375/768/1280.
Why:       The agent's e2e tests only proved the happy path; a runtime error in a nested widget
           shipped because nothing looked at the console.
Rung:      3 — e2e smoke over the route manifest.
Tier:      T3.
Command:   bun run test:e2e:smoke --grep @health
Scope:     every route in the generated route manifest; admin and web.
Budget:    p95 6 min.
Failure:   FAILED on the first violation; the report names route, console text, and screenshot.
Evidence:  2026-11-19 — a fixture route throws in a child; red with the console message and the
           route; reverted; green.
Exception: none. A flaky route is fixed, not excepted.
Owner:     web
```

The test walks the route manifest rather than a hand-written list, so a new page is covered the day
it appears. It asserts `page.on("console")` for `error` and `warning`, `page.on("pageerror")`, the
framework's error overlay, and `naturalWidth > 0` on images. It is the single highest-value gate in
the project because it catches the class of failure that unit tests and happy-path e2e never see.

### Four compact cards

```text
types/no-new-any
  Rule: no new `any`, `as any`, or `@ts-ignore` outside the declared shim files.
  Rung: 1 (ratchet). Tier: T2. Command: bun run gates:types.
  Baseline: 7 existing; target 0; a new one fails. Owner: platform.

app/route-states
  Rule: every route in the manifest has loading, error, and empty components, or a declared reason.
  Rung: 3. Tier: T2. Command: bun run test:conformance:routes.
  Sanity floor: route count > 15. Owner: web.

tests/full-seed
  Rule: every table required by the e2e suite has at least one row after `bun run db:seed`.
  Rung: 3. Tier: T3. Command: bun run test:seed:check.
  Also asserts `bun run db:reset` exists and runs before seed. Owner: qa.

notify/catalog-only
  Rule: no direct toast call outside the notification adapter; the adapter takes a catalog key.
  Rung: 2 (AST). Tier: T1/T2. Command: bun run gates:notify.
  Exception: third-party embed adapter only. Owner: error-platform.
```

The toast rule is the one that fixes the `ui.notify("coral", pickCopy(...))` failure: the color and
the copy stop being arguments. The adapter accepts `notify({ key: "gateway.refresh.failed" })`; the
catalog owns the copy, the severity, and the icon. The AST rule is three lines and catches the next
one.

### What we deliberately did not gate

- **Modal polish, transitions, RTL skeleton direction, z-index order.** Advisory with a visual
  rubric and a review date. The project could measure a few of them later (a transition-duration
  assertion, a screenshot diff), but a fake gate is worse than an honest advisory.
- **Filter placement.** Advisory: "the toolbar must read as page-level." The durable part — every
  widget reads one filter store — is a conformance test; the visual judgment is review.
- **Type duplication.** Advisory for one quarter while the team measures the real duplicates; then a
  ratchet if the count is stable enough to be meaningful.

---

## Step 4: Baseline and ratchet

The first run finds 214 raw colors and 61 raw buttons. Blocking on all of them would disable the
gate by Friday. The baseline is per area, owned, and scheduled:

```yaml
# gates/baselines/no-raw-color.yaml
rule: design/no-raw-color
tool: gates@1.4.0
created: 2026-11-01
owner: design-system
target: 0
expires: 2027-02-01
reduction: "-25% per sprint"
entries:
  - file: src/legacy/Chart.tsx
    fingerprint: "sha256:9f2c1a…"
    count: 12
    ticket: DS-412
  - file: src/features/reports/Export.tsx
    fingerprint: "sha256:41ab7e…"
    count: 3
    ticket: DS-418
  # … 48 more entries; the 50 entries together carry all 214 occurrences
```

The ratchet:

```text
new file with a raw color          → FAIL
new violation block in a baselined file → FAIL
baselined block with more than N   → FAIL
baselined block with fewer than N  → update the baseline downward (reviewed)
entry with zero current violations → remove it (reviewed)
```

The identity is a context-block hash, not a line number. Moving a file or adding an import does not
shift the acceptance; changing the violating block does, which is exactly when a human should look
again.

The first sprint clears the ten smallest entries — 54 occurrences — which takes the count to 160.
The next two sprints follow the scheduled −25% to 120 and 90. The chart port then removes the last
90 in one change, and the register records the target and the owner, not just the number.

---

## Step 5: Exceptions

Two real exceptions, both narrow:

```yaml
# gates/exceptions.yaml
- id: EXC-003
  rule: types/no-new-any
  scope: src/types/vendor-pdf.d.ts
  reason: "Vendor ships a broken declaration file; wrapped by our own adapter."
  approved_by: platform
  ticket: PLAT-88
  compensating_control: "All calls go through PdfAdapter; no direct vendor types in app code."
  created: 2026-11-10
  expires: 2027-02-10

- id: EXC-004
  rule: repo/no-unicode-icons
  scope: docs/CHANGELOG.md
  reason: "Historical entries quote release notes that contained an emoji; rewriting history is worse."
  approved_by: docs
  ticket: DOCS-31
  compensating_control: "The current release notes are scanned; only the frozen archive is excepted."
  created: 2026-11-20
  expires: 2027-05-01
```

The exception job runs at T3 and nightly:

```text
$ bun run gates:exceptions --fail-on-expired --fail-on-missing-owner
EXC-002 expired 2026-11-15 (owner: web) — renew with a new reason or fix.
exit 1
```

A suppression is not an exception. The inline form is for a permanent, local fact:

```ts
// gates-ignore-next-line design/no-raw-color -- official brand mark color; owner: design; exp: 2027-01-01
const BRAND = "#0B5FFF";
```

---

## Step 6: The agent contract

`AGENTS.md` gets a short, exact section (a sync block with the gates document):

```md
## Gates

- Before claiming done, run `bun run gates` (fast) and `bun run verify` (full). Paste the command
  and the exit code. A non-zero exit is a failure; warnings are not done.
- Do not edit `gates/`, `.github/workflows/`, `gates/baselines/`, `gates/exceptions.yaml`,
  `gates/fixtures/`, or the e2e seed fixtures to make a gate pass. Propose an exception with a
  reason and an expiry instead.
- A diff over 20 files requires the full scan, not `--changed`.
- If a required check cannot run, stop and say so. Do not report success.
- Report path: `.reports/gates.json`.
```

The agent's loop is one command:

```text
$ bun run gates
PASS  design/no-raw-color        214 files   2.1s
FAIL  app/route-states            19 routes  1.4s
      11 routes missing a state: /admin/orders, /admin/reports, …
      fix: add loading/error/empty components or declare a reason in routes.manifest.ts
1 failed, 6 passed — report: .reports/gates.json
```

The agent fixes the eleven routes, reruns, and reports the exit code. The completion hook is the
belt; the written contract is the suspenders.

---

## Step 7: Observe each gate failing

```text
$ bun run gates:colors --changed
src/ui/Button.tsx:12:18  error  design/no-raw-color
  Raw color "#ff0000" outside the token module.
  Impact: breaks the dark theme and the contrast budget.
  Fix: use tokens.color.action.danger (nearest match: danger.500).
exit 1

$ git checkout -- src/ui/Button.tsx
$ bun run gates:colors --changed
PASS  design/no-raw-color  214 files  2.0s
exit 0
```

The canary suite makes the observation repeatable:

```text
$ bun test gates/fixtures/no-raw-color
✓ positive/Button.tsx fails with design/no-raw-color at line 3
✓ negative/Button.tsx passes
✓ the gate exits 1 on the positive and 0 on the negative
```

And the render-health canary:

```text
$ bun run test:e2e:smoke --grep @health
✗ /admin/orders — console.error: "Cannot read properties of undefined (reading 'total')"
  screenshot: .reports/health/admin-orders.png
exit 1
```

Every gate in the register gets a date and a method. A gate whose evidence is older than its last
change is unverified.

---

## Step 8: Wire the pipeline and roll out

```yaml
# shape, not a vendor file
on: pull_request

jobs:
  fast:
    steps:
      - run: bun install --frozen-lockfile
      - run: bun run typecheck
      - run: bun run lint --max-warnings=0
      - run: bun run gates --changed
      - run: bun run test:unit
      - run: bun run test:conformance
      - run: bun run build

  deep:
    needs: fast
    steps:
      - run: bun run test:integration
      - run: bun run test:e2e:smoke
      - run: bun run gates:exceptions --fail-on-expired
```

- Branch protection requires `fast` and `deep`. The workflow runs from the default branch; the pull
  request cannot edit it.
- `gates/**`, `ci/**`, the baselines, the exceptions, and the fixtures are CODEOWNERS-protected.
- Rollout: week 1 observe colors/buttons/routes; week 2 warn; week 3 baseline + block new; week 4
  ratchet. Render health and seed completeness block from day one because there is no legacy debt to
  absorb.
- The advisory list gets a monthly review; the tier budget gets a monthly p95 check.

---

## Step 9: Output

```text
docs/gates-architecture.md
  §2  enforcement ladder              ← the classification table
  §3  tiers and budgets               ← 9 s / 4 min / 16 min / 80 min
  §4  gate register                   ← 41 active, 14 advisory
  §5  baselines and ratchets          ← 214 colors, 61 buttons, targets and owners
  §6  suppressions and exceptions     ← syntax, approvers, expiry job
  §7  agent contract                  ← one command, protected paths, evidence
  §8  failure, bypass, flake policy   ← PASS/FAILED/ERROR/SKIPPED + exit codes
  §9  evidence and canaries           ← date, method, re-verify triggers
  §10 census and metrics              ← rule coverage, false positives, bypasses
  §11 rollout                         ← observe → warn → block → ratchet
  §12 sync points
  §13 open decisions                  ← 8 items
```

Census result: **63 binding rules → 41 gated, 14 advisory, 8 open decisions.** The eight open items
are rules that need a decision (a metric, an owner, or an exception); none is silently defaulted.

Registered in `UNITS.md`: the gate runner, the report type, `no-raw-color`, `no-raw-button`,
`render-health`, `seed-check`, `filter-registry`, `notify/catalog-only`.

Sync points: register ↔ `gates/rules.yaml` ↔ CI; tier table ↔ CI/hook config; baselines ↔
`gates/baselines/*`; agent contract ↔ `AGENTS.md`; report schema ↔ runner/dashboard.

---

## What changed

- The pre-commit hook went from 78 s to 9 s; the bypass path stopped being attractive.
- Five blocking gates protect the failures that actually shipped: build/typecheck, specification
  tests, secrets, dependency policy, and destructive migrations — plus the project's design,
  render-health, route-state, seed, and filter-ownership checks.
- 214 colors and 61 buttons are baselined with owners, tickets, and a shrinking target, not
  grandfathered silently.
- Every gate has a canary and a date. The register, not the prompt, is the source of truth.
- Fourteen rules are explicitly advisory. The project stopped pretending that "clean, accessible,
  polished" was enforced by a sentence in `AGENTS.md`.

The gates did not make the agents smarter. They made the agents' failures visible before a user saw
them, which is the only thing a gate was ever asked to do.
