# The five route families

Families exist so your options are **materially different**. Three routes that all say "call the API
differently" is one route with three spellings. Aim to cover at least two families, and always include
one route that does not depend on the blocked thing at all.

The lists below are illustrative shapes to reason from, not an exhaustive menu; a hybrid or an unlisted
route is a fine answer when the situation calls for it.

---

## 1. Reroute - same thing, another door

The capability exists; the door you tried is not the only one.

Look for: another endpoint or version (`[v1]` vs `[beta]` vs `[internal-but-public]`), another protocol
for the same data (`[REST]` vs `[gRPC]` vs `[GraphQL]` vs `[WebSocket event stream]`), a bulk export or
report instead of per-item reads, a file download (`[CSV]`, `[NDJSON]`, `[RSS/Atom]`, `[sitemap]`), an
outbound channel instead of an inbound one (webhooks, event bridges, email/notifications you then parse),
a connector in the tool you already have (spreadsheet, BI tool, notebook, CLI, IDE plugin, desktop app),
or a different transport of the same content (public page vs the JSON that page fetches).

Concrete sketch - one source, four doors, same value:

```ts
// TypeScript: the SDK path is blocked, but the same record is already public.
const item = await fetchJson(`/api/items?id=${id}`).catch(() => null);
if (!item) {
  const row = exportRows.find(r => r.externalId === id);        // bulk export door
  render(row ?? (await rssEntry(id)) ?? unavailable(id));       // feed door, then honest unknown
}
```

```python
# Python: same object, chosen by availability, not by habit.
def get_item(item_id: str) -> Item | None:
    for fetch in (fetch_api, fetch_from_daily_export, fetch_from_feed):
        if (item := fetch(item_id)) is not None:
            return item
    return None          # unknown stays unknown; no fabricated item
```

```go
// Go: doors ordered by cost, with a shared context and no blocking retry storm.
func (s Source) Item(ctx context.Context, id string) (Item, error) {
	for _, f := range []func(context.Context, string) (Item, error){s.api, s.export, s.feed} {
		if it, err := f(ctx, id); err == nil {
			return it, nil
		}
	}
	return Item{}, ErrNotFound // caller renders "unavailable", not a zero-value guess
}
```

**Reroute wins when:** the provider publishes the same data elsewhere and you only assumed the API was the
source. **Fails when:** the alternative door is the same request with different syntax - then you have not
generated a route, you have retried.

---

## 2. Replace - different component, same job

Swap the blocked thing for another thing that satisfies the same interface.

Look for: an alternative hosted service, an open-source equivalent you run yourself, a commodity library,
a local/on-device model instead of a hosted one, a database or filesystem standing in for a hosted store,
or your own already-present dependency that quietly covers the need (the search index you have can answer
the "suggestions" feature; the queue you have can carry the webhook you wished for).

Replace is the family where research pays most: verify the substitute actually supports the specific
operation, at your volume, with the guarantees you need - not that it is "popular".

**Replace wins when:** the blocked thing is a commodity you are renting out of habit.
**Fails when:** you swap the vendor and inherit the same limitation, or you take on a system you cannot
operate.

---

## 3. Rebuild from the pattern - capture the capability, not the asset

> If a capability is closed but its behavior is observable, study what goes in and what comes out, then
> reproduce the function in your own system.

A recommendation order, a ranking rule, a pricing calculation, a layout algorithm, a file format, a
transitions spec, a moderation heuristic, a legacy system's data layout: all of these are behaviors that
leak their rules through what any ordinary user can see. Characterize the behavior, then implement your
own version of it. This is the most powerful family and the one that most needs discipline -
[`03`](03-pattern-extraction.md) owns the method, and [`04`](04-access-parity.md) owns the line you must
not cross while doing it.

**Wins when:** the behavior is simple enough to approximate, and your version fitted to your product can
even beat the original.
**Fails when:** the behavior is only observable through privileged or protected access - then it is not
observable, and the route is dead.

---

## 4. Reshape - remove the dependency

Change the architecture so the blocked thing is not needed.

Look for: moving logic across the boundary (the browser can't do it, so do it server-side - or the server
can't, so do it locally on the device), adding an adapter so your code speaks a format that *is*
available, precomputing what you wanted fetched live, a sync job or queue that turns a real-time need into
a batch one, denormalizing a value the blocked join would have produced, or dropping the feature's
dependency entirely by changing the UX so the same user need is met another way.

Reshape is where the smartest wins live, because the "impossible" requirement often disappears once the
goal is named correctly ([`01`](01-goal-and-value-extraction.md)).

**Wins when:** the blocked capability is load-bearing only because of how the system was drawn.
**Fails when:** reshaping costs more than the feature is worth, or rewrites work the user already approved.

---

## 5. Reduce - the valuable subset

When the full goal truly cannot be met, ship the part that carries the value and name the cut.

Split the goal into must-have and nice-to-have by asking what the user's user actually loses. Example
options: `[show real data for 3 of 5 sources]` while the other two stay visibly unavailable,
`[rank by recency instead of by learned relevance]`, `[one-time manual import instead of live sync]`,
`[feature behind a "beta: limited" label instead of absent]`.

Reduce is honest only when the cut is stated. Delivering a shadow of the feature while calling it done is
the defect in [`09`](09-reporting-and-anti-patterns.md) called fake success.

---

## Telling a real route from a rephrasing

Two routes are different only if at least one of these changes: the **system** that produces the value,
the **path** the value travels, the **moment** it is produced (live vs precomputed), or the **shape** of
what the user gets. If your three options share all four, you have one option.
