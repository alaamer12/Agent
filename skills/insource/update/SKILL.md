---
name: update
description: >-
  Change something everywhere it lives, leaving no stale copy behind. Use for ANY change
  request: reword copy or docs; rename a term, identifier, file, route, or brand; change a value
  (price, limit, version, color, date), a behavior, or a rule; alter an interface or schema;
  swap a dependency; move a path; upgrade, deprecate, or restyle. Trigger on update, change,
  rename, replace, reword, rebrand, bump, correct, migrate, "switch X to Y", "we no longer do
  X", "it says X but should say Y", "make the docs match", even when only one file, line, or
  string is named. Pins the claim, finds its source of truth, sweeps by exact text, naming
  variants, i18n/locale files in every language, tests, docs, config, SEO/a11y text, and by
  meaning; classifies hits, asks how far to go instead of deciding scope alone, applies, and
  proves nothing stale remains. Builds a dry-run batch script for wide mechanical edits. Not for
  new features; for a true defect, find the root cause first.
---

# Update

Every change request has two sizes: the **spot** the user pointed at and the **footprint** the change actually touches. Users describe the spot because that is what they are looking at. The footprint is usually bigger, and the agent is the one who can measure it.

`fix` repairs behavior. `update` changes **information, names, values, or rules** and makes sure no stale copy of the old version survives anywhere in the project. The danger is never the edit itself; it is the copies. One hero title can live in a component, twelve locale files, a README caption, `<meta>` tags, a test, and a snapshot. Change one and the project contradicts itself, and a stale translation of the old title is not merely outdated, it is *wrong* in front of real users.

> **Find the full footprint. Never decide its boundary alone. Show the user what you found and let them choose.**

The failure has two mirror images. *Silent under-reach*: fix the visible spot, report "done", leave the codebase inconsistent. *Silent over-reach*: replace every hit, breaking a public API, rewriting a changelog, mangling a look-alike. The rule is neither "change less" nor "change more": measure wide, edit only what was approved.

> **Everything here is illustrative, not exhaustive.** Example stacks, bucket names, search handles, and scope options are starting points. If the project uses a language, framework, or convention not mentioned, or a different scope split fits better, use that.

## The unit of work is the claim, not the string

State the change as one sentence: **old claim -> new claim**. Search is driven by what is being asserted, so it can find copies that share no words with the original. Label it:

- **Wording** - same meaning, new phrasing. Every language must be re-expressed, but no fact becomes false.
- **Meaning** - the fact itself changed (price, limit, version, feature, name, rule). Everything that asserts *or relies on* the old fact is now false, including text that never quotes it.
- **Removal** - a claim that is no longer true and has no replacement. Hunt for text that promises the removed thing.

If the new value is not actually known (a price, a date, a limit), ask. Never invent information or ship a "TBD".

## Workflow

Do not edit anything before step 7. Steps 1-5 are read-only and cheap; do them eagerly.

