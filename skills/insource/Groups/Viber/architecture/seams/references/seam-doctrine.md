# Seam Doctrine — date the third party, don't marry it

> The seam concept is Michael Feathers' (*Working Effectively with Legacy Code*); the aphorism it
> serves — **"don't marry the framework, date it"** — is the one Uncle Bob made famous. This file is
> the pillar's spine: every other file enforces or extends what is stated here.

## 1. The one idea

Every external capability your code consumes — a library function, a framework primitive, a vendor
type, a platform driver — must pass through a **seam you own**. The consumer knows the seam's name,
never the thing behind it.

```ts
// ❌ married — the vendor is now part of every file that imports it
import { debounce } from "@xxx/debounce"

// ✅ dated — consumers import the project's own named export;
// the vendor lives behind one seam and can be swapped there alone
export { useDebounce } from "@/core/debounce"   // project-owned name, project-owned contract
```

```csharp
// C# — the same seam in a compiled house
// Core/Debouncer.cs
public interface IDebouncer { IObservable<string> Watch(IObservable<string> source, TimeSpan delay); }
// consumers inject IDebouncer; the timer vendor lives in the single registered implementation
```

Same doctrine, opposite worlds: in the script the seam is a module export; in the compiled app it is
an interface with one registered implementation. **The seam is the contract location, not a syntax.**
Where the contract lives in your stack — a file, an interface, a barrel module, a DI registration —
is what the placement step decides.

**And it applies wherever knowledge lives — not just in UI.** A seam is a way of *placing a boundary*,
so it exists in every part of the system, backend logic first: [payment-gateway adapter], [mail/SMS
provider], [the driver behind a repository interface], [a clock or randomness source standing between
a worker and `Date.now()`], [a feature-flag evaluation SDK], [a queue client], [an LLM behind one
`complete(prompt)` contract]. The rule never changes with the layer: name by purpose, seal the vendor
knowledge in one place, swap in one file. The UI ladder in §3 is the most *visible* instance of the
doctrine, not its subject — and the guard is part of the idea: where there is no external thing behind
the boundary, what you have is ordinary layering, and a seam without a third party is decoration.

## 2. Two shapes, not conflated

Seams come in two shapes, and conflating them muddles both:

- **Utility seams** name a capability you own: `useDebounce` hiding a vendor debounce.
- **Usability seams** are the rings that cover the join between such a capability and the functions
  you want it applied to — the ladder in §3.

Everything else in this pillar serves both shapes.

## 3. The composition ladder — usability seams

Capabilities are added by **stacking rings, not by editing inner ones**. Each ring is one usability
seam with one responsibility: it knows the rung below it and applies one thing on top of it. The
schema is a naming-and-knowledge pattern, not a widget pattern — every stack instantiates it:

```text
   <bare primitive>   →   <Skin>          →   <Semantics>      →   <Behavior·Semantics·Skin>
    raw platform          project              our problem        the rung that applies
    or vendor name        vocabulary +         domain job         one capability
                          first obligation
```

Illustrative instances — examples to reason from, not a closed set; an unlisted or hybrid family
always counts:

- **[UI components]** `<input>` → `<Input>` (tokens, a11y) → `<SearchInput>` (search semantics:
  icon, clear) → `<DebouncedSearchInput>` (applies the `useDebounce` utility at this rung)
- **[data/store, e.g. Go]** `*sql.DB` → `store.Repository` (tx + error translation at the boundary)
  → `store.OrderRepository` (order semantics) → `store.CachedOrderRepository` (applies the caching
  utility)
