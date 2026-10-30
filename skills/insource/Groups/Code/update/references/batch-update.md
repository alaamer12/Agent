# Batch Update: Reviewable Mechanical Edits Across Many Files

Merged from the standalone `batch-update` skill. Use it inside `update` whenever one mechanical edit has to be repeated across many files.

## Contents
1. Why this exists
2. When to use it (and when not)
3. How it fits into `update`
4. The workflow
5. Using the template (`scripts/batch_update_template.py`)
6. Pitfalls to check
7. What to tell the user

## 1. Why this exists

Editing many files one by one is slow, easy to get subtly wrong, and gives the user no chance to review before the change is real. Instead, build a small disposable script that performs the edit, let the user preview it (in full and as a random sample), and have **the user** run the final write. The aim is not automation for its own sake; it is making a repetitive change **inspectable** and **controlled** before it becomes hard to undo.

## 2. When to use it (and when not)

Use it when the same kind of edit repeats in more files than you would want to review by hand:

- A file, module, class, or symbol was renamed and other files reference the old name.
- An import path, config key, environment variable, translation key, or API field changed.
- A version string, URL, constant value, or product name must change everywhere it appears.
- A deprecated pattern is replaced with a new one across the codebase or document set.

Do not use it for:

- A single file or a handful of clearly distinct edits - just make them.
- Edits that need judgment in every file (rewritten prose, new translations, per-page copy). Nothing mechanical to script; edit by hand with full context.
- Structured data where a text pattern could corrupt the format. Prefer a format-aware approach (parse and re-serialize, or an `ast`-based rewrite) and still follow the same dry-run/sample/handoff discipline.

## 3. How it fits into `update`

`update` decides **what** changes; batch-update decides **how** the mechanical part is applied.

1. Run the normal sweep and classification first (`scripts/sweep.py`, `classify-and-verify.md`). The *update / leave / ask* decisions determine the batch's scope.
2. Put only the mechanical **update** hits in the batch. Exclude *leave* files (changelogs, migrations, history), generated files, vendored code, and anything marked *ask* from `TARGET_FILES`.
3. Handle the judgment-based hits directly (translations of new wording, rewritten docs, legal text flagged for review).
4. Typical mechanical batches inside an `update` task:
   - renaming a translation **key** across every locale file and every usage site;
   - changing a natural-language key (gettext `msgid`) in every catalog;
   - replacing an old product name or version string in docs, config, and comments;
   - changing a constant's literal value where it appears as a bare number in many places.
   Not a batch: writing the *new* translated sentence for each language. Each locale gets different text, so do those by hand (or per-locale tables).
5. Because the agent stops before applying, the verification step of `update` (residual sweep, locale parity, tests, build) happens **after the user runs `--apply`**. Tell the user to run it, and offer to run the verification once they have.

## 4. The workflow

```
Detect -> Identify patterns -> Generate script -> Dry run -> Random sample -> Validate -> Stop -> User executes
```

### 4.1 Detect and identify the required changes

This is investigative work you do directly; it is not something to delegate to the script. The script only executes a plan, and the plan is only as good as how rigorously you checked the project.

Core discipline: **treat every claim about the project as something to verify, not assume.** "All 49 files reference it the same way" is a claim until you have checked all 49.

- Search the whole project for every occurrence (use `scripts/sweep.py` or `rg`), not just the ones the user mentioned and not just enough to convince yourself of a pattern.
- Do not stop at a representative sample. Write small throwaway checks that count how many files match each candidate pattern and how many match none. If the counts do not add up to the total, some files do something you have not accounted for; look at those specifically instead of rounding them into an existing pattern.
- Group into **distinct patterns** only after confirming they are real, e.g. "A: `from old_module import X` (31 files)", "B: `old_module.py` in a config string (12 files)", "C: `# see old_module` in a comment (6 files)". If pattern counts do not sum to the occurrence total, something is missing.
- Identify false positives (substring matches inside unrelated identifiers, binaries, generated or vendored directories) and verify them by printing surrounding context.
- Flag ambiguous cases a script cannot handle safely (a string that is sometimes the thing to change and sometimes coincidentally similar). Exclude them from the script and call them out.

