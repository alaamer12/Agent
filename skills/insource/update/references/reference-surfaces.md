# Reference Surfaces: Where a Claim Hides (Implicit Search)

Implicit search means asking, for each surface, "could this state or depend on the changed claim?" Walk the whole catalog for a meaning change; for a pure wording change, the first four groups plus any surface that quotes the text are usually enough.

## Contents
1. Presentation
2. Discoverability metadata
3. Accessibility text
4. Verification artifacts
5. Documentation and explanation
6. Configuration and packaging
7. Messages sent outside the app
8. Data and seeds
9. Legal and policy
10. Records and generated output

## 1. Presentation
| Surface | Look for | Typical action |
|---------|----------|----------------|
| Component markup | Literal text, props defaults, `defaultValue`/fallback strings | Update |
| Translation files, all languages | Key + translated values | Update every locale (see `localization-and-i18n.md`) |
| Storybook / design-system docs | Stories with the old copy as args | Update |
| Empty states, tooltips, toasts, placeholders, button labels | Text that repeats the claim in context | Update when it asserts the old fact |
| Marketing pages that reuse the section | Footer blurbs, pricing tables, comparison pages | Update |

## 2. Discoverability metadata
`<title>`, `meta description`, Open Graph and Twitter card tags, JSON-LD / schema.org, `sitemap` descriptions, `manifest.json` / PWA `name`/`description`, RSS feed descriptions, app-store listing text, package registry descriptions (`package.json`, `pyproject.toml`, `Cargo.toml`, `.csproj`). These are copies users and search engines see before they see your page. Action: update; flag store listings and registries that need a manual publish.

## 3. Accessibility text
`alt`, `aria-label`, `aria-description`, `title` attributes, screen-reader-only spans, captions and transcripts. Often forgotten because they are invisible in the UI. Action: update; they must match what the visible text now says.

## 4. Verification artifacts
| Surface | Notes |
|---------|-------|
| Unit/component tests | Assertions on rendered text (`getByText`), on keys, on values |
| E2E tests (Cypress, Playwright, Selenium) | Selectors by text; page titles |
| Snapshots | Regenerate with the test runner after the source change; review the diff, never hand-edit |
| Visual regression baselines | Flag: a human reviews and approves new baselines |
| Test names and descriptions | `it("shows the 14-day trial banner")` becomes a lie after the change |
Update expected values to the new truth. If a test exists *to protect the old behavior*, stop and ask; that is a behavior decision, not a copy change.

## 5. Documentation and explanation
README, `docs/`, wikis, ADRs (see "Records"), API reference and OpenAPI `description`/`summary`, JSDoc/docstrings/XML-doc comments, inline code comments that explain the old value ("// 10 MB limit"), CONTRIBUTING and onboarding guides, tutorials with screenshots or recorded output, example code and sample `.env` files, FAQ and help-center articles. Paraphrases live here: "uploads are capped at ten megabytes" never contains `10`. Action: update prose; flag screenshots and videos.

## 6. Configuration and packaging
Config files (`*.yaml`, `*.toml`, `*.json`, `.env.example`), feature flags, defaults in infrastructure code, installer/updater metadata, `tauri.conf.json` / `app.json` / `Info.plist` / `AndroidManifest.xml` display names, CI scripts and workflow steps that grep for strings, Dockerfile labels. Action: update; check CI scripts that assert text (they fail late and confusingly).

## 7. Messages sent outside the app
Transactional emails, push notifications, SMS templates, in-app announcements, Slack/Discord bot messages, customer-support macros, status pages, social profiles. Often live in a third-party dashboard, not in the repo. Action: update what is in the repo; list the rest under "needs a human".

## 8. Data and seeds
Database seed scripts, fixtures, mocks, demo data, migrations that insert default copy, sample content for new tenants. Existing production rows are data, not code: do **not** rewrite them silently. Update seeds so new environments are correct and report that production data needs a deliberate migration or CMS edit.

## 9. Legal and policy
Terms of Service, Privacy Policy, cookie banners, licenses, data-processing and retention statements, SLAs, refund text. These change legal meaning and usually need an effective date or version bump and sign-off. Action: do not edit silently; propose the exact change and flag it.

## 10. Records and generated output
| Surface | Rule |
|---------|------|
| CHANGELOG, release notes, blog posts, migration files, ADRs | **Leave.** They record what was true then. Add a new entry for this change if the project keeps a changelog |
| Build output (`dist`, `build`, `.next`), minified bundles, source maps | Never hand-edit; rebuild |
| Lockfiles, vendored code, third-party docs | Leave |
| Generated code/docs (OpenAPI clients, protobuf stubs, typedoc) | Edit the input, regenerate |

## Questions that surface implicit references

- Who else *states* this claim, in any wording or language?
- Who *relies* on it (a price that totals feed into, a limit a validator enforces, a name a script greps for)?
- Who *quotes* it (tests, docs, emails, screenshots)?
- Who *derives* it (SEO tags generated from the title, slugs generated from the name, analytics event names built from labels)?
- What would a user, a search engine, a screen-reader user, and a translator each still see saying the old thing?
