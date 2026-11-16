---
name: pages
version: 2.0.1
specialized: none
description: 'A product''s complete page universe: one skill, three modes, one route tree. /pages main plans the core-screen inventory, pruning a 492-row 30-discipline catalog against evidence, splitting mixed concerns, recording redirects/exclusions with reasons. /pages secondary writes the trust documents (ToS, Privacy, Cookies, Contact, Status, DPA, delete-account; scale/phase-gated, one canon each, never invented legal facts). /pages complementary designs the conditional screens that fire only on a trigger, the app fine without them (onboarding, transaction outcomes, HTTP errors, session/access gates, maintenance, token handoffs, relays). Every page is one lean file in a <docs>/pages/ route tree (path = route, _.md root, [param].md dynamic), a shard index.md per directory; kind/access/decisions on the map; nothing a product lacks gets invented. Triggers: plan my pages, legal pages, onboarding flow, error page, callback URL. Not for designing/building screens (prototype, impeccable) or implementation order (planner).'
when_to_use: Any question of which pages a product has, needs, or must not have — core inventory, trust documents, conditional screens — or when a change touches the <docs>/pages/ tree.
argument-hint: "[main|secondary|complementary] [plan|list|new <x>|audit]"
---

# pages — one inventory, three kinds of page, one route tree

A product's pages fall into exactly three kinds, and the old three skills are now one:

| kind | exists when | mode | method |
|---|---|---|---|
| **main** | navigable at any time by anyone with the right to it — the core flow | `/pages main` | `main/method.md` |
| **secondary** | trust/legal/support documents off the primary flow — once written always reachable; which exist is scale- and phase-gated | `/pages secondary` | `secondary/method.md` |
| **complementary** | only when a trigger fires; the app operates normally without it | `/pages complementary` | `complementary/method.md` |

The kind boundary is defined once — in `complementary/references/boundary-test.md` (the three
questions that separate signup [main] from a payment-success screen [complementary] from the
ToS [secondary]) — and every entry in the **root index map** carries its kind tag. Adding any
page to the project means adding its file under `<docs>/pages/` and its index entry in the same
change; the format is owned by `references/pages-tree-format.md` and nothing else restates it.

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
- **One owner per fact.** A page lives once in the tree (one file per page); the shard indexes
  map it; document content canon lives in one place; the catalog row does not restate the
  method, the method does not restate the catalog.
- **The artifact is a tree, not chat.** `<docs>/pages/` (the docs location the project uses) is
  the contract every downstream skill (`prototype`, `planner`, `impeccable`, `seo`,
  `collection`) reads and must update in the same change it adds or removes a page.

## Routing — load only the mode you are in

| the task is | load |
|---|---|
| planning/auditing the core screen set, splits, redirects | `main/method.md`, then its `references/` per its steps |
| drafting any trust document (ToS, privacy, contact, status…) | `secondary/method.md`, then `secondary/references/<type>.md` |
| deciding/designing a conditional screen, callback relay, gate | `complementary/method.md`, then its family reference |
| writing or updating the artifact itself | `references/pages-tree-format.md` (the only schema owner) |
| asking where a page's content canon lives and how it gets built | `references/output-contract.md` (the only output story — one file, one canon, one build; type and family docs never own one) |

## Layout

```
pages/
├── SKILL.md                        # this map: kinds, shared laws, routing
├── references/pages-tree-format.md # the pages tree schema: route tree, shard indexes, page files (single owner)
├── references/output-contract.md   # the one output story: register → canon → build (single owner)
├── main/          method.md + references/ (data.csv catalog, patterns, splits,
│                  decision-recording, sources) + research/
├── secondary/     method.md + references/ (catalog + one doc per page type +
│                  presentation + engineering)
└── complementary/ method.md + references/ (boundary-test, catalog, anatomy,
                   nine family docs) + examples/after-payment/
```

Modes are self-contained: no file in one mode restates a law from another; the only shared
surface is this SKILL.md and the format reference. Mode commands keep their old skills'
workflows — `/pages main plan` is what `main-pages` did; `/pages secondary new <type>` is
`secondary-pages`; `/pages complementary audit <routes>` is the conditional-family pass.