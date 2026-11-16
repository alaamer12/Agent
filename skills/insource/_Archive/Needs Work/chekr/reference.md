# Chekr reference — SNDUK

Deep reference for `.cursor/skills/chekr/SKILL.md`. CLI version: **@chekr/cli v0.3.2**.

---

## Layout

```
.chekr/
├── checks/              check_*.js — one export per rule
├── check_functions_duplications/   pipeline for functions_duplication
└── (support helpers colocated in checks/)
chekr.config.js          steps, scopes, cache, ignoreMarker
.chekr-cache/            result cache (gitignored)
violations.json          audit output (gitignored, repo root)
docs/CHEKR.md            human-oriented overview
```

---

## Active steps (`chekr.config.js`)

| Step | ID | Scope (summary) | Notes |
|------|-----|-----------------|-------|
| 2 | `unknown_cast` | `apps/`, `packages/`, `capabilities/` | `as unknown` patterns |
| 3 | `unused_params` | same | Unused function params |
| 4 | `react_srp` | `apps/`, `packages/shell/` | Component size / SRP |
| 5 | `react_handlers` | `apps/`, `capabilities/` | Handler lifecycle / data flow |
| 6 | `duplicate_interfaces` | `apps/`, `packages/` | Duplicate TS interfaces |
| 7 | `typia_validation` | `apps/`, `packages/` | Typia validator usage |
| 8 | `tsconfig_paths` | `apps/`, `capabilities/` | Manual workspace path aliases |
| 9 | `literal_unions` | `apps/`, `packages/` | String literal unions → enums |
| 10 | `mixed_concerns` | `apps/web/components/` | tRPC in presentation components |
| 12 | `functions_duplication` | `apps/`, `packages/` | `optimize: true` repo-level dedup |

**Commented out (present on disk, not in pipeline):**

| ID | Reason |
|----|--------|
| `reinvented_hooks` | Legacy — disabled in config |
| `code_duplication` | Legacy — disabled in config |

Run `bunx chekr list` for the live discovery order (may differ from `step` numbers in config).

---

## Ignore matrix

`buildIgnoredLines` from `@chekr/cli/utils` — **block-only** (`@chekr-ignore-start` / `@chekr-ignore-end`). Default marker matches `chekr.config.js` → `ignoreMarker: "@chekr-ignore"`.

### Honors ignores (`import { buildIgnoredLines } from "@chekr/cli/utils"`)

| Check file | ID |
|------------|-----|
| `check_unknown_cast.js` | `unknown_cast` |
| `check_unused_params.js` | `unused_params` |
| `check_react_srp.js` | `react_srp` |
| `check_react_handlers.js` | `react_handlers` |
| `check_duplicate_interfaces.js` | `duplicate_interfaces` |
| `check_typia_validation.js` | `typia_validation` |
| `check_literal_unions.js` | `literal_unions` |
| `check_mixed_concerns.js` | `mixed_concerns` |
| `check_code_duplication.js` | `code_duplication` (disabled) |
| `check_reinvented_hooks.js` | `reinvented_hooks` (disabled) |

Verify: `rg buildIgnoredLines .chekr/checks/`

### Does NOT honor line ignores

| Check | Why |
|-------|-----|
| `functions_duplication` | Repo-level AST mesh; compares functions across files — no per-line ignore hook |
| `tsconfig_paths` | Validates `tsconfig.json` structure, not application source lines |

For `functions_duplication`, fix by extracting shared utilities. For `tsconfig_paths`, fix `extends` / `paths` to use workspace package names.

---

## Ignore handler behavior (`@chekr/cli/utils`)

Source: `node_modules/@chekr/cli/utils/src/ignore-handler.js`

| Case | Suppressed? |
|------|-------------|
| Lines strictly between start and end markers | Yes |
| `// @chekr-ignore-start` on its own line | No (marker line only) |
| `code // @chekr-ignore-start` | Yes (that line) |
| `{/* @chekr-ignore-start */}` inside JSX | No (marker line only) |
| `<div> {/* @chekr-ignore-start */} ...` | Yes (inline with code) |
| Start + end on same line with code | Yes |
| Unclosed start | Yes through EOF |
| Nested starts | No nesting — first end closes block |

JSX and `//` comment styles are both supported. Optional dashes: `// ---------- @chekr-ignore-start`.

Override marker per call: `buildIgnoredLines(lines, { marker: "@chekr-ignore" })`.

CLI override: `chekr run --ignore-marker @custom-ignore` (must match check usage).

---

## Config highlights (`chekr.config.js`)

