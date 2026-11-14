# Example — Cross-Engine Query Duplication: One Filter Language, Two Storage Engines

**Proves:** the cross-engine query/decision duplication spectrum in `../../../../decision-spectra.md` — that query semantics shared across storage engines are a decision-duplication risk, not "just plumbing."

**Redaction note:** project name, domain, and field names are genericized. The duplication pattern and its fix are preserved exactly.

---

## The situation

Two independent codebases (a server component and a client-side component) both need to answer the same question against their own local storage: "give me everything changed since checkpoint X, matching filter Y." The server runs against one storage engine; the client runs against a different, embedded one. Both need identical results for the same logical query — a record that should match on the server must also match on the client, and vice versa.

## The traditional default

```text
server/src/queries/sinceFilter.ts     ← hand-written for engine A's query syntax
client/src/queries/sinceFilter.ts     ← hand-written for engine B's query syntax
```

Each file is locally reasonable: it correctly implements the delta-pull-plus-filter logic for its own engine, and passes its own tests. "Query code" doesn't read as a business decision the way a pricing rule does, so it doesn't trigger the usual instinct to ask whether it needs a single owner — it looks like plumbing, gets written twice, and each half looks fine in isolation.

## What was built instead

```text
packages/query/
├── filter.ts               ← the query semantics, expressed once, engine-agnostic
├── since.ts                 ← the delta-pull atom, same status
├── engines/engine-a.ts       ← compiles the shared semantics to engine A's syntax
├── engines/engine-b.ts       ← compiles the shared semantics to engine B's syntax
└── (differential tests)      ← same logical query, run against both compiled outputs,
                                  must return the same result set or the build fails
```

The filter and delta-pull logic exist in exactly one place. Each engine gets a thin compiler translating that single definition into its native query syntax, and a differential test is the thing that actually enforces agreement — not code review, not convention, a test that runs the same logical query through both compiled paths and fails the build if the results diverge.

## What would have changed the answer

If there were genuinely only one storage engine for the system's lifetime — not "for now," but architecturally committed to staying that way — this whole layer would be unjustified complexity. Hand-writing the query directly against the one engine, with no compiler and no differential test, would be correct. The layer earns its cost specifically because two engines must agree, indefinitely, on what "the same query" returns.

## What this proves

The failure mode here isn't obviously a failure mode, which is why it's worth an example on its own: duplicated business thresholds get caught by instinct because they look like business logic. Duplicated query semantics don't, because they look like implementation detail — and that's exactly why two independently-correct implementations can drift silently for a long time before anyone notices the server and client disagree about which records match. The fix isn't "write better query code" — it's recognizing that a query two systems must agree on is a decision like any other, and decisions get one ground, protected by a test that would actually catch the drift.
