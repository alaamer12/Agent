# Gray zones — choosing the type and the scope when it is not obvious

Most mislabelled commits happen in a handful of recurring judgment calls. They are settled here so nobody
re-decides them under deadline pressure.

## Scoping rules (p.71, p.93–95)

A scope exists for **navigation**: `fix(_generate_graph): handle NaN values in input data` makes `git log` and
`git blame` searchable (p.71).

| Style | Use | Example |
|---|---|---|
| file path | small projects, one file touched | `fix(lib/parser.py): …`, `fix(api/user.py): …` |
| module / package | logical boundaries, larger codebases | `feat(auth): …`, `feat(src/utils/time.py): …` |
| domain / tooling | build, CI, releases | `chore(ci): …`, `chore(release): …` |
| component | UI work | `test(Button): …`, `test(views/home.test.js): …` |

Keep it short, use `/` only when necessary, never an absolute path.

**The change spans several files** (p.94–95):

1. **Name the shared concern** — `fix(reporting): correct summary totals in multiple files`,
   `feat(auth): support 2FA flow across login and settings`,
   `refactor(parser): unify error handling across all stages`.
2. **Never concatenate paths.** `fix(src/a.py+src/b.py+lib/x.py): …` parses and reads terribly, and defeats
   the purpose of a scope. Wanting to write it is the signal that the commit should be split instead.
3. **No common denominator → drop the scope**: `fix: correct several unrelated minor bugs`,
   `chore: update license headers across codebase`, `style: format all Python files`.

Many teams pin the approved scope list in `CONTRIBUTING.md`; if it exists, use it.

## Subject-line style (p.92–93)

Write the subject like a changelog line: short, descriptive, clear. Lowercase, no trailing period, imperative
tone — `fix overlay positioning`, not `fixed overlay positioning`. Do not repeat the type (`fix: fix …`) and
do not be vague (`fix: stuff`, `feat: improvements`). Full imperative sentences are an acceptable alternative
convention (`fix: resolve language detection issue`); pick one per team and enforce it with a linter or
template.

**Words inside a scope or subject are vocabulary, not keywords.** `overlay`, `parser`, `reporting`, `2FA` carry
no reserved meaning — only the `type` does. Anything domain-specific is fair game:
`fix(overlay): handle resize` · `feat(parser): add AST support` · `refactor(reporting): extract PDF generation`.

## The type decision table

| Situation | Type | Why |
|---|---|---|
| A refactor is needed **before** a feature (p.44–46) | two commits: `refactor:` then `feat:` | the refactor adds no behavior; separating them isolates bugs to the refactor and lets reviewers take "just a refactor" as a safe step. Stage the refactor alone with `git add -p` |
| You restructured **test code**, assertions unchanged (p.46–48) | `refactor:` | `refactor: rename tests for clarity` |
| What is *tested* changed (new/removed assertions, new cases) | `test:` | `test: add more edge cases to divide() test` |
| Both at once | two commits, or one honest combined message | `test: restructure and add new cases for divide()` |
| Method → `@staticmethod` because `self` was unused (p.77–79) | `refactor:` | not `style:` (that is formatting/lint only) and not a no-op: the machine does not care, **humans read clarified intent** |
| You added `print()` / log statements (p.48–50) | `chore:` or a team prefix (`debug:`, `wip:`) | temporary instrumentation, removed before merge. `style:` only if it changed output *appearance*. `feat:` **only** if the output is user-facing on purpose (CLI feedback, structured logging). Personal-only? stash it, don't commit it |
| Ran the formatter on the whole codebase (p.52–54) | `style:` alone | `style: format code using black` — one dedicated commit declaring *zero functional change*: reviewable, undoable, blame-preserving. Better: hook the formatter so it never mixes in. **Never** `feat: implement chart and reformat code` — it destroys blame and bisect. Tip: format at branch start so later diffs stay clean |
| What does `chore:` even mean (p.51–52) | routine, tedious, necessary, **no src or test logic** | `chore: add .gitignore for virtualenv`, `chore: bump version to 1.2.3`, `chore: move utils to /helpers folder`, `chore: update coverage badge`, `chore: add GitHub Actions config`. TLDR: *support, not behavior*. Real case: adding `__init__.py` files for package structure → `chore: add __init__.py files to mark package structure` (p.142–143) — infrastructure, no business logic |
| Is CSS a `style:` commit? (p.79–81) | **no** | `style:` = formatting only (indentation, semicolons, lint, import order). CSS is typed by *why*: visual bug → `fix(ui): correct navbar spacing on mobile`; new visual capability → `feat(profile): add animation to avatar`; reorganized/renamed styles → `refactor(css): extract card styles into mixin`; reindent-only → `style(css): fix indent and spacing` |
| `refactor:` vs `chore:` in one rule (p.66–67) | logic → `refactor:`; everything else → `chore:` | `refactor: extract auth logic into AuthService` vs `chore:` for configs, scripts, spacing, dependencies. Deep layout-logic changes (flex→grid) are a judgment call some teams write as `refactor(ui):` |
| Swapped a slow library for a fast one, `json` → `orjson` (p.90–91) | `perf:` | `perf: switch from json to orjson for faster serialization`. `refactor:` requires no behavior **and no performance** change; a speed win is exactly what `perf` exists for |
| A fix that required building a mini-feature (p.81–83) | prefer two: `feat:` then `fix:` | `feat(ui): add support for in-box scrolling` → `fix(overlay): position overlay relative to container`. Or one commit by dominant intent with the utility explained in the body: `fix(overlay): resolve incorrect positioning via scroll container`. **Never** invent `feat+fix(ui):` — non-conventional, and release automation will not recognize it |
| Mixed change: a previously-unused parameter now used, plus restyled HTML/CSS (orig, Jun 6) | `refactor(footer): use timestamp parameter and enhance styling` | Ask four questions: did output change? **yes**. was it broken? **no**. new feature? **not really**. purely cosmetic? **partly**. → an output/structure improvement that is neither `feat` nor `fix`. `style(footer): …` is valid **only** where the project lets `style:` cover markup/CSS structure rather than formatting alone (see the CSS row above). If both must ship together, prefer `refactor` and describe both |

`enhancement` and `improvement` are **not** Conventional Commits types (p.77–78); some organizations use them
anyway — follow the repo, not the spec, when they conflict.

## The two questions that resolve any new case

1. **Did observable behavior change?** yes → `feat` (new) or `fix` (was broken). no → keep asking.
2. **What kind of non-behavior change is it?** logic shape → `refactor`; speed → `perf`; formatting/lint →
   `style`; what is tested → `test`; text → `docs`; build/CI/deps → `build`/`ci`/`chore`; routine support →
   `chore`.

If answering requires the word "and", the commit is two commits.
