# pages — one inventory, three kinds of page, one artifact

A product's pages fall into exactly three kinds, and the old three skills are now one:

| kind | exists when | mode | method |
|---|---|---|---|
| **main** | navigable at any time by anyone with the right to it — the core flow | `/design pages main` | `main/method.md` |
| **secondary** | always present but off the primary flow — trust/legal/support documents | `/design pages secondary` | `secondary/method.md` |
| **complementary** | only when a trigger fires; the app operates normally without it | `/design pages complementary` | `complementary/method.md` |

The kind boundary is defined once — in `complementary/references/boundary-test.md` (the three
questions that separate signup [main] from a payment-success screen [complementary] from the
ToS [secondary]) — and every entry in **`PAGES.md`** carries its kind tag. Adding any page to
the project means adding its row to `PAGES.md` in the same change; the format is owned by
`references/pages-md-format.md` and nothing else restates it.

## Shared laws (mode methods inherit these — they do not repeat them)

- **Read before asking.** Project evidence (routes, entities, docs, tickets, recorded
  decisions) answers first; a route that exists is a page that exists.
- **One round of questions.** All open items in one message; never drip.
- **Never invent** — not a domain-implausible screen (main), not a fabricated legal fact or
  retention number (secondary), not a conditional page with no real trigger (complementary).
  The candidate catalog ranks possibilities; the project decides.
- **Every exclusion recorded with its reason** and a revisit trigger. An unrecorded "no" is
  re-invented by the next agent.
- **Status vocabulary everywhere:** `confirmed` (evidence) / `inferred` (domain logic) /
  `uncertain` (ask) / `excluded(reason)`. Labels matter: calling a guess confirmed corrupts
  the map.
- **One owner per fact.** Pages are listed once in `PAGES.md`; document content canon lives
  in one place; the catalog row does not restate the method, the method does not restate the
  catalog.
- **The artifact is a file, not chat.** `PAGES.md` at the project root (or the docs location
  the project uses) is the contract every downstream mode or skill (`prototype`, `planner`,
  `impeccable`, `seo`) reads and must update in the same change it adds or removes a page.

## Routing — load only the mode you are in

| the task is | load |
|---|---|
| planning/auditing the core screen set, splits, redirects | `main/method.md`, then its `references/` per its steps |
| drafting any trust document (ToS, privacy, contact, status…) | `secondary/method.md`, then `secondary/references/<type>.md` |
| deciding/designing a conditional screen, callback relay, gate | `complementary/method.md`, then its family reference |
| writing or updating the artifact itself | `references/pages-md-format.md` (the only schema owner) |
| asking where a page's content canon lives and how it gets built | `references/output-contract.md` (the only output story — one row, one canon, one build; type and family docs never own one) |

## Layout

```
pages/
├── method.md                        # this map: kinds, shared laws, routing
├── references/pages-md-format.md   # the unified PAGES.md schema (single owner)
├── references/output-contract.md   # the one output story: register → canon → build (single owner)
├── main/          method.md + references/ (data.csv catalog, patterns, splits,
│                  decision-recording, sources) + research/
├── secondary/     method.md + references/ (catalog + one doc per page type +
│                  presentation + engineering)
└── complementary/ method.md + references/ (boundary-test, catalog, anatomy,
                   nine family docs) + examples/after-payment/
```

Modes are self-contained: no file in one mode restates a law from another; the only shared
surface is this method.md and the format reference. Mode commands keep their workflows —
`/design pages main plan` is what `main-pages` did; `/design pages secondary new <type>` is
`secondary-pages`; `/design pages complementary audit <routes>` is the conditional-family pass.