```js
{
  checksDir: "./.chekr/checks",
  include: ["**/*.{js,jsx,ts,tsx}"],
  exclude: ["**/__tests__/**", "**/*.test.*", "**/*.spec.*", "**/*.stories.*", "**/__mocks__/**", ".chekr/**"],
  gitignore: ".gitignore",
  bail: true,
  parallel: true,
  concurrency: 4,
  ignoreMarker: "@chekr-ignore",
  cache: true,
  cacheDir: ".chekr-cache",
  steps: [ /* see table above */ ],
}
```

Per-step overrides: `extensions`, `scope`, `exclude`, `optimize`.

---

## Cache and prune

**Structure:** `.chekr-cache/<hash>/steps/<check-id>.json`

| Command | Effect |
|---------|--------|
| `chekr prune all` | `rm -rf .chekr-cache` |
| `chekr prune <check-id>` | Delete that check's cache files in all hash folders |
| `chekr prune <step-number>` | Resolves step → check id via config, then prunes |
| `chekr run --clear-cache` | Remove cache before run |
| `chekr run --no-cache` | Disable cache for one run |
| `chekr run --keep-on` | Skip large-diff cache invalidation prompt (used in audit) |

Root alias: `bun run chekr:prune [target]`.

**When to prune:** check logic changed, false positives fixed in rule code, ignore blocks added/removed, or results contradict `git diff`.

---

## `violations.json` schema (audit reporter)

Produced by `check-violations:audit` / `chekr:audit`.

```json
{
  "passed": false,
  "violations": [
    {
      "rule": "mixed_concerns",
      "severity": "error",
      "message": "TRPC_IN_COMPONENT: ...",
      "logicalId": "mixed_concerns:TRPC_IN_COMPONENT",
      "metadata": {},
      "locations": [
        { "file": "apps/web/components/foo.tsx", "line": 42, "text": "...", "label": "primary" }
      ]
    }
  ],
  "summary": { "...": "..." }
}
```

Violations are **grouped** by `logicalId` or `checkId:message`. Each group has multiple `locations`.

**Per-package split:** `.cursor/skills/chekr/scripts/split-violations-by-package.mjs` buckets `locations[].file` by first two path segments (`apps/web`, `packages/api`, etc.).

---

## CLI command reference

```
chekr [command] [options] [path]

Commands:
  run        Run checks (default)
  list       List discovered checks
  validate   Validate check/fix file contracts
  init       Scaffold .chekr/ and chekr.config.js
  prune      Delete cache (all | step-number | check-id)
  publish    Publish check to marketplace
  install    Install check from marketplace
  fix        Run fixers (not yet implemented)

Options (selected):
  --no-bail              Continue after failures
  --reporter json|default|compact
  --report <file>        Write JSON report
  --only <ids>           Comma-separated check ids
  --skip <ids>
  --changed / --staged   Limit to git diff
  --concurrency <N>
  --no-parallel
  --clear-cache / --no-cache
  --keep-on
  --ignore-marker <s>
  --config <file>
```

---

## Check authoring contract

Each `check_*.js` must export a camelCase function derived from the filename:

| Pattern | Export | When |
|---------|--------|------|
| `check_foo.js` | `checkFoo(filePath, content)` | Per-file |
| `check_foo.js` | `checkFooRepo(scanPath, files, onProgress, context)` | `optimize: true` in config |

Return `Violation[]` or empty array. Use `@chekr/types` / engine types for shape.

Validate: `bun run chekr:validate`.

**Utilities:**

```js
import { buildIgnoredLines, walkFiles } from "@chekr/cli/utils";
import { createMeshOptimizer } from "@chekr/cli/mesh";
import { run } from "@chekr/cli/engine"; // programmatic
```

---

## Remediation patterns (by check family)

| Family | Typical fix |
|--------|-------------|
| `mixed_concerns` | Move `trpc.*.useQuery` to `apps/web/hooks/` or colocated `use-*.ts` |
| `react_handlers` | Split orchestration vs presentation; fix effect fetch |
| `react_srp` | Extract subcomponents / hooks; reduce LOC |
| `unknown_cast` | Narrow types; fix upstream typing |
| `unused_params` | Remove or prefix with `_` if required by interface |
| `duplicate_interfaces` | Consolidate to shared type module |
| `literal_unions` | Promote to `enum` or `as const` object |
| `typia_validation` | Add/fix Typia validators at boundaries |
| `functions_duplication` | Extract shared helper module |
| `tsconfig_paths` | Use `workspace:*` deps + package `exports` |

---

## SNDUK policy

From `.cursor/commands/clean-up.md`:

- Fix violations at source; no suppressions by default.
- `@chekr-ignore` only for genuine false positives — document why.
- `check_mixed_concerns` is an architecture gate for web → mobile shared logic.
