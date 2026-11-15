# Capability Matrix — Worked Examples

These illustrate the *method* in `references/capability-matrix.md` and the evidence discipline in `references/evidence.md`: splitting a product's modes into separate candidate rows, deriving binary yes/no questions from the requirements, and letting real-world proof overturn a negative capability claim.

**Illustrative only.** The named tools and cells below show the shape of the reasoning. They are **not asserted as current fact** — verify every cell fresh against the candidate's latest stable version (`evidence.md` Part 1) before reusing any of it, and find and cite the actual real-world project yourself (`evidence.md` Part 2) rather than trusting the placeholder citations here. The version pins are left as `[pin fresh]` on purpose: a real run fills them with the version, date, and source it actually checked.

## Case 1 — One brand, three candidates: the variation split

The project needs a backend that (a) lets a client read/write rows directly with per-row permissions, no custom backend in between, **and** (b) allows raw SQL / joins / an ORM / extensions when the data model grows. A topic search surfaces "Appwrite" and "Supabase." Treating each brand as one row hides the decision, because Appwrite ships two materially different modes with *opposite* answers. Split them:

| Candidate (product — mode) | Client-direct access + row permissions | Raw SQL / joins / ORM / extensions |
|---|---|---|
| Appwrite — TablesDB | ✅ yes — SDK, realtime, triggers, transactions, atomic ops `[pin fresh]` | ❌ no — SDK Query helpers only `[pin fresh]` |
| Appwrite — native Postgres | ❌ no — needs your backend in between `[pin fresh]` | ✅ yes — full SQL via an ORM such as Drizzle `[pin fresh]` |
| Supabase — Postgres | ✅ yes — PostgREST + row-level security `[pin fresh]` | ✅ yes — full SQL in Edge Functions / via an ORM `[pin fresh]` |

**How to read it.** The two requirements are both must-haves, so they are gates. The Appwrite rows each fail one gate: TablesDB gives client-direct access but no raw SQL; native Postgres gives raw SQL but no client-direct access. Only the Supabase row passes both. The decision falls out of the matrix — but *only because the modes were split*. Collapsed to one "Appwrite" row, the answer would have been a mushy "sort of, depends," and the real trade-off (you can have one or the other, not both) would have been invisible.

**The lesson.** A product name is the surface; the mode is the mechanism. When a configuration flips a yes/no answer, it is a separate candidate. Name rows `[product] — [mode]`, never bare `[product]` when the modes differ. (Cells above are illustrative; confirm the current Appwrite/Supabase architectures and versions fresh — they change.)

## Case 2 — Real-world proof overturns a "no"

The agent is comparing lightweight backends and starts to write: *"PocketBase's relationships are awkward; you cannot really do joins, so it is a poor fit for relational data."* That is a negative capability claim inferred from the API's shape — and it is about to eliminate a candidate. Before it is allowed to, `evidence.md` Part 2 requires a real-world-proof search.

**The search.** Query the capability plus the candidate plus proof terms — for example "PocketBase relational data example", "PocketBase YouTube clone", "built with PocketBase", "PocketBase joins in production". The search surfaces a real application: a YouTube-clone built on PocketBase that models videos, channels, comments, and likes with relations and queries them in production. (Find and cite the actual repository or write-up fresh; do not reuse this description as a verified citation.)

**The corrected claim.**

> Before: "PocketBase's relationships are awkward; you cannot really do joins."
> After: "Possible — a real YouTube-clone application on PocketBase `[version, pin fresh]` models and queries relational data in production `[cite the actual project]`. The mechanism is `[how it expresses relations and queries]`, and the cost is `[what is harder than in a full SQL engine — e.g. no arbitrary multi-table JOIN syntax, so some queries are composed differently]`. Verified against `[version]`, `[date]`, `[source]`."

The candidate stays alive. The honest finding is no longer "cannot" but "can, proven, with this specific cost" — which the user can weigh against a full SQL engine instead of having the option silently removed.

**Two checks still apply.** The proof is version-pinned (a clone on an old release proves the capability class exists; confirm the current release behaves the same). And "a real app does it" is not "it is easy" — the mechanism cost is recorded, not hidden. If the search had found *nothing*, the cell would read "no production example found" (unproven), not a hard "impossible."

## Case 3 — The split generalizes beyond backends

The same method applies in any ecosystem where one product offers decision-relevant modes. Illustrative shape (verify fresh):

| Candidate (product — mode) | Public pages indexable by search engines (SEO) |
|---|---|
| `[UI framework]` — client-rendered SPA | ❌ no — content renders after load; needs an added SSR/SSG layer `[pin fresh]` |
| `[UI framework]` — server-rendered / static | ✅ yes — HTML ships pre-rendered `[pin fresh]` |

A project whose hard requirement is search-engine visibility gates on this column; the client-rendered mode fails it unless an extra layer is added (a qualified yes with a cost), while the server-rendered mode passes. One brand, two candidates, opposite answers — exactly the pattern the split exists to expose.

## How to use these

Treat these as demonstrations of the method, not a lookup table. For the actual decision: derive the columns from *this* project's requirements, discover the candidates and their modes by topic search, pin every cell to the latest stable version, run the real-world-proof check on every disqualifying "no", and lead with the decision the matrix supports. The specific tools and answers here will go stale; the discipline does not.