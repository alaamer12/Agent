# Examples: recognizing concern-mixing — and recognizing when there isn't any

Small, realistic snippets showing the pattern this skill exists to catch: a document that mixes concerns which belong in different homes, described in different words each time it comes up. Each example gives a short **Before** excerpt and an **After statement** — a description of where the content should end up and why, not a full rewritten file. Producing the actual split files is Step 5 of the main workflow, after the user has approved a plan. Examples 7 and 8 are the deliberate exceptions: cases where the right after-statement is "leave it alone" or "don't create this," included because both a long file and an eagerly-produced split are easy to mistake for progress when they aren't.

---

## Example 1: domain concept vs. persistence detail, same paragraph

**Before** (excerpt from a catalog/domain document):

> A catalog video represents a video that MuslimTube has selected for its content catalog. A video is identified primarily by its YouTube video ID. The catalog may contain metadata such as title, description, thumbnail, channel name, channel ID, duration, publication date, and topic assignments. The exact field names and data types are defined in `Catalog Schema.md`.

**What's mixed:** this paragraph is doing two jobs. The first two sentences are a *domain* statement — what a catalog video conceptually *is* and how it's identified. The metadata list, framed with "field names and data types," is drifting toward a *schema/persistence* concern — even though it correctly defers the exact definition elsewhere, listing the fields at all here duplicates (in looser form) what the schema document states precisely.

**After statement:** Keep the domain paragraph in the catalog/domain doc as-is — it's the right home for "what a catalog video is." Drop the metadata field list from this document entirely and replace it with a single link: "see the video entity in `Catalog Schema.md` for the exact fields." The domain doc should describe the *concept*; the schema doc should be the only place that enumerates *fields*. Right now both partially do both.

---

## Example 2: the same concept explained twice, in different vocabulary

**Before** (excerpt A, from a catalog/domain document):

> The primary deduplication key is the YouTube video ID. If the same YouTube video is encountered through multiple acquisition jobs or providers, it should resolve to the same catalog video rather than creating duplicate video entries.

**Before** (excerpt B, from a database/persistence document):

> Each catalog video has an internal MuslimTube identifier and an external YouTube identifier. The `youtubeVideoId` should be unique within the catalog. This allows the system to identify the same YouTube video even when it is discovered multiple times or returned by multiple providers.

**What's mixed:** these are the same rule — "one catalog video per YouTube video ID, regardless of how many times or which provider discovers it" — stated twice, in two files, in different words. Neither excerpt is wrong, and they don't currently contradict each other, but this is exactly the drift risk: if one gets refined later ("unique per (youtubeVideoId, region)", say) and the other doesn't, the two documents now silently disagree.

**After statement:** Pick one home for the *rule* — most naturally the domain/catalog doc, since "why this identity matters" is a domain concern. State it there once. In the database/persistence doc, keep only the *implementation* of that rule (e.g., "`youtubeVideoId` has a unique constraint — see catalog identity rules for why") and link back rather than re-explaining the reasoning. The persistence doc should say *how* the constraint is enforced; it shouldn't re-derive *why* it exists.

---

## Example 3: a diagram repeated with the same meaning, different shape

**Before** (excerpt A):

```text
Catalog
"What does the system store?"
        │
        ▼
Catalog Schema
"What does each entity look like?"
        │
        ▼
Database
"How is it persisted?"
```

**Before** (excerpt B, elsewhere in the same doc set):

```text
Acquisition Layer
       │
       │ Raw external data
       ▼
Orchestrator
       │
       │ Unified representation
       ▼
Catalog
```

**What's mixed:** these aren't literal duplicates — one is about the Catalog → Schema → Database layering, the other about Acquisition → Orchestrator → Catalog. They're a milder version of the same issue: two ASCII diagrams independently trying to convey "here's how the big pieces relate," scattered as asides inside content-specific docs, instead of living together in one place a reader would actually look for "how do the pieces fit together." Diagrams like this are a strong signal that an architecture-level document is missing, and each doc is quietly trying to be that document a little bit at a time.

**After statement:** Consolidate both relationship diagrams (and any others like them) into a single architecture/overview document whose whole job is "how do the major pieces relate." Each content-specific doc keeps only the one or two relationships directly relevant to its own concern (or drops the diagram and links to the architecture doc instead) rather than each re-deriving the full system picture from its own angle.

