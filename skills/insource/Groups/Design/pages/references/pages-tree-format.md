# The pages tree — `<docs>/pages/` (the one schema owner)

The artifact is a **route-mirroring tree** under the project's docs root: `<docs>/pages/`.
The filesystem path *is* the route. Every page is one spec file; every directory carries a
shard `index.md` that maps its contents. The root `index.md` is the full typed map of every
page. This tree is the contract every downstream skill reads — `prototype`, `impeccable`,
`planner`, `seo`, `collection` — and updates in the same change it adds, removes, or renames a
page. Nothing outside the tree maintains a screen list.

## 1. The tree convention

| Form | Means | Route |
|---|---|---|
| `<page>.md` | one static page | `about.md` → `/about` |
| a directory | a segment that groups pages | `funds/` → `/funds/…` |
| `_.md` inside a directory | the segment's root page | `funds/_.md` → `/funds` |
| `[param].md` | a dynamic segment (Next.js-style brackets; any param name) | `funds/[slug].md` → `/funds/:slug` |
| `[...param].md` | a catch-all dynamic segment (Next.js-style) | `docs/[...slug].md` → `/docs/*` |
| `index.md` | the directory's shard map — **never a page** | no route |

Nesting recurses: a directory inside a directory follows the same rules.

```
<docs>/pages/
├── index.md            ← root shard: the full typed map
├── _.md                → /              (the tree root is itself a segment)
├── about.md            → /about
├── disclaimer.md       → /disclaimer
└── funds/
    ├── index.md        ← shard map of funds/
    ├── _.md            → /funds
    ├── [slug].md       → /funds/:slug
    └── funds-category/
        ├── index.md    ← shard map of funds-category/
        ├── _.md        → /funds/funds-category
        └── [id].md     → /funds/funds-category/:id
```

- The tree root is a segment too: `pages/_.md` is `/`.
- A grouping directory with **no route of its own** (e.g. `legal/` when only `/legal/terms` and
  `/legal/privacy` exist) has **no `_.md`** — only its `index.md` and children. Never invent a
  segment root the product does not have.
- Access is never encoded in naming — `_.md` is an index leaf, not a "private" marker; access
  lives in the page's frontmatter.
- The `url` frontmatter of a dynamic page carries the bracket form (`/funds/[slug]`); the
  runtime path pattern is the project's own.
- **A route that only hands off is a redirect, not a page file** — a recorded decision in the
  map's Redirects section (§5). This is the precedence over "a route that exists is a page that
  exists": the route is real evidence, but its unit is a redirect, so it gets no file.
- A modal or a transient state is **not a route** — it gets no file. It is recorded as a decision
  (state/modal) in the map, or as depth inside its owning page (§3).
- A framework fallback (404, offline) is a **complementary** screen whose trigger is "no route
  matched" / "network down". Record it on the map with that condition; do not invent a literal
  path the product never routes.

## 2. Shard indexes — every directory, every depth

