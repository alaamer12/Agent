# Triage — reading order for a diff you cannot read top to bottom

A large diff is not a large task if you read it in the right order. The order below is about **where behaviour
lives**, not where files sort.

## Size decides the method, not the effort

| Size | Method |
|---|---|
| ≤ 10 files, ≤ 300 lines | read every hunk, in risk order |
| 10–50 files, ≤ 2 000 lines | survey, skip generated/lockfiles, read the rest grouped by concern |
| 50+ files or 2 000+ lines | **review by commit**, not by range: `git log --reverse --format='%h %s'` then `git show <sha>` each; or split by directory with `--stat`/`--dirstat` |
| A lockfile or minified bundle dominates | `git diff -- . ':(exclude)*.lock' ':(exclude)dist/**'`; read the manifest that produced it |

When the diff is regenerated output, the information is the **generator input change**, not the output.

## The reading order

1. **Deletions.** Search the added/removed stream for `^-` lines in non-generated files. A removed guard, a
   removed `try`, a removed test, a lowered timeout — additions announce themselves; deletions do not.
2. **Dependency manifests** (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Gemfile`, `composer.json`)
   — a version bump can explain half the diff, and a **manifest without its lockfile** (or the reverse) is a
   finding.
3. **Migrations, schema, config, CI** — `*.sql`, `migrations/`, `.github/workflows/`, `Dockerfile`, env files,
   feature-flag defaults. These change the environment the code runs in, and are often irreversible.
4. **Core logic** — the files whose hunks contain conditions, error paths, defaults, signatures.
5. **Public surface** — exported functions, API routes, CLI flags, env variables, config keys: anything a
   consumer notices.
6. **Tests** — present? changed to *describe* the new behaviour, or weakened to accept it? A test whose
   assertions were relaxed is the most expensive hunk in the diff.
7. **Generated, vendored, minified** — confirm they match their source; then skip.

## Commands that order the reading

```bash
git diff --dirstat=files,10 <range>           # where the mass is
git diff --stat -M -C <range>                 # names + churn, one screen
git diff -O /tmp/order.txt <range>            # your paths first: tests, manifest, core
git diff <range> -- ':(exclude)*lock*' ':(exclude)dist/**' ':(exclude)vendor/**'
git diff --numstat -M <range> | sort -k1,1nr  # biggest additions first
git diff <range> -- '*.py'                    # one language at a time
git diff -U0 <range> | grep -n '^[+-][^+-]'   # only changed lines: a map, not a read
```

## The risk checklist — what to look for in each hunk

Not "read every line twice"; read with these questions in mind and the dangerous hunks surface.

| Category | The change to notice | Why it matters |
|---|---|---|
| **Error handling** | removed `try`/`catch`/`except`, `?`/`!`, ignored return code, `catch {}` | failures now propagate or disappear silently |
| **Defaults** | constant, timeout, retry count, page size, flag default, sort order | changes behaviour for every caller, in one line |
| **Boundaries** | `<` ↔ `<=`, `&&` ↔ `||`, off-by-one, null/None checks | the classic "works on my data" bug |
| **Order** | reordered statements, `await` added/removed, transaction boundaries | concurrency and atomicity changes hide here |
| **Data** | column type, index, cascade, uniqueness, migration fallback | irreversible at the schema level |
| **Permissions** | mode bits, role checks, `chmod`, file modes `100644`→`100755` | security, not style |
| **Dependencies** | version bump, new transitive dependency, replaced library | supply chain and behaviour drift |
| **Public surface** | signature change, removed export, renamed env var/CLI flag | breaks consumers outside this diff |
| **Tests** | deleted, skipped (`.skip`, `xfail`, `@Ignore`), assertion loosened | the safety net moves, not the code |
| **Secrets / data** | added keys, tokens, personal data, production hostnames | rotate, not "remove in a follow-up" |
| **Noise** | formatting, import reorder, `println`, `debugger`, `sleep`, commented-out blocks | masks the real change or ships debug code |
| **Locales / i18n** | hardcoded strings replacing message keys | regressions in non-English products |

## Structural inconsistencies (the highest-value findings)

A diff is internally consistent only if the **shape** of the change matches its risk:

| This changed… | …without this | Finding |
|---|---|---|
| behaviour in a function | any test file | untested change — ask, or run it |
| a dependency version | the lockfile (or vice versa) | unreproducible build |
| a schema / query | a migration | runtime failure on existing data |
| a public route/flag | documentation, changelog or consumer update | silent breakage |
| a removed file | its imports/usages | dead reference or crash |
| generated output | its source | hand-edited artifact |

`git grep` at the **new** revision for the removed symbol answers the "still referenced?" question in seconds
([`02`](02-searching-diffs.md)).

## Reading moved code without reading it twice

```bash
git diff -M20% -C --color-moved=zebra --color=always <range> | less -R
```

Moves are the main source of false "huge changes". If a block appears twice, the second copy is usually the
move; the interesting part is the difference between them. `--color-moved-ws=allow-indentation-change` keeps
moves visible when the block was re-indented.

## When the diff is too big to be a diff

A 6 000-line change with a one-line message, or a refactor touching every file, is not reviewed hunk by hunk:

1. establish the **claim** (message, PR, ticket);
2. sample the pattern — three representative files — and check it is uniform;
3. check the **exceptions**: files that do not follow the pattern are where the bug is;
4. verify mechanically where possible (tests, build, type check, `git diff -w` for the formatting-only claim);
5. report the sampling explicitly: "reviewed pattern across 3/180 files; deviations: …". Never imply full
   coverage.