---

## Example 4: a design rule that belongs with its concept, not bolted on at the end

**Before** (excerpt — a numbered "Design Rules" list appended at the end of a long document):

> 6. Provider-specific schemas should not become database schemas.
> 12. Topic hierarchy is an organizational structure, not a universal theological ontology.
> 17. Feed ranking is separate from catalog storage.

**What's mixed:** these three rules belong to three different concerns (provider independence, topic hierarchy design, and feed/catalog separation), each of which is *also* explained at length earlier in the same document or in a different document entirely. The rules list is a second, compressed restatement of content that already has a proper home — it's duplication wearing the disguise of a "summary."

**After statement:** Don't create a standalone "design rules" catch-all. Each rule belongs directly next to (or inside) the section that already explains its reasoning — "provider independence" stays with the acquisition/provider-boundary discussion, "topic hierarchy" stays with the topic-hierarchy discussion, "feed vs. catalog separation" stays with whichever doc owns that boundary. If a short "principles at a glance" recap is genuinely useful for skimming, it can exist as a few one-line bullets at the top of the *same* document it summarizes — not as a separate list re-deriving content that's explained in full somewhere else.

---

## Example 5: explaining instead of mentioning

**Before** (excerpt — from a document whose stated concern is the technical acquisition pipeline):

> Users follow topics rather than individual creators. Following therefore operates directly against the topic structure of the catalog. When a user follows a set of topics, the personalization layer scores each candidate video by how many of the user's followed topics it matches, then blends that score with recency and a small exploration factor before ranking the final feed.

**What's mixed:** the first two sentences are a fine one-line mention — "following works against topics" is genuinely useful context for a reader of the acquisition doc. But the third sentence isn't a mention anymore; it's a full explanation of the personalization scoring algorithm, which is a different document's concern entirely. The acquisition doc doesn't need the reader to understand *how* personalization scores videos — only that following-by-topic is a thing that exists downstream of what this doc produces.

**After statement:** Cut the acquisition doc's reference down to the one-line mention plus a link: "Users follow topics rather than individual creators — see `Personalization.md` for how followed topics affect ranking." The scoring explanation stays only in `Personalization.md`, at full depth, where it belongs. A useful test while drafting: if a sentence needed to explain *how* something works rather than just *that* it exists, it has crossed from mentioning into explaining, and belongs in that concept's own file instead.

---

## Example 6: a global index that isn't told to maintain itself

**Before** (a `docs/README.md` written once, at the end of a refactor, with no closing instruction):

```markdown
# Docs

- `catalog.md` — the catalog domain model
- `database.md` — persistence layer
- `feed.md` — feed selection and ranking
```

**What's mixed:** nothing is mixed here — this is a reasonable index. The problem is what's missing: nothing tells a future contributor (human or AI) that this file needs to be kept in sync. Six months and four new documents later, this index is stale, and nobody was ever told it was their job to update it. The doc set has quietly reverted to the same problem the refactor was meant to fix — just one level up, at the index instead of the content.

**After statement:** Add an explicit, plainly stated maintenance instruction to the index itself, not just to a separate contributing guide someone might not read: *"You must update this file whenever a document is added, removed, or moved."* The instruction belongs in the file people (and agents) will actually be looking at when they add a doc — not somewhere they'd only find if they already knew to look.

---

## Example 7: a long file that should be left alone

**Before** (structure of a real ~1000-line document, `Table Reference: Normalization and SQL Conventions.md` — shown as its table of contents, not full content):

```markdown
## 1. `schema_migrations`
### Purpose / Functional Dependencies / Normalization Proof / DDL / Column Reference / SQL Conventions Applied / Canonical Queries

## 2. `settings`
### Purpose / Functional Dependencies / Normalization Proof / DDL / Column Reference / SQL Conventions Applied / Canonical Queries

## 3. `categories`
### Purpose / Functional Dependencies / Normalization Proof / DDL / Column Reference / SQL Conventions Applied / Canonical Queries

...(9 more tables, same seven-section shape each)...

## Summary: Normal Form per Table
| Table | 1NF | 2NF | 3NF | BCNF | Notes |
```