The docs methodology this tree follows: **every directory carries exactly one `index.md`** that
describes its contents — a framing line, then each file/subdirectory as a **link + one-line
purpose**, grouped under sections when useful; subdirectories link to their own `index.md`.
(The project's other docs shards — e.g. `steering/` — follow the same convention.)

- **Root `pages/index.md` = the full typed map.** Every page, with its link, route, **kind**
  (main / secondary / complementary), **access**, and **status**. Group by category or segment
  as the product suggests. Below the map, cross-page decision sections — **Exclusions,
  Redirects, Splits, States, Open decisions** — appear *only when non-empty* (§5).
- **A nested `index.md` = the local map** of that segment's files and sub-shards, in the same
  link+purpose form; it may carry local notes (a segment's shared states, its role surfaces).
- **An index is a map, never content.** No page specs, no sketches, no canon text inside an
  index. One owner per fact: the page file owns its spec; the root index owns classification and
  cross-page decisions. The tree is the registry — indexes link and describe, never a second
  source of page content.

Root map entry shape (a guideline, not a forced table):

```markdown
## Main
- [Dashboard](dashboard.md) — `/dashboard` · main · private · confirmed — the member's home; own work at a glance
## Secondary
- [Disclaimer](disclaimer.md) — `/disclaimer` · secondary · public · confirmed — investment risk warnings
## Complementary
- [Payment success](payments/success.md) — `/payments/success` · complementary · private · confirmed · family: transaction-success — receipt after a settled order
```

## 3. The page file — guidance, not enforcement

A page file is **guidance, not a form**. The agent writes what fulfils the project's
requirements — as little or as much as the page needs. The default aim is a simple, readable
spec anyone can imagine the page from; but brevity is not enforced and richness is not
forbidden. A one-component page may be a few lines; a complex page may describe its surrounding
machinery, its decomposition, and an illustrative layout. Nothing here is mandatory boilerplate,
and nothing caps what the agent may express when the project calls for it.

**Frontmatter (the core fields):**

```yaml
---
name: Disclaimer          # the page's name on the web
url: /disclaimer          # its route
access: public            # public | protected | private
---
```

| access | means |
|---|---|
| `public` | no gate — anyone can open it |
| `private` | sign-in required, no special role — the signed-in user's own space (profile, settings, my dashboard); a user sees their own data, never another's |
| `protected` | sign-in **plus a privilege/role gate** — admin, staff, a verified-investor area |

These three are the core; add frontmatter fields when the project needs them.

**Body:** a description of what the page is for, then a sketch of how it looks **from inside** —
its internal composition, not its visual UI. The sketch may be as light or as full as the page
requires: the main building block(s) and the data/labels that identify them, and — when useful —
what surrounds them.

```markdown
Essential investment disclaimers and risk warnings for platform users — a read-only
legal document reached from the footer.

## Inside

    LegalDocumentPage          # one component renders this page (single unit)
      path        = <the page route>
      breadcrumb  = <localized document name>
      title       = <localized title, via its i18n key>
      document    = <the legal content, via its document key>
      sections    = <the document's sections>
```

**How to express it (guidance, not a rigid form):**

- Picture the page's **composition** — its building block(s), and whether it is a **single unit**
  (one component renders the page, as above) or **multi** (assembled from children — show them).
  Describe content and surrounding concerns as the project needs; don't stop at a vague feature
  list, and don't pad a simple page to look thorough.
- Every value is a **descriptive placeholder** (`<localized title>`, `<fund summaries: name,
  type, risk, return>`), never a hard-coded literal. Prop/field names are descriptive labels,
  not a real component's API (`title`, `funds` — not `titleKey="funds.index.title"`).
- Notation is **flexible and language-neutral** [/polyglot] — an outline, a tree, a
  pseudo-structure, whatever pictures the page clearly. Never JSX, and never any one framework's
  syntax as the archetype.
- The examples here are **one rendering of the shape, not templates to copy**.

**What the sketch may cover** (all opt-in — write what fulfils the requirements):

- **Surrounding functions** — SEO metadata generation (title, description, canonical, OG,
  hreflang); AEO / answer-engine content (server-rendered, crawler-readable without JS); data
  fetchers; guards (e.g. a country/lang mismatch → 404); rendering strategy (blocking vs
  prerendered, suspense boundaries, server-static vs client-interactive layers).
- **The slim-page decomposition** — the page layer stays thin while its content is decomposed
  across child components/files; show that composition.
- **States, CTAs, exits, redirects, data sources, the complementary anatomy fields** — when the
  page genuinely needs them or the user asks.
- **An illustrative layout** — a possible arrangement/decomposition, always under this banner:

  > CAUTION — ILLUSTRATIVE GUIDANCE ONLY. NOT CANON. NOT TIED TO ACTUAL CODE.

  It pictures one way the page might be built; it prescribes nothing, and no component, prop,
  or file name in it is a fact about the real implementation.

A richer page, illustratively (descriptive placeholders, neutral notation):

```markdown
One fund's details — performance, facts and trading info for a signed-in investor, reached
from the funds list; the URL carries the market country and the fund slug.

## Inside

    Fund details page        # slim orchestrator; content decomposed across files (multi)
      rendering = <blocking: request-time cookies + live data; body behind a suspense boundary>
      guards    = <URL country must match the fund's country, else 404; lang defaults to ar>
      data      = <server: fund by slug · performance summary · trading info · markets · translations>
      seo       = <metadata generator: title/description/canonical/OG/hreflang from fund + market + lang>
      aeo       = <server-rendered crawler-readable article + performance; HTML first, no JS>
      content   = <decomposed children:>
        ├─ SEO article        (server-static, visually hidden)
        ├─ performance static (server-static, visually hidden)
        ├─ content static     (server: fund facts, prospectus label, country name)
        └─ details client     (interactive; seeded with performance + trading data)

    CAUTION — ILLUSTRATIVE GUIDANCE ONLY. NOT CANON. NOT TIED TO ACTUAL CODE.
```

## 4. Kinds and status — the map's vocabulary

- **Kind** (what the page is): `main` / `secondary` / `complementary`. The boundary test is
  owned by `../complementary/references/boundary-test.md`; the root index carries each page's
  kind. Kind is a map fact, not forced into page frontmatter.
- **Status** (how settled): `confirmed` (openable evidence) / `inferred` (domain logic) /
  `uncertain` (an Open decision) / `excluded(reason)`. The root index map carries status for
  pages that exist; evidence and reasons are recorded leanly — a note on the map entry, or the
  decision sections. An `excluded(reason)` page has **no file and no map row** — it lives only
  in the Exclusions section (§5), so the fact has one owner.
- A complementary page's **family** (one of the nine) is noted on its map entry; its anatomy is
  the mode's design contract (`../complementary/references/anatomy.md`), recorded in the page
  file at the depth the page needs.

## 5. Decision records — reasons survive the tree

The tree is valuable because of its **reasons**, not its files.
`../main/references/decision-recording.md` owns the record anatomy, reason quality, evidence
hierarchy, and supersession — this section only places them.

- **Exclusions** (every kind): a root-index section — the page/route considered, its kind, the
  decision (`excluded`/`deferred`/`redirect`/`state`/`owned-elsewhere`), the specific reason,
  its source, and a revisit trigger. An unrecorded "no" is re-invented by the next agent.
- **Redirects / Splits**: root-index sections when they exist — from/to/type/reason/what the
  user sees; was/became/tests/date. A redirect may instead be a page file whose sketch shows the
  handoff — the user's call; the decision is recorded either way.
- **States** that are not routes: a root-index section (shared states) or depth inside the
  owning page — planned, not implied, so blank screens do not ship.
- **Open decisions**: a root-index section — decision, options, owner, needed-by. Nothing stays
  `uncertain` without one.
- Omit any section that has no rows. Counts are computed from the tree, never estimated.

## 6. Migration — an old monolith into the tree

A project may carry the previous single-file map (`PAGES.md`, `PAGE-MAP.md`, or
`COMPLEMENTARY-MAP.md`). Migration is mechanical where the route is clear, and a question where
it is not:

1. **Read the monolith** and list its rows: route, kind, status, evidence, notes; plus its
   exclusions, redirects, splits, states, and open decisions.
2. **Place each page by its route**: static → `<page>.md`; a segment root → `<segment>/_.md`; a
   dynamic route → `[param].md`; nested routes → nested directories. Create the directories the
   routes imply.
3. **Write each page file** (§3): frontmatter from the row (name, url, access — ask when access
   is unstated), a purpose description from its notes, a sketch at the depth the row or the
   project's code suggests. Carry the row's depth where it exists; write more where the
   requirements call for it.
4. **Carry the decisions into the root index**: the typed map (kind, status, evidence notes)
   plus the Exclusions/Redirects/Splits/States/Open-decisions sections, reasons intact.
5. **Build shard indexes bottom-up**, the root index last.
6. **Ask on ambiguity, in one round**: a row whose route is unclear, a modal/state entry that is
   not a route, a conflict between the monolith and the code. Never guess a route.
7. **Reconcile and retire**: old rows = page files + exclusions (counts match), links resolve;
   then remove the monolith in the same change, with the user's confirmation — the tree now
   carries everything it said.

## 7. Downstream contract

| Consumer | Reads | Expects |
|---|---|---|
| `prototype` | page files + root index | one page per confirmed route; states as variants; conditional pages built per their anatomy |
| `impeccable` / design | root index map + role notes | the screen set and role surfaces |
| `planner` | root index + splits/exclusions | work breakdown that respects the map |
| `seo` | secondary canons + root index | canon routes, sitemap completeness |
| `collection` | the page list from the tree/index | a BOM per page; never invents pages |
| implementation | the whole tree | no pages outside the map; a conditional page with no file stops and registers first |

**Same-change duty.** A page added, removed, or renamed in code updates its file *and* the
indexes in the same change. A page that exists only in code is a map defect; a file no index
lists is a phantom. When a downstream skill needs a page the tree lacks, it adds the file and
the index entry first, then builds.

## Writing rules

- One file per page; two routes never share a file.
- Indexes link and describe — never duplicate page content or canon text.
- No empty sections, no placeholder headings; omit what has no rows.
- Dates are real (the session date); links resolve at write time.
- The tree is not a **visual** design doc: no colours, spacing, or pixel layouts — those belong
  to `prototype`, `impeccable`, or the design system. An illustrative **structural** layout or
  decomposition is welcome in the sketch, marked not-canon (§3).
- Page files are guidance, not a form: write what fulfils the project's requirements — neither
  brevity nor richness is enforced (§3).