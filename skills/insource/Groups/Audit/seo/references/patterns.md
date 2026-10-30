# Patterns P1-P17 — Principle First, Per-Stack Adapters Second

Each pattern: **principle** (why it scores), **generic recipe** (framework-neutral), **stack adapters** (idiomatic wiring). Stack choices are illustrative — if the repo already has a working convention, reuse it. Options in [brackets] are examples, not mandates.

Reference stacks used below: **Next.js/SvelteKit/Nuxt** (TS), **Blazor/Rails/Laravel** (C#/Ruby/PHP), **Dioxus/Leptos** (Rust), **static/SSG** (Hugo/Eleventy/plain HTML).

**Every windowed pattern (P1 title, P2 description, P3 h1, P9 slug) must run its value through a data gate — templates may not assume entity data fits their windows; see `data-gates.md`.**

---

## P1 — Keyword-as-Title Template, Tuned to the Length Window
**Earns:** Title keyword 8 + position 6 + length 6 = 20/27.
**Principle:** title = a *template with the keyword at token 1*, appearing exactly once, with a fixed suffix whose length keeps the total in 30-60 chars for typical entity names. Content editors can't maintain this; templates can. Length is enforced by **pixel width** by search engines — keep the primary query inside the first ~50 chars.
**Recipes by page type** (illustrative — `{ }` = entity data, always keyword-first):
`{Entity} | {Site}` (profile) · `{A} vs {B}: {deciding difference}` (comparison) · `{Category} for {Audience} | {Brand}` (landing) · `{Term}: What It Means and Why It Matters` (glossary) · `{Service} in {Location}` (location).
**Rules:** every title unique site-wide (duplicates usually mean the template prints the same string everywhere); a promise in the title (year, number, "free") must be true on the page; keyword stuffing or generic titles ("Home", "Untitled") are rewrite triggers — search engines replace them with the H1/anchor text, costing the click. Align title with h1 without copying it (P3 trap). **Gate:** measure `MAX(LENGTH(name))` before shipping — a 78-char entity name silently breaks the window; degrade via keyword-atomic ladder (data-gates.md), keep the query inside the first ~50 chars (pixel truncation ≈600).
**Anti-pattern → fix:**
```razor
@* Blazor — anti-pattern: name buried after marketing text, no length control *@
<PageTitle>Dashboard - Welcome to Our Amazing Platform - @entity.Name</PageTitle>
<PageTitle>@entity.Name — Company Profile | MySite</PageTitle> @* keyword first, once, sized *@
```
```ruby
# Rails — layout yields the per-page keyword-first title
content_for :title, "#{entity.name} — #{@site_name}"
```
```ts
// Next.js App Router
export async function generateMetadata({ params }): Promise<Metadata> {
  const e = await getEntityCached(params.slug);
  return { title: `${e.name} | ${SITE}` };   // keyword first, once
}
```

## P2 — Keyword-Bearing Fallback Description
**Earns:** Meta 5/5, unlosable.
**Principle:** two-layer description — real copy if present, else a **template that interpolates the keyword** (+ one computed fact for uniqueness). There must be no data state, short of entity nonexistence, that yields a keyword-less `<meta name="description">`.
**Recipe:** `description = entity.metaDescription || truncate(entity.copy) || templateWithKeyword(entity, stats)`. Sanitize/limit to ~160 chars at a word boundary. **Gate:** truncation must never cut before/at the keyword — front-load the keyword in the first ~50-60 chars (mobile renders ~120), assert `contains(keyword)` AFTER the cut, else rebuild from the fallback template (data-gates.md).
**Adapters:** [Rails: helper in `ApplicationHelper`] [Blazor: same template in the page's HeadContent/model] [Laravel: Blade `@isset`/`??` chain] [Dioxus/Leptos: function returning `String`] [static: front-matter default in the template].

## P3 — Single, Keyword-Only `<h1>` in Server HTML
**Earns:** Headings keyword 5 + position 5 + length 2 + count 4 = 16/20.
**Principle:** the page's `<h1>` contains only the entity name (keyword = entire h1 = position 1), exists exactly once, in raw HTML, ≤ 40 chars. Placement discipline, not styling, makes it score: it must be emitted **above/outside every client-render boundary** (see P13).
**Rules:** badges/subtitles/prices render as siblings, never inside h1. Interactive UI labels sections with `aria-labelledby` on `<section>`s instead of emitting `<h1>/<h2>`. Grep the whole route subtree for `<h1` before declaring done — a second one anywhere in first-packet HTML zeroes the count check.
**h1 ≠ title trap:** if the title is `{Name} | Site` and the h1 is `{Name}`, score models that strip the suffix see them as identical (−2). Keep a differentiator: h1 suffix span (`{Name} <span class="sr-only">profile</span>`), or a title template variant — and re-verify after any title copy change.

## P4 — Keyword-Interpolated Heading Templates
**Earns:** Headings subheading 2/2 (one keyword heading = half credit).
**Principle:** every server-rendered h2/h3 template interpolates the entity name. Generic labels (`Performance`, `About the fund`) score 0; ship ≥2 keyword-bearing headings.
```rust
// Dioxus-style (illustrative): headings built from entity data, never hand-written per entity
h2("{t("about")} {entity.name}"),
h3("{entity.name} — {t("performance")}"),
h3("{t("details")} {entity.name}"),
```
Blade/ERB equivalent: `<h2>نبذة عن {{ $entity->name }}</h2>` — the wording pattern is fixed, the value is dynamic.

## P5 — The Hidden Prose Engine (crawler layer)
**Earns:** Body words 14/14; feeds P8.
**Principle:** decouple "what the crawler reads" from "what the user sees": a server-rendered prose block, rendered **first in the page body**, visually hidden or integrated invisibly. CSS is irrelevant to the HTML parser — `sr-only`-style clipping (1px absolute) and even `display:none` still count as words; prefer visually-hidden-but-focusable patterns for accessibility.
**Two flavors:** [data-dependent — prose built from entity fields; richer, degrades with gaps] or [template-driven — keyword-interpolated boilerplate; robust, risks near-duplicate copy across entities (doorway-content exposure — vary paragraphs per entity)]. Default to data-dependent with P2-style keyword fallbacks.
**Quality gate (when the ceiling, not just the floor, matters):** template prose must pass the mask-the-name test in `content-quality.md` — two pages of a family should not read identically once the entity name is hidden. Branch paragraph selection on data shape, interpolate numbers/dates/names over adjectives, and avoid AI-tell fill patterns.
**Recipe:** `class="sr-only"` (Tailwind) or a global `.visually-hidden` utility (Bootstrap `sr-only`, custom clip CSS) wrapping `<article>` with h2/paragraphs.

## P6 — Repetition by Construction
**Earns:** Body keyword 14/14 (needs 3; patterns produce 10+).
**Principle:** every paragraph template interpolates the entity name — intro (×2), one sentence-cluster per populated fact, performance/stats lines, closing. Mentions arise from templates, not hand-copy. Repetition penalties apply to titles only, never body.
**Guard:** if all inputs are empty, render nothing (return null / omit the block) — never emit an empty shell that fakes structure.

## P7 — Raw `<img>` with Keyword Alt
**Earns:** Media 4/4.
**Principle:** the scored element is a literal `<img … alt="keyword…">` tag in raw HTML — use the platform's **bare tag**, not an optimizer wrapper that may render `<picture>`/placeholder/`srcset` indirection or omit alt server-side. The `alt` is generated from entity data (localized name + optional qualifier), **never from filenames** (filenames are usually English/generic and miss localized keywords). The crawler reads the attribute; hosting/CDN never matters.
```php
{{-- Blade --}}
<img src="{{ $entity->logo_url }}" alt="{{ $entity->name }} - {{ $entity->company }}" width="48" height="48" loading="eager">
```
```csharp
@* Blazor *@
<img src="@entity.LogoUrl" alt="@($"{entity.Name} - {entity.Company}")" width="48" height="48" />
```
React: `<img>` instead of `next/image` for the crawler-critical logo (keep `width/height` for layout stability). Watch the NULL case: a ternary that omits the tag entirely zeroes the check — prefer a fallback image with keyword alt, or accept the data gap consciously.

## P8 — Lean Prose for the Text/HTML Ratio (≥ 2%)
**Earns:** Code 3 points.
**Principle:** ratio = visible-text chars ÷ total response bytes. Runtime payloads (hydration/streaming JSON), inline SVG icon sets, and class-string bloat are pure denominator. Fix on both sides: add plain-tag prose (P5/P6), and remove icon-heavy styled chrome from the first-packet crawl path (move it behind client boundaries or into composition per P13) — the same facts re-expressed as sentences cost ~10× fewer bytes of markup.
**Recipe:** audit with the script's ratio report; target ≥ 2.5% for headroom. External `<link rel="stylesheet">` (the other 3 points) is automatic in most stacks — just don't inline critical CSS *exclusively*.

## P9 — Keyword-Transliterated Slug Column
**Earns:** URL keyword up to 5/10.
**Principle:** stable, keyword-bearing, ASCII-safe slugs (`[a-z0-9-]{3,100}`: lowercase, transliterate/convert whitespace to hyphens, strip the rest, cap length, uniqueness with collision suffix). Store as a column, backfill, and route **all** URL generation (canonicals, sitemap, internal links, JSON-LD `url`) through the same `slug || publicId || id` fallback chain. Legacy ID URLs → permanent 301 to slugs, kept ≥ 6 months.
**Note:** word-level scoring means a Latin slug still earns partial credit for an Arabic keyword — transliteration bridges languages.

## P10 — Fast Head Lane (data for the head must be cheap)
**Earns:** the timing half of Title/Meta — nothing scores if it arrives after the budget.
**Principle:** the data feeding title/canonical/description is fetched on a **cross-request cached lane** ([full-route cache] [fragment cache] [ISR/SSG] [build-time] — not necessarily "in-memory"); the data feeding the h1/visible body may stay per-request-deduped so it reflects fresh entity data (a stale name flips the keyword checks). Two lanes, deliberately.
**Failure signature:** head tags exist but score 0 → TTFB/streaming: measure with `--mode raw` (content fine) vs default (points lost) → fix the data path, not the markup.
**Guard:** cache miss/error in the metadata path must degrade to safe noindex metadata, never a 500 with no head.

## P11 — One Metadata Funnel + Locale Variant Correctness
**Earns:** indexing hygiene (not directly scored): canonical per language variant, hreflang set, OG/Twitter, `robots: index,follow` (+ `noindex` on not-found/error metadata).
**Principle:** a single shared builder every route must use — hand-written tags drift; a funnel is patched once.

**Language-variant scheme:** [path prefix `/ar/…`] and [ccTLD/subdomain] are the preferred schemes; [query param `?lang=`] is treated as a weaker locale signal and is fragile — search crawlers may send no `Accept-Language` and can cluster param variants as duplicates. If the codebase already uses params (as SNDUK does), it *can* work **only** with rigor: the discriminator is carried consistently through canonical, hreflang targets, internal links, and sitemap `<loc>`; each variant's body is genuinely localized (not one language with translated chrome); and never mix schemes on one site. When building fresh: prefer path prefixes.

**Hreflang rules (validate on every multilingual audit):**
- **Self-reference:** every page includes itself in the hreflang set — the single most common failure.
- **Reciprocity:** if A declares B, B must declare A, or both are ignored. Report per-pair; one broken pair does not invalidate the cluster.
- **Codes:** ISO 639-1 language + optional ISO 3166-1 region (`en`, `en-GB` — never `en-UK`, never region-only). `x-default` is a recommended fallback for unmatched users, **not a validity gate**.
- **Three placement methods** (HTML `<link>`, HTTP `Link` header, sitemap `<xhtml:link>`); if multiple are used they must agree, or conflicting pairs get dropped. At [10-20+] locales prefer sitemap-based (head annotations cost ~1.5 KB/page); plan 2K-5K URLs per sitemap when carrying full hreflang (50 MB binds before the 50K `<loc>` cap; `xhtml:link` children don't count toward it).
- **Canonical interplay:** the canonical URL must itself be inside the hreflang set, or all annotations on the page are ignored; never cross-locale canonical (kills the non-canonical locale). Split sitemaps by content type, not locale (reciprocity makes per-locale splits unmaintainable).
- **Framework trap:** in Next.js, `alternates.languages` does **not** auto-include the current page in the sitemap's `<xhtml:link>` set — add the self entry explicitly.
- **Consistency:** one absolute-URL format — protocol, www-vs-not, trailing slash, case — identical across canonical, hreflang, sitemap, internal links; non-canonical formats 301 to canonical.

Also: `<html lang>`/`dir` must match the rendered content language (derive from the served variant, not the country alone); OG locale per variant; translated metadata (title/description) in every language — visible content, not attributes, decides what a page is "in".

## P12 — Deployment Basics
**Earns:** URL 5/10 (HTTPS) + crawl integrity.
HTTPS everywhere with canonical scheme; consistent trailing-slash policy; `robots.txt` allowing the scored sections and referencing the sitemap; sitemap = cross-product of indexable routes × language variants (skip auth/dashboard/admin/API).

## P13 — Stream Survival (the meta-pattern)
**Earns:** nothing alone; **everything, collectively.** The most common site-wide 100→0 killer.
**Principle:** no component between the document and the content may replace server HTML with a loading placeholder. The universal anti-pattern: a client-side initialization gate that renders a fallback until some client effect runs — every descendant page ships an empty body while the browser (and DevTools) shows a perfect DOM after hydration.
```tsx
// React — ANTI-PATTERN (kills SSR body for ALL children)
const [ready, setReady] = useState(false);
useEffect(() => { setReady(true); }, []);
if (!ready) return <Spinner />;        // server render: ready=false → spinner-only HTML
// FIX: initialize synchronously (or render children on server + first paint):
if (!ready && mounted) return <Spinner />;
```
```csharp
@* Blazor — ANTI-PATTERN: interactive components without prerender *@
<RootComponent @rendermode="new InteractiveServerRenderMode(prerender: false)" />
@* static SSR / prerender:output default → real HTML for crawlers; interactive-after-load only *@
```
Same trap in [Vue/Nuxt: `v-if="hydrated"` wrappers] [Dioxus/Leptos: client-only rendering of fullstack routes] [any SPA without prerender/SSG] — the fingerprint is identical: **head checks pass, every body check is 0**.
**Companion techniques:** (a) critical content (h1, prose, img) rendered by server components *above* client boundaries; (b) **prop-injection composition** — pass a *server-rendered* block into a client component as a slot/child/prop so its HTML enters the stream at its exact visual position without restyling the UI ([React children-as-props through the RSC boundary] [Blazor `RenderFragment` from server side] [Blade partial included server-side] — natural in Rails/Django, which render server-first by default).

## P14 — Entity Structured Data in the Same Packet
**Earns:** no on-page points; compounds indexing/rich results with work already done.
**Principle:** emit JSON-LD for the entity type ([Product] [Article] [FAQPage] [Organization/FinancialService] [BreadcrumbList] — pick by schema.org, not habit) from a server component, with localized names; keep its `url` consistent with the canonical (same lang variant, same slash policy). Reuse existing generated Q&A prose as `FAQPage` — zero new copy.
**Detection caveat (audit discipline):** raw-HTML fetches cannot see schema injected by client-side JS (many CMS plugins do this) — "no structured data found" is only a valid finding from a rendered check (browser / Rich Results Test), never from source alone. schema.org validity also ≠ rich-result eligibility; validate against the target engine's requirements.
**Bilingual entities:** add `{alternateName: [name, nameLocalized]}` to the entity node — one entity consolidates searches in both languages instead of two competing profiles.

## P15 — First-Packet Link Fabric (discovery without JS, independent of the sitemap)
**Earns:** 0 direct rubric points — and losing it silently caps every other page's floor, because PageRank distribution and discovery ride on it.
**Principle:** a hub page (category/list/landing) must emit **real `<a>` elements to every entity page in server HTML**, regardless of what the interactive UI does — the sitemap is not a substitute; a link inside crawlable HTML is stronger evidence of importance than a sitemap line.
**Recipe:**
- Server-rendered entity list on the hub — either a genuine visible grid or a visually-hidden `<ul>` of entity links with localized anchor text (plus one h2 naming the list).
- **Coverage ≥ entity count**: a hardcoded cap (limit 100 vs 1000 entities) silently strands everything beyond it — audit caps and paginate instead.
- **Tenant scoping:** links must respect the entity's owning locale/region/workspace (never a `sa` entity link under `/eg/`); same rule for sitemap emission — entities appear only under their own locale.
- Breadcrumbs server-rendered + `BreadcrumbList` schema; related-entity cross-links in server prose (spokes ↔ hub).
- External links: `rel="noopener"`, and don't let an orphan page exist with 0 inbound links anywhere in crawlable HTML.

## P16 — Graceful Degradation & Mismatch Guards (protect the floor)
**Earns:** keeps every other pattern from turning into an indexing liability.
**Principles:**
- **SEO calls degrade, never block:** every data fetch behind scored content gets a default on failure (null/empty → the P2 keyword-bearing fallback path, prose engine omits its section rather than emitting an empty shell). No scored element's presence depends on an optional query succeeding.
- **Metadata miss → safe `noindex` branch**, never a 500 without a head or a title-less page.
- **Mismatch guard:** entity doesn't belong to the URL's locale/tenant → redirect to the owning scope OR noindex+404 metadata — never render a scoreable duplicate in the wrong scope (and keep sitemap + hub links aligned so crawlers rarely hit it).
- **Shared/family layout leak:** list-level metadata and CollectionPage schema declared in a family layout apply to ALL child routes — scope them to the list segment ([per-segment layouts] [route-group metadata] [conditional on children]) or a detail page ships CollectionPage + a homepage title leak.
- **Silent-failure discipline for audits:** the same catch-defaults that protect the score hide regressions — pair every fail-silent SEO component with a completeness signal (admin health check, the mask-the-name/coverage audits in `content-quality.md`) so data gaps surface as data gaps, not as quietly-lost points.

## P17 — One Funnel, Separate Files (the architecture pattern)
**Earns:** no points directly — and it is the reason the other 16 stay earned. Duplicated SEO logic silently degrades a subset of pages while the rest look perfect.
**Principle 1 — never duplicate:** all metadata/SEO *building* lives in shared functions that similar pages call with data (builders + route helpers + copy modules). Copy-pasted per-route metadata code drifts within weeks — one route gets the cached lane, its sibling doesn't; a suffix change lands in seven of twelve copies. The manager P10 breach in the reference repo is textbook drift: the fund path used the cached getter correctly; the manager path re-implemented the shape and forgot the call site. Same for prose/heading templates, alt builders, link-fabric components — one implementation, called everywhere.
**Principle 2 — keep SEO-files separated from business-logic files:** SEO artifacts sit in dedicated, greppable locations, not embedded in UI/business components:
- `lib/metadata/` (or `app/Seo/`, `src/seo/`, `features/seo/`) — title/description builders, copy templates, truncation/gate utilities, schema constructors
- `components/seo/` — JSON-LD renderer, link-fabric/list components, prose-engine renderers
- route-local `*_seo_*` files — page-specific prose templates that *use* the shared helpers, never re-derive them
Business components consume the layer; they hold **no keyword logic, no title arithmetic, no schema payloads**. Payoff: an audit is a folder-scan, gate tests target one module, framework migration touches one layer, and `/seo` can trust the map.
**UP-mode recipe when one page fails and its siblings pass:**
1. **Find the funnel, fix once inside it.** Never hot-patch the failing route's local copy.
2. **Count copies before editing** — grep for the failing construct (title literal, metadata function shape); ≥2 variants means *consolidate first*, then fix.
3. **Express page differences as data, not code forks** — a builder parameter (`subPage: 'compare'`, `ogType`, copy-table keys), not a per-route fork.
4. **Sweep the blast radius** — after one funnel fix, re-audit every route that consumes it; drift usually hides in more than the reported page.
```ts
// ANTI — N routes drift apart; route 7 silently loses the cached lane
async function generateMetadata() { const x = await trpc.funds.getById… /* copy #7, unoptimized */ }
```
```ruby
// FIX — any stack: route passes the discriminator, the funnel owns data access + templates
seo page: :funds_compare, entity: @fund   # one builder, one cache lane, one copy table
```
