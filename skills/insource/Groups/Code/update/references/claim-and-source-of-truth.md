# Pinning the Claim and Finding the Source of Truth

## Write the claim down

State it in one sentence before searching:

> **Old:** "Landing page headline says Symphony is a *code editor*." -> **New:** "...an *AI-first IDE*."

Then label it:

| Kind | What changed | Consequence |
|------|--------------|-------------|
| **Wording** | Phrasing only, same fact | Every language must be re-expressed; nothing else becomes false |
| **Meaning** | The fact itself (price, limit, version, capability, name) | Everything asserting *or relying on* the old fact is now false, even text that never quotes it |
| **Removal** | A claim no longer true and has no replacement | Hunt for text that promises the removed thing; delete or rewrite, don't leave a hole |

A meaning change widens the search a lot: changing a trial from 14 to 7 days also affects the pricing FAQ ("cancel anytime within your 14 days"), the onboarding email, the checkout footnote, and the support macro - none of which contain the headline string.

If the new value is unknown or ambiguous, ask before editing. Placeholders like "TBD" shipped to users are worse than the stale text.

## Find how the text is delivered

The place the user points at (e.g. `HeroSection.tsx`) is usually a *consumer*, not the source. Trace forward from the rendering code to the origin:

| Delivery mechanism | How to recognize it | Source of truth |
|--------------------|---------------------|-----------------|
| Literal in markup | Text sits directly in JSX/template/XML | That file (but check for copies elsewhere) |
| Translation key | `t("hero.title")`, `$t(...)`, `intl.formatMessage({ id })`, `AppLocalizations.of(ctx).heroTitle`, `@string/hero_title`, `_("...")` | The locale files for **every** language |
| Key with inline default | `t("hero.title", "Build faster")` / `defaultValue` | Both the locale files **and** the default in code - the default can mask a missing locale entry |
| Natural-language key | `_("Build faster")`, `t("Build faster")` with keys-as-text | The key *is* the old text: every locale file's key must change too |
| Dynamic key | `` t(`hero.${variant}.title`) `` | All variants matching the prefix; static search for the full key finds nothing |
| Constant / config | `const TAGLINE = ...`, `settings.py`, `appsettings.json`, `.env` | The constant; then everything that formats it |
| CMS / database | Fetched at runtime, seed scripts, admin panel | The CMS entry (a human or an API call), plus the seed/fixture so new environments match |
| Generated | Built from a schema, OpenAPI, protobuf, design tokens, a translation platform export | The generator input - hand edits get overwritten |
| Rendered artifact | Images, OG cards, PDFs, videos, app-store screenshots | The design source; flag for a human |

Technique: open the component, read the rendering line, then follow identifiers (`t`, the key, the constant) until you reach a value that is not itself a lookup. Then search for that origin's *consumers* in the other direction (who else reads this key or constant?).

## Key names that embed the old claim

A key is a name for a concept. If wording changes but the concept is the same (`hero.title`), keep the key. If the key encodes the old fact (`pricing.trial14Days`, `hero.codeEditorTagline`, `MAX_UPLOAD_10MB`), the name is now misleading too. Rename it only when it would mislead a future reader, and then rename it **everywhere** (all locales, all usages, tests) in one change. Say so in the report.

## One claim, many independent copies

Often the same claim is typed out by hand in several places that do not share a source. Update all of them for now. Afterwards, *propose* (don't perform) a single source if the duplication is likely to recur - it is a design decision for the owner, not a side effect of a content change.

## Kinds of change and their search handles

The handles that reveal every other place depend on what kind of change it is. Pick the row, then build the vocabulary (`search-vocabulary.md`, `variant-patterns.md`).

| Kind of change | Example request | Search handles |
|---|---|---|
| Wording / copy | "tagline should say *AI-first IDE*" | old text, fragments, key, inline default, old wording in every locale, metadata, docs |
| Rename / terminology | "we say *topic*, not *catalog*" | the old term in every naming convention the stack uses, plus plurals, file names, routes |
| Value | "brand blue is now `#0b57d0`"; "limit is 25 MB" | the old value in every notation (hex/rgb/token; `10 MB`/`10485760`/`10 << 20`/`١٠`), constant names, units per locale |
| Behavior / logic | "free tier gets 3 projects, not 5" | the constant, the check that enforces it, messages and docs that state it, tests that assert it, and what happens to existing data |
| Interface / API | "add a required `region` parameter" | every caller, type or schema, mock, doc, test, SDK/client, OpenAPI |
| Dependency / config | "move from library A to B" | every import/`use`/`require`, manifest, lockfile, config entry, type reference; note the APIs differ, so it is a rewrite per call site |
| Path / structure | "move module `utils` to `shared`" | every import path, alias, build/package config, doc link, CI path filter |
| Schema / data shape | "split `name` into `first_name` and `last_name`" | the column/field, every reader and writer, serializers, fixtures, migrations (new migration, never edit applied ones) |

For each kind, ask who *states*, *relies on*, *quotes*, and *derives from* the claim (`reference-surfaces.md`, last section).
