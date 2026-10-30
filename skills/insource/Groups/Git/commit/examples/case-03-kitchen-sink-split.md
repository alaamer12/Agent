# Case 3 - the kitchen sink: eight files, four concerns

**Situation:** the user says "commit this". The tree holds a session that did four unrelated things:

```bash
git status --short
 M src/search/index.ts              # the actual feature: prefix suggestions
 M src/search/ranking.ts            #   same feature
 M src/auth/session.ts              # unrelated fix: session refresh on 401
 M package.json                     # unrelated: bumped the lint toolchain
 M package-lock.json                #   consequence of that bump
 M .github/workflows/ci.yml         # unrelated: cache npm between jobs
?? scripts/tmp-bench.ts             # scratch: a benchmark probe
?? src/search/notes.md              # scratch: thinking-out-loud, not for history
```

## Partition first, stage second

| Group | Files | Type | Depends on |
|---|---|---|---|
| A. search suggestions | `src/search/index.ts`, `src/search/ranking.ts` | `feat` | - |
| B. session refresh fix | `src/auth/session.ts` | `fix` | - |
| C. lint toolchain bump | `package.json`, `package-lock.json` | `chore(deps)` | - |
| D. CI npm cache | `.github/workflows/ci.yml` | `ci` | C (cache key uses the new lockfile hash) |
| E. scratch | `scripts/tmp-bench.ts`, `src/search/notes.md` | **do not commit** | - |

Order: C → D is the only dependency-driven pair; A and B are independent, so they go in whichever order the
reviewer would read them best. Committing D before C would reference a lockfile that has not changed yet -
each intermediate commit should make sense.

```bash
git add package.json package-lock.json && git commit -F msg-c
git add .github/workflows/ci.yml       && git commit -F msg-d
git add src/search/index.ts src/search/ranking.ts && git commit -F msg-a
git add src/auth/session.ts            && git commit -F msg-b
git status --short                     # E still untracked, deliberately
```

`git add .` would have made one commit out of all of it, including the scratch files. That is the mistake this
case exists to prevent.

## What E is for

Scratch work is yours to keep or delete, not the project's to carry. If the benchmark found something worth
keeping, it becomes its own commit with a real subject and the numbers in the body; if the notes contain a
decision, the decision belongs in the code comment, the PR, or an ADR - not as a tracked markdown file nobody
reads.

## The four messages

```text
chore(deps): upgrade eslint 8 -> 9 and migrate the flat config

The old config format is end-of-life; 9 is what the plugins we want require.
Config moved to eslint.config.mjs - rule set unchanged, so no new violations
appeared and nothing was reformatted as a side effect.
```

```text
ci: cache npm between jobs

Installs took 90s of a 4-minute pipeline. The cache key is the lockfile hash, so
it invalidates on the next dependency change.
```

```text
feat(search)!: add prefix suggestions to the search bar

Suggestions come from the existing index, so no new service is involved; ranking
shares the code path used by the results page to keep the two consistent.

BREAKING CHANGE: /api/search now returns { items, suggestions } instead of a bare
array. Consumers must read .items; ?compat=1 returns the old shape until
2026-01-15.

Closes #4970
```

```text
fix(auth): refresh the session instead of failing on a 401

Token expiry was surfacing as a hard error on the first request after midnight.
A 401 on a refreshable scope now triggers one refresh and replays the request
once; a second 401 is still an error, so we cannot loop.
```

## What got reported to the user

Four hashes, one line each, plus the explicit note that the two scratch files were left uncommitted and why,
and that no tests were run in this session because none were added to A/B beyond what already existed - the
`feat` commit's verification status is stated, not implied.