1. **Pin the change.** Write: what is changing, old -> new, wording/meaning/removal, the seed location (where the user pointed), and the **search handles** (strings, identifiers, values, patterns that would reveal every other place). Handles depend on the kind of change: a rename needs every naming convention; a value needs every notation (hex/rgb, `10 MB`/`10485760`/`10 << 20`); a behavior change needs the constant, the check that enforces it, the messages that state it, the tests that assert it; an interface change needs every caller, type, mock, doc, and test. See `references/claim-and-source-of-truth.md`. If what is changing is genuinely ambiguous, ask before searching.
2. **Find the source of truth and how it is delivered.** The place the user points at is usually a *consumer*. Follow the code from there to where the value originates: literal in markup, translation key, key with inline default, natural-language key, dynamic key, constant, config, CMS/DB, generated file, rendered artifact. Edit the source; regenerate derived copies instead of hand-editing them.
3. **Explicit sweep.** Search for the old text, its fragments, its key/identifier, its value, and every variant form. Run `scripts/sweep.py`, then add the old wording read out of each locale file as extra terms (this finds hard-coded translations in tests and docs). Also search by hand for what a script cannot see and say "none found" explicitly for each: file and directory names, routes/URLs/redirects, identifiers, style hooks, tests/fixtures/snapshots, docs/comments/changelog, config/env/flags/build scripts, data (schema, migrations, seeds, serialized keys), UI copy (labels, placeholders, alt, aria, errors, emails). See `references/search-vocabulary.md` and `references/variant-patterns.md`.
4. **Implicit sweep.** Ask what *else* states, relies on, quotes, or derives from this claim without matching text: SEO/social metadata, accessibility text, other languages, emails, store listings, FAQs, paraphrases, infrastructure (a proxy limit that contradicts an app limit fails only in production). Walk the catalog in `references/reference-surfaces.md`. For a meaning change walk all of it; for a pure wording change the first four groups plus any surface that quotes the text usually suffice.
5. **Classify every hit** by the role it plays, then decide update / leave / ask. See `references/classify-and-verify.md`.
6. **Report and ask. Mandatory unless an exception below applies.** Present counts per bucket with examples, call out the risky items, give a recommendation, and ask one scope question. Use the structured question tool (e.g. `ask_user_input_v0`) so the user answers with one tap; otherwise end with a numbered question. Format in `assets/report-template.md`.
7. **Apply exactly the chosen scope.** Change the source first, then its dependents, so no intermediate state contradicts itself. Keep each copy faithful to the conventions of the place it lives (structure, markup, placeholders, escaping, units, style). Regenerate derived files. Hand-edit copies that need judgment; use the batch path below when one mechanical edit repeats across many files. If the user chose a narrow scope, do not argue or re-ask; record the skipped items in the summary.
8. **Verify by re-sweeping.** The re-sweep, not your memory of what you edited, is the evidence. Then report. See "Verify" below.

## Step 5 in short: buckets and decisions

Sort each hit by what it *does*, not by its filename or spelling.

| Bucket | Meaning | Default decision |
|---|---|---|
| **Core** | The code, value, or rule that *is* the change | Update (always in scope) |
| **User-facing** | Text/UI/messages a human sees, in every language | Update |
| **Internal** | Identifiers, styles, helpers, file names, callers carrying the old idea | Update if scope allows (touches many files) |
| **Verification** | Tests, fixtures, snapshots, mocks | Update with the code; **ask** if the test exists to protect the old behavior |
| **Docs** | README, guides, API descriptions, comments, paraphrases | Update; flag screenshots and videos |
| **Contract** | Routes, API fields, DB columns, env vars, events, public signatures, URLs that outsiders depend on | **Ask.** Never assume; offer an alias/deprecation path |
| **Historical** | Changelogs, applied migrations, release notes, ADRs, quoted reviews | **Leave**; add a new entry if the project keeps a changelog |
| **Generated / vendored** | Build output, lockfiles, snapshots, compiled translations, third-party code | Never hand-edit; fix the source and regenerate |
| **Look-alike** | Same word or number, different meaning (`class` keyword, a retry count of `5`) | **Leave**; ask if unsure |

Living vs historical: if a reader today would be misled, it is living, so update. If it faithfully records what was true on a date, leave it. Legal/privacy/terms text carries meaning and effective dates: propose the exact change and flag it, never edit silently. Production data and CMS entries are data, not code: update seeds, report the rest as "needs a human".

**Short or common words** (`class`, `type`, `order`, `user`, `state`, `10`) over-match. The sweep is a *finder*, not a judge: filter to hits that plausibly mean the changed concept, then show the user a small sample of both groups (candidates and set-aside) so they can confirm the boundary. A 400-line grep dump is not a decision the user can make.

## Step 6 in short: the report and the scope question

The report contains: the one-line change; counts per bucket with `file:line` examples; risky items (contracts, look-alikes) with what would break; what you cannot verify from here (other repos, DB rows, dashboards, app stores); your **recommendation**, clearly marked as a suggestion; and one scope question.

Build the choices from the buckets you actually found, narrowest to widest, and name them in the words of *this* change. Always include the narrowest, because it is a legitimate choice. Shapes, not a closed menu:

- `[just the spot you named]`
- `[the change + everything that shows or explains it]` (core, user-facing, docs, verification)
- `[everything except contracts]`
- `[everything, with old public names kept as deprecated aliases]` or `[everything, including a breaking rename]` (offer only when you can name what breaks)

A hybrid or a split the user proposes is equally valid. Drop options for empty buckets. Ask **one** scope question (three questions is the ceiling): add a second only when it is genuinely separate, such as the translation policy below or whether to include a large separable test/docs bucket. Do not narrate assumptions as facts: "you probably don't want the API changed" is a question wearing a statement's clothes, so ask it.

