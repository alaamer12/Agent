# Engineering duties - config identity, template files, light rendering, SEO

Platform-neutral rules; [bracketed] stack examples are illustrative.

## 1. Identity and PII come from config - never from source

Contract data (operator name, legal entity, registration number, address, phone, email, VAT,
support hours) appears in these documents constantly and changes slowly. Hardcoding it is the
failure the user named: a typo'd registration number baked into three bundles is a false legal
statement shipped everywhere at once.

```text
env/config ->  legalContact: { entity, address, regNumber, email, phone }
documents  ->  render/placeholders: " {{legalContact.entity}} ", never literals
```

- [`.env` / config file] holds the values; [a typed schema with fail-fast validation] per the
  project's own golden-rule style: a missing contract value at build time is LOUD, not a page
  silently rendering `undefined GmbH`.
- Machine-readable for the user, invisible spam-food for scrapers where shown on web: obfuscate or
  use a form; never publish a raw personal phone.
- App surfaces read the same config at build time - NOT a second hardcoded copy (sync-block law:
  one canon of each value).

## 2. Message templates are files, not strings

Transactional mail and notice templates (welcome, reset, policy-change notice, receipt) are
secondary-page content in envelope form:

- one file per template: [`.txt`] for plain, [`.json`/`.yaml`] for structured (subject/body/
  variables), stored in a `templates/` folder the project declares;
- variables (`{{name}}`, `{{entity}}`) injected from config; no email body composed from
  string concatenation in application code;
- templates are reviewed like legal text - a "refund takes 30 days" string in a mail template
  contradicts a 14-day refund policy unless both trace to one decision.

## 3. Light rendering: static by default, zero app logic

These documents have no state, no interactivity, no data fetching (contact FORM submission is the
one exception and it is a boundary, not a page feature):

- [web]: prerender/SSG - the full text is in the first packet (verifiable with `curl`); no
  hydration, no client router needed, no framework runtime on the route if the stack can avoid it
  ([Astro], [Next.js SSG], [plain HTML], [static-gen] all fine - the stack's own idiom wins);
- [desktop/mobile/embedded]: a plain content view (markdown/bundle asset) with no network fetch for
  text that is shipped anyway;
- content-as-data: documents live as [markdown/structured files] under version control; editing a
  policy is a file change, not a code change - diffable, reviewable, and the "last updated" date
  comes from the change itself, never hand-typed.

## 4. SEO where a web canon exists - they are canon pages

Policy pages rank for things users genuinely search and are the URLs others cite:

- indexable by default; `robots.txt` allows them; no `noindex` on any legal document (a private
  preview DRAFT is noindexed while drafted, the moment it speaks of itself as current it must
  be public);
- real `<title>` + meta description per document ("Refunds - {Product}", not boilerplate);
- `<link rel=canonical>` to the own URL (they get copied across mirrors);
- add every document to `sitemap.xml` in the same change that creates it; lastmod from the file's
  actual change date;
- structured data [schema.org `Organization`/`LegalService`] where the project already emits JSON-LD -
  contact and legal-notice pages benefit; only with real values from config, never a template of
  fake fields;
- localized: `hreflang` pairs + one URL per language;
- internal links: the footer block links the whole set (crawl path to every document); documents
  cross-link (ToS↔Privacy↔Cookies↔AUP) so the set reads as one system.

## 5. Honesty gates (over-engineering stops)

- No badge, certification, "GDPR compliant", SOC2 logo, or audit claim unless the project actually
  has it - say "not stated yet" and ask.
- Dates are real: `Effective:` / `Last updated:` from the actual change; a future or decorative
  date is a fabrication.
- Generator output (form-fill "Your Company LLC") must be caught by review: any placeholder that
  survived into the build is a defect, checked before writing the file - grep for the generator's
  residue.
- Error/maintenance pages: honest one-liner + status link + retry; no fake "we fixed it".
