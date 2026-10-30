# When to commit — cadence, size, and the "too small" trap

Citations `p.N` refer to the source conversation reconstructed in [`08`](08-sources.md); they are provenance,
not authority — the rule stands on its own reasoning.

## The trigger is a sentence, not a line count (p.4–6)

| Signal | Commit? |
|---|---|
| You can describe the change in one sentence | yes, now |
| You finished and tested a function | `feat: add user scoring function` |
| You fixed a bug | `fix: handle edge case in scoring` |
| You only improved readability | `refactor: improve readability of score calculation` |
| Only formatting changed | separate `style:` commit |
| Only docs/comments changed | `docs: clarify score function behavior` |
| ~100 lines reached | a ceiling, not a target — commit before you lose the thread |
| 500 lines at once | **too big**: unreviewable, unrevertable, unbisectable |

The anti-pattern (p.5): 500 lines that are two features, a fix, and a cleanup, under `-m "update file"` —
"untraceable and hard to maintain." The pro move is the *same* 500 lines as three commits:
`feat: add user login parser` → `fix: prevent crash on missing token` → `refactor: extract config loading`.

## Commit by intent, not by importance (p.8–11)

There is no change too small to commit. Moving `fig.savefig("plot.png")` into
`def export_plot(fig, path="plot.png")` looks trivial and is a **reuse decision**:
`refactor: wrap plot saving in reusable export_plot function` (p.9).

The trap is cumulative (p.10–11): deciding "too small" ten times produces one 200-line context-less blob.
Small commits individually record a design decision, keep blame honest, and make a revert cheap.

Good small messages (p.11): `refactor: wrap plot export in helper function` ·
`style: remove unused import in plot module` · `docs: add explanation for smoothing algorithm` ·
`fix: use safer default value for output file path`.

**Time-saver (p.9):** group tiny changes *of the same kind*. Renamed three functions and wrapped a helper →
one `refactor:` commit, not four. Same kind, same intent → one commit; different intent → different commit.

## Feature + its docs + its tests: one or three? (p.11–13)

**Default: one atomic commit.** They serve a single purpose, and keeping them together preserves
bisect/blame/rollback coherence:

```text
feat(math): add calculate_mean with docstring and unit test
```

**Split when the intents are separable (p.11–12):**

| Situation | Commits |
|---|---|
| Docs added to an *existing* function | `docs:` alone — an independent change |
| Tests added to a *previously untested* function | `test:` alone — logical evolution |
| Refactor, then test | two commits — two intents |
| TDD team, or CI gates on coverage per commit | split, per the team's convention |
| Feature A + unrelated test B | **definitely** separate |

Calibration in one line: feature+docs+test = one; refactor+test = two; feature+unrelated-test = never one.

## 500 lines that are genuinely ONE functionality (p.6–8)

Both options are professional; cohesion decides.

**Option A — one commit**, when every line belongs, nothing works without the rest, and it compiles and passes
tests as a unit:

```text
feat(report): add full PDF report generation from raw data

Includes data aggregation, formatting, and PDF rendering using ReportLab.
```

**Option B — sub-task commits**, when the pieces could be reviewed, cherry-picked, or bisected separately:

```text
feat(report): parse CSV input into structured data
refactor(report): clean up table column alignment logic
feat(report): render formatted data as PDF
fix(report): prevent crash on missing values
test(report): add test case for multi-page report
```

Splitting one file across those commits is `git add -p` ([`10`](10-hunks-and-splitting.md)).

## Bulk work: N similar files at once

A DSA tutorial repo where each algorithm folder gets a `README.md`, plus a global one.

**Separate commits** when each file is substantive and self-contained, was authored in its own step (different
days or people), or will be owned by a different contributor later — per-file blame survives, and one file can
be reverted alone:

```text
docs(greedy): add README with overview of greedy strategies
docs(backtracking): add README with explanation and example
docs(dp): add README with top-down vs bottom-up comparison
docs(root): add global project README with index and instructions
```

**One bulk commit** when the files are boilerplate or placeholders ("Coming soon", title-only), were produced
in one sitting as a unit, or when a tidy history matters more than per-file traceability:

```text
docs: add README files for all algorithm categories
```

| Situation | Strategy |
|---|---|
| Each file has meaningful, distinct content | one commit per file, scoped |
| All files share a structure or are placeholders | one bulk commit, descriptive message |
| Made in one session and related | one bulk commit |
| Different people will own them later | separate commits, for blame |

This is the atomicity rule at file granularity: the unit of a commit is the unit of **intent**, so N identical
boilerplate files are one decision and N real documents are N decisions.

## Cadence tactics while developing (p.5–6)

- **Prototyping:** commit the mess — `feat: prototype search algorithm (not final)` — then squash it clean
  before sharing ([`13`](13-wip-checkpoints-and-squash.md)).
- **TDD:** commit after each test passes — `test: add test for input validation`.
- **Interrupting fix:** commit it separately, immediately ([`12`](12-fix-interrupts-feature.md)).
- **Half-done but harmless:** legitimate — `feat: scaffold report export logic (not active yet)` (p.55–56).
  The app works; the code is inert or flag-gated. "Half-done" and "broken" are different states.

## The ritual, every time (p.1, p.3)

```bash
git status          # what changed?
git diff            # review YOURSELF first
git add <file>      # selectively — not git add .
<project test cmd>  # never commit untested code as tested code
git commit -m "type(scope): description"
```

Enforcement means *something checks the message at commit time* (p.3). The tool-neutral form is a committed
`core.hooksPath` hook; language-specific linters and hook managers fill the same role. See
[`07`](07-history-hygiene-and-hooks.md).

One caveat on the last step: run the project's own test command, and respect a repository whose instructions
say not to run heavy checks by default. If you did not run them, the message says nothing about tests passing
— silence beats a false claim.