### When the question is not needed

The decision to skip the question is made **after** the sweep, never before it. Run steps 1-5 every time, then:

- **The sweep finds nothing else.** Say so in one line and make the change ("I checked for other uses and this was the only one").
- **The user already stated the scope** ("only the pricing table, leave the rest"). Respect it and do not re-ask or expand. Still add a one-line heads-up about notable leftovers so they know they exist.
- **The sweep finds other references.** Ask, even if the user only named one spot and even if you are fairly sure what they want. Being fairly sure is exactly when the local-fix trap springs; the cost of asking is one tap.

## Copies in other languages

When the claim also exists in other languages, a translation of the old claim is a stale claim. Never leave one behind silently. Enumerate the full locale set first (folders, `.po`/`.arb`/`.xlf` files, i18n config), detect pipeline ownership (Crowdin, Lokalise, Phrase, Weblate, "do not edit" headers), and check how strings are keyed (natural-language keys turn a wording change into a key rename in every catalog). Then, per locale, choose and report one of:

1. **Translate it** (default for languages you write well): match register, brand terms, and placeholders of that file.
2. **Translate and flag for native review** when less sure.
3. **Defer to the project's pipeline**: update the source locale only and say so.
4. **Remove the key** so the fallback shows, only if a fallback is configured and acceptable.

If the convention is unclear, ask once rather than guess per file. Details, format-by-format notes, and Arabic/RTL/plural-form guidance are in `references/localization-and-i18n.md`.

## When the edit is mechanical and wide: batch path

