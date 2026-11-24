# Case 05 — the ladder on a client, no components anywhere

*Names and numbers are illustrative. This case exists to prove §3's schema on a backend object: the
rungs are not widgets — they are one-responsibility wrappers around a capability, and the name spells
the path here too.*

## The ladder

A market-data REST API consumed by a portfolio engine. The schema, instantiated:

```text
bare primitive      skin                  semantics           behavior applied
raw HTTP fetch  →   ApiClient   (contract  OrdersClient  (job  CachedOrdersClient
                      boundary, our types)   named here)        (caching utility at rung 4)
```

Four rings, four responsibilities, one knowledge direction each:

| Rung | Owns | May know | Must never be seen by |
| --- | --- | --- | --- |
| `fetch` / `req` / `HttpClient` | nothing — the platform primitive | (vendor SDK, if one exists, ends at rung 2) | rungs 3–4's consumers |
| `ApiClient` | auth headers, base URL, JSON→**our** types, error translation | the vendor's response shapes | the domain |
| `MarketDataClient` | endpoint semantics: `quotes(symbol, range)`, pagination as "give me the window" | `ApiClient`'s contract | cache/rate-limit callers' internals |
| `CachedMarketDataClient` | applies the caching utility at this rung | `MarketDataClient` only | everything below — it edits nothing |

```ts
// market/apiClient.ts → market/client.ts → market/cachedClient.ts
export interface MarketDataClient { quotes(s: Symbol, r: Range): Promise<Quote[]> }
export const cachedMarketData: MarketDataClient = withTtlCache(rawMarketData, { ttl: 15_000 });
```

```go
// market/api.go → market/orders.go → market/cached.go
type QuotesProvider interface { Quotes(ctx context.Context, s Symbol, r Range) ([]Quote, error) }
func Cached(inner QuotesProvider, ttl time.Duration) QuotesProvider { /* new object; inner untouched */ }
```

```csharp
// market/ApiClient.cs → market/MarketDataClient.cs
services.AddMarketData();                 // composition root: IQuotesProvider -> Cached(MarketData(...))
// the DI line is the pin — rung 4 added without editing rung 3, per the ladder's third invariant.
```

## The invariants, tested on the backend version

- **Remove the outermost:** delete `CachedMarketDataClient` — engine runs, slower, correct. Nothing below changed. ✓
- **Add one:** the day rate-limiting lands, it becomes `RateLimited·Cached·MarketDataClient` (or the
  client's own mid-rung if every consumer must inherit quota safety — the doctrine's *common shape,
  not a rule*, tested by asking who should inherit for free). Rungs below: untouched in the diff. ✓
- **Upward blindness:** `MarketDataClient`'s tests import nothing from the cached layer; a grep for
  the cached name inside `market/client.*` matches zero files. ✓

## The sibling-behavior shape, honestly marked unresolved

The same question the doctrine flags for UI inputs lands here: caching *and* retrying *and* quota —
one ladder with attach-order chosen by who-must-inherit-for-free, or a provider-per-combination? The
doctrine does not decide; a real project picking one **is an open decision row in the seams document,
with a reason** — not a silent default. (See `../references/seam-doctrine.md` — the naming-path rule
narrows the options, it does not close them.)

## The general form

Anywhere a capability composes onto a function, the ladder works: [repository + cache], [validator
pipeline], [notifier + dedupe], [an LLM client + token budget]. The audit question is always "what
did I edit to add a rung?" — and the honest answer must be exactly one new file plus one line at the
composition point.
