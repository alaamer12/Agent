---
name: chekr
description: >-
  Run and remediate SNDUK Chekr architectural checks (@chekr/cli v0.3.2).
  Use when fixing check-violations, writing custom .chekr/checks, using
  @chekr-ignore blocks, pruning cache, auditing violations.json, or
  parallel per-package remediation.
---

# Chekr — SNDUK architectural checks

Custom static analysis for this monorepo. Rules live in `.chekr/checks/`; config in `chekr.config.js`. CLI: **@chekr/cli v0.3.2**.

**Read [reference.md](reference.md)** for the full check catalog, ignore matrix, cache/prune details, and `violations.json` schema.

---

## When to use this skill

| Task | Action |
|------|--------|
| Quality gate / clean-up step 1 | `bun run check-violations` until exit 0 |
| Full audit for parallel fix | `bun run check-violations:audit` → `violations.json` |
| Rule contract / new check | `bun run chekr:validate` |
| Stale cache after big refactor | `bun run chekr:prune all` or per-step prune |
| Split work across agents | Run audit script, then one agent per package slice |
| Add suppression | Block-only `@chekr-ignore-start` / `@chekr-ignore-end` (see below) |

Also read `.cursor/commands/clean-up.md` when Chekr is step 1 of the full pipeline.

---

## Repo scripts (root `package.json`)

| Script | Command | Purpose |
|--------|---------|---------|
| `check-violations` | `chekr run` | Default gate — bail on first failing step |
| `check-violations:audit` | `chekr run --no-bail --keep-on --reporter json --report violations.json` | All steps, JSON report at repo root |
| `chekr` | alias of `check-violations` | Same as above |
| `chekr:audit` | alias of `check-violations:audit` | Same as above |
| `chekr:validate` | `chekr validate` | Validate check file contracts |
| `chekr:prune` | `chekr prune` | Delete cache (see Cache) |

Human docs: [docs/CHEKR.md](../../../docs/CHEKR.md).

---

## Quick workflow — fix violations

1. **Run** from repo root: `bun run chekr`
2. **Read** the failing step ID, file, line, and message
3. **Fix at source** — extract hooks, remove casts, dedupe types, etc.
4. **Re-run** until exit 0
5. **Do not** add `@chekr-ignore` unless the violation is a documented false positive (explain in PR/summary)

After large diffs or suspicious stale results: `bun run chekr:prune all`, then re-run.

---

## Ignore blocks (block-only)

**No single-line ignore.** Only paired block markers (immune to formatter line breaks).

Configured marker: `@chekr-ignore` (`ignoreMarker` in `chekr.config.js`).

```ts
// @chekr-ignore-start
const legacy = somethingWeCannotRefactorYet();
// @chekr-ignore-end
```

```tsx
{/* @chekr-ignore-start */}
<div className="legacy">{children}</div>
{/* @chekr-ignore-end */}
```

Rules:

- Directive-only lines are **not** suppressed; lines **between** start/end are.
- Inline directives on the same line as code **do** suppress that line.
- Unclosed `start` suppresses to EOF.
- Legacy `@symphony-ignore` still works inside checks that pass a custom marker — prefer `@chekr-ignore` in this repo.