**Why this isn't a candidate, even though it's long:** every one of the twelve sections is the exact same fixed template (purpose → functional dependencies → normalization proof → DDL → column reference → conventions applied → canonical queries) applied to a different table. There is exactly one concern here — "the concrete schema reference, table by table" — explained at full, consistent depth for each table. Nothing here is theoretical framing leaking into technical detail, no product context, no repeated-in-different-words explanation of the same idea: each table's normalization proof is genuinely about *that* table, not a restatement of another table's proof. A reader (human or AI) wants exactly this: one place to look up any table using the same mental template every time.

**After statement:** No split. Splitting this into twelve files — one per table — would force a reader comparing two related tables (or scanning the whole schema) to open twelve files instead of scrolling one, for no concern-separation benefit at all; the "concern" of each section is inseparable from the concern of the whole document. If this document keeps growing (new tables added indefinitely) a table of contents with anchor links — which it already has — is the right scaling answer, not fragmentation. The one legitimate question worth asking is narrower: does the *normalization theory* explanation (what 1NF/2NF/3NF/BCNF mean, in general) live here or in a separate primer the reader is assumed to know? If this document assumes that knowledge and only applies it, it's already correctly scoped; if it were to start re-teaching normalization theory from scratch inside each table's proof, *that* would be the mixing to watch for — not the file's length.

---

## Example 8: a split that shouldn't have happened

**Before** (a ~90-line file, `configuration-reference.md`, covering every user-facing setting and its default — one coherent concern, on the shorter side):

> Documents every setting: `poll_interval_seconds`, `max_requests_per_minute`, `theme`, `notification_grouping_enabled`, and seven others. Each gets a short paragraph: default value, effect, and any constraints.

**A plan that over-splits it:**

```
Before:                          Proposed after:
configuration-reference.md       config/
                                  ├── README.md
                                  ├── polling-settings.md      (2 settings, ~10 lines)
                                  ├── notification-settings.md (3 settings, ~15 lines)
                                  ├── display-settings.md      (1 setting, ~5 lines)
                                  └── misc-settings.md         (5 settings, ~25 lines)
```

**What's wrong:** every one of these five new files is internally fine — none of them mixes unrelated concerns, none duplicates another. The problem is upstream of content quality: nothing about this file needed splitting in the first place. Ninety lines describing a flat list of settings is not concern-mixing; it's one concern (configuration) that happens to enumerate several items, the same shape as the table-reference case in Example 7, just shorter. The split didn't fix a real problem — it manufactured four thin files (one of them, `display-settings.md`, is a single setting) and a README whose only job is now pointing at fragments that didn't need to be separate. A reader who wants "what does `theme` default to" now navigates two hops (README → file) instead of one (scroll).

**After statement:** No split. `configuration-reference.md` stays as one file. If it later grows enough that settings genuinely cluster into distinct concerns with their own surrounding explanation (not just a shared prefix in the name), that's the point to reconsider — not now. This is exactly what Check 0 in `templates/self-check-checklist.md` exists to catch before a plan like this reaches the user: for each of the five proposed files, "does this need to exist" fails immediately, because none of them holds a concern the original file didn't already hold perfectly well on its own.

---

## What these examples have in common

None of these are about literal copy-pasted text — a grep for repeated strings would miss all of them. Each positive example (1-6) is:

- The same idea, explained again in different words (Examples 2, 3), or
- Two different levels of abstraction (concept vs. schema, concept vs. rule, or mention vs. explanation) tangled into one passage instead of split by concern (Examples 1, 4, 5), or
- A structural safeguard that was skipped, letting the same drift happen one level up (Example 6)

Examples 7 and 8 are the deliberate counter-cases, and both are about restraint rather than technique: Example 7 is a file that's long for a legitimate reason and should be left exactly as it is; Example 8 is a file that gets split into pieces that are each individually fine, but shouldn't have been created at all, because nothing about the original was actually mixing concerns — it just looked refactor-shaped once it existed.

This is the pattern to actively look for during Step 2 of the main workflow (building the concept map): not "does this text match text I've seen before," and not "is this file long or does it have multiple sections," but "have I already read an explanation of this idea, even if it looked nothing like this on the page" — and, once a split is on the table, whether it's answering a real finding or just producing more files. Once the new structure exists, the same question applies to keeping it from drifting again.
