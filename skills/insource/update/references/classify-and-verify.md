# Classifying Hits, Verifying, and Reporting

A wide sweep returns hits that should not all be treated alike. Classify each hit by the **role it plays** (bucket), decide what to do with it (update / leave / ask), then prove the result.

## Contents
1. Buckets and decisions
2. Rules of thumb
3. Judgment calls
4. Verification checklist
5. Reporting

## 1. Buckets and decisions

The bucket says what the hit *is*; the decision says what to do. Buckets feed the scope question (`assets/report-template.md`); decisions feed the apply step. `scripts/sweep.py` prints a suggested bucket per surface as a hint only: a file named `limits_test.go` is Verification, not Core, and `source` hits can be Core, Internal, or Contract. Read the line.

| Bucket | Meaning | Decision | Examples |
|---|---|---|---|
| **Core** | The code/value/rule that *is* the change | Update | the constant, the check, the source string |
| **User-facing** | What a human sees, in every language | Update | UI copy, all locales, meta tags, alt/aria, emails |
| **Internal** | Identifiers, styles, helpers, file names, callers carrying the old idea | Update if in approved scope | class/function names, CSS hooks, module paths |
| **Verification** | Tests, fixtures, snapshots, mocks | Update with the code; **ask** if the test protects the old behavior | `getByText(...)`, expected values, test names |
| **Docs** | README, guides, API descriptions, comments | Update | prose, OpenAPI `description`, `// 10 MB cap` |
| **Contract** | Things outside consumers depend on | **Ask** (offer alias/deprecation) | URL slugs, analytics event names, API/JSON fields, DB columns, env vars, webhooks, public signatures, legal text, store listings |
| **Historical** | Records of the past | **Leave** | old changelog entries, applied migrations, release notes, ADRs, blog posts, quoted reviews |
| **Generated / vendored** | Derived or third-party | **Leave**; fix source and regenerate | `dist/`, lockfiles, `.mo`, snapshots, `node_modules`, OpenAPI clients |
| **Look-alike** | Same word/number, different meaning | **Leave**; ask if unsure | `class` keyword, `5` as a retry count, a vendored lib's `catalog` |

## 2. Rules of thumb

- **Living vs historical.** If a reader today would be misled, it is living: update. If it faithfully records what was true on a date, it is history: leave it, and add a new entry if the project keeps a changelog.
- **Derived artifacts follow the source.** Generated code, snapshots, compiled translation binaries, and docs built from comments are regenerated, never patched by hand.
- **Identifiers are not copy.** Anything other systems or bookmarks reference (URLs, event names, JSON fields, CSS classes used by external scripts, deep links) can break consumers when renamed. Treat as ask, usually with a redirect/alias plan.
- **Unrelated look-alikes.** Another section that also says "faster" is out of scope unless it asserts the changed claim.
- **Classify by function, not filename.** Check the directory and read the line before choosing.
- **Short common words over-match.** Filter, then show the user a sample of both candidates and set-asides.

## 3. Judgment calls

- **Tests that assert old text.** Update the expected string when the test checks "the component renders its title." Stop and ask when the test exists to protect the old behavior (it enforces a limit or business rule); that is a decision, not a copy edit.
- **Comments that explain old values** (`// 10 MB cap`). Update them, or replace the number with a reference to the constant if that is a trivial local improvement; otherwise mention it.
- **Example data and screenshots.** Update text-based examples; list images and recordings under "needs a human".
- **Legal, privacy, and policy text.** Propose the exact change and flag it. These often need an effective date, a version bump, and sign-off.
- **Production data and CMS.** Report what needs a manual or scripted edit; never run destructive updates against live data without explicit instruction. Update seeds so new environments are correct.
- **Behavior changes with existing-data questions** (free tier cut from 5 to 3 projects: what about accounts already at 5?). Invisible to text search; raise it as a question.
- **Ambiguous scope.** Do not guess the smaller scope silently: ask (step 6). If the user is unreachable, finish the smallest defensible scope and list larger candidates for approval.
- **Related defects noticed along the way** (typos, broken links, inconsistent wording elsewhere): note them in the report; do not fold them into this change.

## 4. Verification checklist

Run what exists in the project; skip what does not, and say so.

1. **Residual sweep with reconciliation.** Re-run `scripts/sweep.py` with the old claim's full vocabulary (old text, fragments, key, old-language wordings, variants) and `--allow` for each path the user approved leaving. Goal: `UNAPPROVED remaining: 0`. A match not on the approved list is a miss even if the visible result already looks right (`<h1 className="catalog__title">Explore the topics</h1>` reads correctly yet still carries the old class).
2. **Positive sweep.** Search for the **new** text: it should appear in each intended surface, including every locale. Missing places are as informative as leftover ones.
3. **Locale integrity.** `scripts/locale_parity.py`: no missing keys, no accidental source-language copies, placeholders and plural forms intact.
4. **Tests.** Run them. Regenerate snapshots only for diffs you can explain by the change, and read the diff.
5. **Static checks.** Type-check, lint, i18n linters/extractors, markdown/link checkers if present.
6. **Build.** A successful build catches dangling imports and bad JSON/XML/YAML quickly. CI scripts that assert text fail late and confusingly: check them.
7. **Rendered check** (when feasible). Run the app in the source language and one RTL or long-text language; look for overflow, mirrored layout, mixed-direction glitches.
8. **Diff review.** Read the full diff once as a reviewer: is every changed line related to the claim?
9. **Batch path.** If part of the change went through a batch script, all of the above happens after the user has run `--apply`.

"Tests pass" is evidence, not proof: tests rarely cover docs, metadata, accessibility text, or locales.

## 5. Reporting

Use `assets/report-template.md`: the pre-edit scope report (step 6) and the post-change summary with its reconciliation table. Keep it short and scannable; group by surface, not file order; sample instead of dumping. Always include "Left on purpose", "Needs a human / your decision", "Cannot verify from here", and "Noticed but not touched".