Output of this step: a list of patterns, each with a **verified count** and a real before/after example. Show it to the user briefly before or alongside the script.

### 4.2 Generate the batch script

Build the script from the patterns actually found, not one blind find-and-replace. Copy `scripts/batch_update_template.py` into the project (for example as `batch_update.py`) and edit `TARGET_FILES` and `PATTERNS`. Keep it simple and readable: a person should be able to open it and see exactly what it will change and why.

### 4.3 Dry run

The script must report every change it would make without writing anything. Each change is legible: file, line, before and after for that specific occurrence, not just a count. The template makes this the default behavior.

### 4.4 Random sample (`--sample N`, default 5)

Alongside the full report, print a **random** handful of changes. Always showing the first N hides problems later in the list. The template samples from the full set on every run and prints the seed, so a sample can be reproduced (`--seed`) or re-rolled.

### 4.5 Validate; do not apply

Your job is to verify the script, not to run it for real:

- Run the dry run yourself and read the output. Does it match the patterns from 4.1? Does the file/occurrence count look right?
- Spot-check sampled changes against the actual files; confirm nothing unrelated got swept up.
- Fix the script if the dry run reveals a missed pattern, a false positive, or an edge case (quote styles, trailing whitespace, case differences, overlapping patterns).

Once satisfied, **do not run `--apply`**. That step belongs to the user.

### 4.6 Stop and hand over

Report what the script does (which patterns, how many files and occurrences), state that you have not modified the project, and give the exact command, for example:

> The batch update script is ready and its dry run is verified. It handles the identified patterns across the affected files. I have not applied it to your project. To apply it, run:
>
> ```bash
> python batch_update.py --apply
> ```

Give the real command for what you built, including any extra flags.

## 5. Using the template

`scripts/batch_update_template.py` supplies the scaffolding so dry-run and sampling logic is not rebuilt each time. Fill in:

- `TARGET_FILES` - globs scoped to the files Detect found. Do not point it at the whole repo unless verified. Plain `**/*.yml` skips dot-directories such as `.github/`; list those explicitly.
- `PATTERNS` - `(regex, replacement, description)` tuples, one per distinct pattern. Do not merge distinct patterns just to save lines, or the report can no longer say which pattern matched.

Behavior built in:

- Nothing is written without `--apply`; running with no flags is a dry run.
- The preview shows the exact final text of each changed line, computed by the same function the apply step uses.
- Patterns run in order per line; lines touched by more than one pattern are listed as overlaps.
- Apply re-reads each file and skips any line that changed since the scan (stale preview) instead of overwriting it.
- CRLF/LF line endings are preserved; unreadable files are reported and skipped.
- Matching is line-by-line. Text wrapped across lines will not match; handle it by hand or adapt the script to whole-file matching.

Adapt freely (for instance `ast`-based matching for structure-aware renames). The parts that matter are dry-run by default, random sampling, and never applying unless the user explicitly runs it.

## 6. Pitfalls to check

- **Overlapping matches.** One line matched by two patterns; check order and the overlap warning.
- **Quote and whitespace variants.** `"old"`, `'old'`, and bare `old` are often three patterns.
- **Partial-name collisions.** `old_module` inside `old_module_test` or `some_old_module_wrapper`: use word boundaries and read the dry run for these.
- **Case and escape variants.** Casing, HTML entities, `\u` escapes, URL-encoded forms (`sweep.py` lists them).
- **Non-text and generated files.** Binaries, lockfiles, `dist/`, `build/`, snapshots, compiled translation binaries: exclude and regenerate instead.
- **Historical records.** Changelogs, migrations, ADRs, release notes: exclude unless the user explicitly asks.
- **Encoding and line endings.** Do not assume UTF-8 with `\n`; the template preserves line endings and skips unreadable files per file.
- **Windows paths.** Use `pathlib` for path checks; do not split on `/`.

## 7. What to tell the user

Keep the hand-off short: the claim being changed, the patterns with verified counts, what was deliberately excluded and why, the exact `--apply` command, and what you will check afterwards (residual sweep, parity, tests, build).
