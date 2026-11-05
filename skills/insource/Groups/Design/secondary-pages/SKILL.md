---
name: secondary-pages
description: 'Secondary DOCUMENTS: ToS, Privacy, Cookies, Acceptable Use (violations + consequences), Contact, About, FAQ, Status, Security, Accessibility, Refund/Shipping, Community, Legal notice, DPA, Takedown, Delete-account, Unsubscribe - catalog in references/, ONE reference per type. Any platform: [web] route, [desktop]/[mobile] surface, [embedded] view; shared contracts across platforms keep ONE canon (usually web; others redirect/embed; offline copies are declared synced duplicates). The agent ALWAYS asks which to create; never invents facts (retention, refund windows, registration numbers from user/config); skips what the project lacks; unclear+material gets asked. Duties: PII/contract data never hardcoded (env/config + json/txt templates); light static, no app logic; a web canon gets full SEO (sitemap, robots, canonical). Placement per document is the user''s call - presentation.md shapes are examples, not a menu. Triggers: terms of service, privacy policy, legal pages, policy pages, contact page, status page.'
---

# Secondary pages - the trust surface of a product

**"Page" is shorthand.** The unit is a *document*, not a web page: it may render as a web route, a
settings surface inside a [desktop] or [mobile] app, a sheet opened in the system browser, a
terminal `--license` output. What every form shares: it keeps promises and carries liability -
what data is stored and used, what counts as a violation and what violations lead to, who the
operator legally is, how to reach a human, whether the service is up. They are read rarely and
trusted completely - which is exactly why a wrong or fabricated one is worse than none.

## Non-negotiables

| Law | Meaning |
|---|---|
| **Ask which pages** | the catalog is long (`references/catalog.md`); present the candidate set for THIS project, then ask the user what to create. Never generate "a full legal set" nobody asked for |
| **Never invent facts** | retention days, refund windows, company registration numbers, governing law, SLA times - each is a question for the user. A plausible filler in a legal page is a promise the operator may not keep. Unclear + material → ask; anything not understood about the project's reality gets a clarification question, never a guess dressed as boilerplate |
| **No page for what is not true** | no shipping policy without physical delivery, no child-privacy page for a 13+ gated product beyond one statement line, no press kit with fabricated logos. Skipping is correct and said so |
| **One owner per fact** | retention lives in Privacy and is linked from ToS; cookie specifics live in the Cookie policy; the FAQ answers by pointer, never by restatement |
| **Plain language is the standard** | a summary line before every dense section; "deliberately confusing terms" is documented research and legislated against - write for the reader who will quote the page in a dispute |
| **PII and contract data never hardcoded** | operator identity, address, phone, email, registration numbers resolve from env/config; emails and message templates live in `.json`/`.txt` template files, not in source strings (`references/engineering.md`) |
| **Light content, zero app logic** | these documents carry no behavior: static content, no runtime logic, no computed state - on the web that means pre-rendered with no hydration (first paint is the feature); in an app it means a plain content view, not a routed feature |
| **ONE canon location per document** | when a project spans platforms ([web], [desktop], [mobile], [embedded]) and shares the same business contracts, the document lives ONCE - canonically the web copy when a web surface exists - and other platforms reach it by redirect (open in system browser) or embedding, never by forking the text. A bundled offline copy is a DECLARED synced duplicate with the canon as its source (same-change duty), not a second original |
| **SEO where a web canon exists** | indexable by default, in sitemap.xml, canonical set, real meta descriptions, robots-aware, localized with hreflang when the project has locales (`references/engineering.md`) |

## Workflow

1. **Learn the project** (from the repo, not from the user): product type (digital/physical/SaaS/UGC),
   accounts + data processed, payments, jurisdictions served (footer/company config), locales,
   framework + rendering modes, existing pages. Evidence wins; anything missing becomes a question.
2. **Present candidates from the catalog, then ask.** Group by family (legal / trust / support /
   commerce / lifecycle / company) with one line each about whether this project plausibly needs it,
   and ask which pages to create. Also ask for every project-specific fact the chosen pages will
   require in one round (operator identity, contact channel, data classes, retention, refund stance,
   governing region) - never one ping per field, never an invented default.
3. **Per chosen page: read its reference** (`references/<page>.md`) and draft with it. The reference
   owns: required blocks, professional writing rules, the questions, the failure patterns.
4. **Decide canon location and placement per document.** Canon first: one canon per document -
   with a web surface it is the web route (linkable, updateable without a store release); app
   platforms [redirect to the canon] (system browser / deep link) or [embed] it; a project with no
   web surface picks its own canon (docs host, bundled asset) and says where. Placement is then
   decided with the user: `references/presentation.md` lists common shapes (route, footer, signup
   inline, modal, accordion) as EXAMPLES, not an allowed set - a project may mix or invent; what
   binds every shape is the reader contract there: full current text one step away, stable canon
   URL, consent gates the whole document.
5. **Build under the engineering duties**: content-as-data (markdown/structured files), config-driven
   identity, static/prerender, SEO metadata, sitemap + robots entries updated in the same change.
6. **Verify**: every stated fact traces to a user answer or config; every link resolves; the
   document renders with scripts disabled (web) / without network (app surface reading its own
   view); a `curl` of the canonical web URL returns the full text in the first packet (static
   proof); the sitemap contains the route; the "last updated" date is today's, not decorative;
   and NO second platform carries its own copy of text the canon owns.

## Scope

- This skill writes these pages as **professional, honest documents and their engineering** - it is
  not legal advice; every legal page carries a plain note ("review with counsel for your
  jurisdictions") and the skill never claims a document is compliant, only that it is transparent.
- The product's main pages, marketing voice, and SEO audit beyond these pages belong elsewhere
  (`seo`, `readme-md`'s voice rules inform copy, `impeccable` owns UI craft).

## References

| File | Owns |
|---|---|
| `references/catalog.md` | the complete page list by family, with the needs-it? filter and pointers |
| `references/presentation.md` | placement modes per page type: route / footer / modal / new tab / accordion, accessibility rules |
| `references/engineering.md` | config-driven identity, message template files, static rendering, SEO/sitemap/robots |
| `references/<page>.md` | one per page type: required blocks, professional writing, questions to ask, failure patterns |