If the sweep shows the same transformation repeated across many files (a rename, an import path, a key, a version string, a constant's value; more than a handful), do not hand-edit. Follow `references/batch-update.md`: verify patterns with real counts (they must sum to the total), generate the script from `scripts/batch_update_template.py`, check it with `--dry-run` and a random `--sample`, then **stop and give the user the exact `--apply` command**. Do not apply it yourself.

Scope the batch with step 5: only mechanical *update* hits go in; *leave*/*ask* files, generated output, and vendored code stay out. Judgment-based copies (rewritten prose, new translations) are edited directly. Skip the batch path for a handful of files. Because you stop before applying, verification happens **after the user runs `--apply`**; offer to run it then.

## Boundary rule

`update` is bounded by the **claim**, not by location, so it may legitimately touch dozens of files. A hit is in scope when it **states, depends on, or is derived from** the changed claim, *and* falls inside the scope the user approved. Out of scope either way:

- Rewording neighboring copy, fixing unrelated typos, restyling while you are there. Mention them under "Noticed but not touched".
- Renaming keys, files, or identifiers beyond what the claim requires (rename a key only when its name embeds the old claim, like `pricing.trial14Days`, and then everywhere at once).
- Consolidating duplicated copies into a shared source unprompted. Propose it.

## Verify

1. **Residual sweep** with the old claim's full vocabulary, reconciled against the approved skip list:
   ```bash
   python scripts/sweep.py "<old text>" "<old key>" "<old translation>" --allow CHANGELOG.md --allow vendor
   ```
   Every remaining hit must be on the list the user approved, with a reason. **Any other match is a miss, even if the result already looks right**: a visible label can read correctly while a class name, serialized key, or config entry beside it still carries the old term. Fix misses and re-sweep until `UNAPPROVED remaining: 0` (exit code 0). If a miss needs a decision you have not asked about, stop and ask instead of listing it as done.
2. **Positive sweep** for the *new* text: it should appear in every surface intended, including every locale. Missing places are as informative as leftovers.
3. **Locale integrity**: `python scripts/locale_parity.py --root <dir>` (no missing keys, no accidental copies of the source language, placeholders and plural forms intact); `--grep "<old wording>"` for leftover wording.
4. **Project checks**: tests (regenerate snapshots only for diffs you can explain, and read them), type-check, lint, i18n extractors, markdown/link checks, build. Skip what does not exist and say so. "Tests pass" is evidence, not proof; tests rarely cover docs, metadata, accessibility text, or locales.
5. **Rendered check** when feasible: source language plus one RTL or long-text language.
6. **Read the diff once** as a reviewer: is every changed line related to the claim?

Finish with the post-change summary from `assets/report-template.md`: scope chosen, what changed grouped by surface, the reconciliation table, what was left on purpose, what needs a human (native-speaker review, CMS or dashboard edits, store listings, production data, images), and anything noticed but not touched.

## Anti-patterns

- **Silent minimal edit**: changing the visible string and leaving locales, metadata, tests, docs, and identifiers saying the old thing.
- **Silent maximal edit**: replacing every hit without asking; wide search does not license wide editing.
- **Exact-string-only search**: misses keys, escapes, wrapped lines, plurals, other languages, paraphrases.
- **Assumption as statement**: deciding contract/scope questions out loud instead of asking them.
- **Wall of hits**: pasting 200 grep lines and asking "what do you want?". Group, count, sample, recommend.
- **Closed menu**: offering "pick 1, 2, or 3" as if those were the only scopes. A hybrid is welcome.
- **Questionnaire / endless questions**: asking when the sweep found nothing or the user set the scope; or asking one question per category. Ask one.
- **Re-arguing**: repeating the case for a wider scope after the user chose a narrow one.
- Hand-editing generated files, snapshots, or compiled translations instead of the source.
- Rewriting history (old changelog entries, applied migrations) to match the new truth.
- Silently editing legal/privacy text, or renaming an externally visible identifier (URL slug, analytics event, API field) as if it were copy.
- Weakening a test to make it pass.
- Skipped verification: reporting done without re-sweeping, or stopping the search at the first file type that looks finished.

## Relationship to other skills

- **fix / dbug**: if the "outdated" value is really a symptom of a defect (wrong value computed, broken lookup), diagnose and fix the root cause first; use `update` afterwards for the sweep if the fix changes what is true. Pure feature work and unrelated cleanup are out of scope.
- **test**: update assertions that quote changed text; never weaken a test to make it pass.

## Bundled resources

Scripts (read-only except the batch template, which is dry-run by default):
- `scripts/sweep.py` - the main search tool. Expands terms into naming conventions, plurals, BEM fragments, HTML entities, unicode/JSON escapes, URL-encoding, curly quotes, Arabic/Persian digits, and flexible whitespace; groups hits by surface with a suggested report bucket; lists matching file/directory names and hits hiding inside excluded dirs (vendor look-alikes); warns loudly on zero matches; `--allow` reconciles remaining hits against the approved skip list (exit 1 if any are unapproved); `--count`, `--files-only`, `--json`. Stdlib only. Run with `--help`.
- `scripts/sweep.sh` / `scripts/sweep.ps1` - dependency-free fallbacks (bash with grep/ripgrep; native PowerShell 5.1+) for machines without Python. Same idea, per-variant line counts.
- `scripts/locale_parity.py` - JSON locale folders: `--key` shows one key in every language, `--grep` finds old wording across languages, default mode reports missing keys and values identical to the reference language.
- `scripts/batch_update_template.py` - scaffold for the batch path: dry-run by default, reproducible random `--sample`, preview identical to what `--apply` writes, line endings preserved.

References (load when needed):
- `references/claim-and-source-of-truth.md` - pinning the claim, kinds of change and their search handles, how text is delivered, key names that embed the old claim.
- `references/search-vocabulary.md` - building the term vocabulary and the forms text takes in real repos; `rg` recipes.
- `references/variant-patterns.md` - per-ecosystem naming conventions, layers where a concept hides, grammar traps, look-alikes. Read when the project mixes stacks or the sweep finds less than expected.
- `references/reference-surfaces.md` - catalog of implicit surfaces (metadata, a11y, emails, config, legal, records).
- `references/classify-and-verify.md` - update/leave/ask rules, judgment calls, verification checklist.
- `references/localization-and-i18n.md` - locale files by ecosystem, traps, writing translations, Arabic/RTL.
- `references/batch-update.md` - the full batch workflow and pitfalls.
- `references/examples.md` - worked multi-language examples (rename, value, behavior, contracts, look-alikes, dependency migration, when NOT to ask).
- `assets/report-template.md` - the scope report, scope question, and post-change summary with reconciliation table.
- `examples/` - end-to-end polyglot walkthroughs: a hero title across locales in several i18n stacks; a 10 MB -> 25 MB meaning change across code, infra, UI, and docs.