- **[service client, e.g. C#]** raw `HttpClient` → `ApiClient` (their JSON becomes our records) →
  `OrdersClient` (endpoint semantics) → `ResilientOrdersClient` (applies retry/circuit-breaker)
- **[handler chain, e.g. Python/Elixir middleware]** `handler` → `authenticated(handler)` →
  `validated(handler)` → `rate_limited(validated_handler)`

Worked out end to end for the backend worlds: `../examples/case-04-payment-gateway-backend.md`,
`../examples/case-05-api-client-ladder.md`, `../examples/case-06-feature-flags-both-halves.md`.

The utility usually attaches at the outermost rung: that is the common shape, not a rule. Any ring
whose honest job includes the capability may own it, and a mid-rung is legitimate when every rung
above should inherit the behavior for free.

In every instance the **name spells the ladder path** — the base noun is the inner rung and each
added word is one outer application, in whichever direction the language composes (prefix in
`DebouncedSearchInput`, suffix in `CachedOrderRepository`). A rung whose honest name needs "and"
is two rungs welded together.

Three invariants the ladder must keep, in every world:

1. Nothing in an inner ring knows an outer ring exists.
2. Remove the outermost and everything below still stands.
3. Add one and nothing below changes.

This is the same discipline hexagonal and ports-and-adapters authors state for whole systems; the
ladder states it per component, one ring at a time.

## 4. Seam taxonomy

| Kind | What it separates | Example |
| --- | --- | --- |
| **Utility seam** | A single capability, exported under a project-owned purpose name | `useDebounce` hiding a vendor debounce |
| **Usability seam** | The join where a utility is applied to a function — one ring of a ladder | `DebouncedSearchInput` over `SearchInput`; `CachedOrderRepository` over `OrderRepository` |
| **Framework seam** | Your domain from the host framework's own primitives | a project-named memo/cache contract over the framework's scheduler; a View Barrel over platform widgets |
| **Vendor seam** | Your system from a third-party library or service | an adapter around an editor/terminal/chart widget |
| **Contract seam** | Your types from theirs — vendor types never cross the boundary | your `SearchResult`, never the client's generated response type |

The taxonomy is how you classify what you already have. DDD names the framework/vendor rows
**anti-corruption layers**; the contract row is the boundary translation those layers owe. The
vocabulary differs; the obligations here are the same and the swap test (§6) is the shared proof.

## 5. Rules of ownership

1. **Name by purpose, never by implementation — each shape by its own kind of purpose.** The utility
   is `useDebounce`, not `useLodashDebounce` (purpose = the capability). The ring is
   `DebouncedSearchInput`, not `LodashSearchInput`, and `CachedOrderRepository`, never
   `RedisOrderRepository` (purpose = the job the rung does). The name is the promise; the vendor must
   never appear in public vocabulary, utility name or ring name alike. The
   full naming law, including where the vendor's name may appear at all, is
   [the-two-walls.md](./the-two-walls.md) §0.
2. **Exactly one seam per capability.** Two seams for one capability means two places a replacement
   has to happen, which means it never happens.
3. **Vendor knowledge is sealed.** Setup, teardown, theming, event shapes — all of it stays inside
   the seam file. A consumer reading only the seam's signature could not guess which library answers
   it.
4. **Types are seams too.** The moment a vendor's type appears in a consumer's code, the vendor is
   married. Convert at the boundary.
5. **Swap must be a one-file edit.** Replacing the implementation — a better library, a native
   feature, a test double — touches the seam and nothing else. If a swap ripples, the seam was leaky;
   fix the seam, not the count of ripples.
6. **Rings compose; they don't reach.** An outer ring configures an inner one only through the inner
   one's published props — never by poking its internals or hoisting its state upward.
7. **Every seam is dated.** Pin what hides behind it, and write the seam so the pin can be dropped:
   the day the host framework ships the capability natively, the seam's body changes and its
   consumers don't.

The boundary cuts **both ways**: a seam file importing upward — from a page, a store, a feature —
turns "put it in the seam" into the way around every other rule. One rule per direction, per
[the-two-walls.md](./the-two-walls.md) §0.

## 6. Why it pays, and the test that proves it

- **Replaceability** — the whole point: the external thing is an ingredient, not architecture.
- **Testability** — a seam is the natural place to stand a fake; no consumer needs a real vendor to
  be tested. (The `testing` pillar calls this a determinism seam; this pillar says where it lives.)
- **Upgrade blast radius** — breaking vendor changes land in one file with one name.
- **Naming honesty** — the codebase's vocabulary describes what your product does, never what you
  installed.

**The test of a seam:** ask of any boundary in the codebase — *if the thing behind this disappeared
tomorrow, how many files would edit?* One file: it's a seam. More: it never was. The walls
([the-two-walls.md](./the-two-walls.md)) keep the claim true mechanically;
[the swap-test sweep in the spec](../specs/vendor-seal-audit-spec.md) is how a whole tree is graded
against §5.
