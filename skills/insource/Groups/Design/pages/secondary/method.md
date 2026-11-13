# secondary — trust documents (`/pages secondary`)

Owns `PAGES.md` §5 (document rows), exclusions with kind=secondary, and the documents'
canon/placement decisions. The list lives in §5; the *content method* lives here.
**"Page" is shorthand — the unit is a document**: it may render as a web route, an in-app
surface, a system-browser sheet, or a terminal `--license` output. These documents are read
rarely and trusted completely, which is exactly why a wrong or fabricated one is worse than
none.

## Laws specific to this mode

| Law | Meaning |
|---|---|
| **Never invent facts** | retention days, refund windows, registration numbers, governing law, SLA times — each is a question for the user. A plausible filler in a legal page is a promise the operator may not keep. Unclear + material → ask; never a guess dressed as boilerplate |
| **No document for what is not true** | no shipping policy without physical delivery, no child-privacy page beyond one statement line for a 13+ gated product, no press kit with fabricated logos. Skipping is correct and said so |
| **ONE canon per document** | when a project spans platforms and shares contracts, the text lives once — canonically the web route when one exists; other platforms redirect (system browser) or embed; a bundled offline copy is a DECLARED synced duplicate with same-change duty, not a second original |
| **Plain language is the standard** | a summary line before every dense section; write for the reader who will quote the page in a dispute — deliberately confusing terms are documented and legislated against |
| **PII/contract data never hardcoded** | operator identity, address, emails resolve from env/config; message templates live in `.json`/`.txt` files, not source strings (`references/engineering.md`) |
| **Light content, zero app logic** | static content, no runtime behavior — on web: pre-rendered, no hydration (first paint is the feature); in apps: a plain content view. A web canon gets full SEO: indexable, sitemap, canonical, real meta descriptions, hreflang when locales exist |

## Workflow

1. **Learn the project from the repo**: product type (digital/physical/SaaS/UGC), accounts and
   data processed, payments, jurisdictions, locales, rendering modes, existing pages. Evidence
   wins; gaps become questions.
2. **Present candidates from the catalog, then ask** — in one round, including every
   project-specific fact the chosen documents need (operator identity, contact channel, data
   classes, retention, refund stance, governing region). Never a full legal suite nobody asked
   for, never one ping per field.
3. **Per chosen document: read `references/<type>.md`** — the type reference owns required
   blocks, professional writing rules, its questions, its failure patterns.
4. **Decide canon and placement.** Canon first (rule above; a no-web project picks and states
   its own canon). Placement is the user's call — `references/presentation.md` shapes
   (route/footer/modal/accordion) are examples, not a menu; what binds every shape: full
   current text one step away, stable canon URL, consent gates the whole document.
5. **Build under the engineering duties** (content-as-data, config-driven identity, static
   rendering, sitemap/robots entries in the same change).
6. **Verify**: every stated fact traces to a user answer or config; every link resolves; the
   document renders scripts-off / network-off; `curl` of the canon URL returns the full text
   in the first packet; sitemap contains the route; the "last updated" date is real; and no
   second platform carries its own copy of canon-owned text.
7. **Register** every created document as a §5 row in `PAGES.md` — one row, one canon, one
   build per `../references/output-contract.md`; declines as kind=secondary exclusions with reasons.

## Scope boundary

These are professional, honest documents — not legal advice: every legal page carries a plain
"review with counsel for your jurisdictions" note, and the skill never claims compliance,
only transparency. Marketing/main voice belongs to `main` and the design skills; SEO audit
beyond these pages to `seo`.

## References (this mode)

| File | Owns |
|---|---|
| `references/catalog.md` | the complete document list by family with needs-it? filters |
| `references/<type>.md` | one per type (25): required blocks, writing rules, questions, failure patterns |
| `references/presentation.md` | placement shapes as examples + the reader contract every shape must meet |
| `references/engineering.md` | config-driven identity, template files, static rendering, SEO/sitemap/robots |