**Which checks honor ignores:** see [reference.md § Ignore matrix](reference.md#ignore-matrix). Summary: all per-file AST/line checks use `buildIgnoredLines` from `@chekr/cli/utils`; **repo-level** `functions_duplication` and **tsconfig** `tsconfig_paths` do **not**.

---

## Parallel per-package remediation

For large violation sets, audit once then fan out by monorepo package:

### 1. Generate report

```bash
bun run check-violations:audit
```

Produces `violations.json` at repo root (`passed`, grouped `violations[]` with `rule`, `message`, `locations[]`).

### 2. Split by package

```bash
bun run .cursor/skills/chekr/scripts/split-violations-by-package.mjs violations.json
```

Writes `scratch/chekr-by-package/<slice>.json` (e.g. `apps-web.json`, `packages-api.json`, `_root.json`).

### 3. Assign workers

One agent per slice with **non-overlapping** file ownership:

| Slice prefix | Typical owner scope |
|--------------|---------------------|
| `apps-web` | `apps/web/**` only |
| `apps-admin` | `apps/admin/**` only |
| `apps-mobile` | `apps/mobile/**` only |
| `apps-backend` | `apps/backend/**` only |
| `packages-*` | matching `packages/<name>/**` |
| `_root` | `chekr.config.js`, root configs |

Each worker:

1. Reads only their slice JSON
2. Fixes listed `locations[].file` paths
3. Re-runs `bun run check-violations` locally before handoff (or scoped `--only <check-id>` if known)

Orchestrator merges when all slices are clean. Prefer `/pool-agents` or `up-agents` notation from `AGENTS.md` for fan-out.

---

## Cache and prune

| Setting | Value |
|---------|-------|
| `cache` | `true` |
| `cacheDir` | `.chekr-cache` |
| `parallel` | `true`, `concurrency: 4` |

```bash
bun run chekr:prune all              # wipe entire .chekr-cache
bun run chekr:prune mixed_concerns   # one check id
bun run chekr:prune 10               # step number from chekr.config.js
chekr run --clear-cache <DONT do it, only user the user can do it>             # delete cache dir before single run
chekr run --no-cache                 # skip cache reads/writes for one run
```

Prune after changing check logic, ignore rules, or when cache and git state disagree. `--keep-on` on audit skips large-diff cache invalidation countdown.

---

## CLI essentials (`bunx chekr`)

```bash
bunx chekr list                      # discovered checks
bunx chekr validate                  # contract check
bunx chekr run --only mixed_concerns # single step
bunx chekr run --skip functions_duplication
bunx chekr run --changed             # git diff files only
bunx chekr run --staged
bunx chekr --help
```

Version pinned in root `devDependencies`: `@chekr/cli@^0.3.2`.

---

## Thin-wrapper suppression (`check_functions_duplication`)

Named functions with **fewer than 5 logical statements** (a multiline `return trpc.*.useQuery(...)` counts as one) are thin wrappers. When **both** sides of a pair are thin wrappers but call **different** tRPC procedures, the finding is suppressed (e.g. `useFundPerformanceSummaries` vs `useFundPerformanceData`).

- Logic: `.chekr/check_functions_duplications/thin-wrapper.js` (wired in `pipeline.js`)
- Tests: `bun test .chekr/check_functions_duplications/thin-wrapper.test.mjs`
- Anonymous callbacks (e.g. shared `onSuccess` invalidation blocks) are **not** exempt

---

## Writing / editing checks

1. Add `check_<id>.js` under `.chekr/checks/` exporting `check<Id>(filePath, content)` or `check<Id>Repo` for `optimize: true` steps.
2. Register step in `chekr.config.js` (`id`, `step`, `scope`, `extensions`).
3. Run `bun run chekr:validate`.
4. For line-level rules, import and use ignores:

```js
import { buildIgnoredLines } from "@chekr/cli/utils";

const ignored = buildIgnoredLines(content.split("\n"));
if (ignored.has(lineNum)) return;
```

5. For O(N²) repo checks: set `optimize: true`, implement `*Repo`, use `createMeshOptimizer` from `@chekr/cli/mesh`.

---

## Verification checklist

Before reporting done:

- [ ] `bunx chekr list` lists expected checks
- [ ] `bun run chekr:validate` passes
- [ ] `bun run check-violations` passes (or audit slice clean)
- [ ] New suppressions use block form only and are justified

---

## Related skills

| Situation | Also read |
|-----------|-----------|
| Full quality gate | `code-review-and-quality` + `.cursor/commands/clean-up.md` |
| React boundary fixes | `frontend-ui-engineering`, `api-and-interface-design` |
| Parallel workers | `up-agents` or `AGENTS.md` pool notation |
