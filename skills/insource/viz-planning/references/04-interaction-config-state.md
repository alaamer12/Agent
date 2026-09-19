# Filtering, State, and Configuration

Covers: filtering architecture, visualization state and storage, visualization configuration and precedence.

These are **global** decisions — architecture choices made once for the whole system, not per chart.

---

## Filtering

If the visualization supports filtering, decide where the filter state actually lives — this is an architecture decision, not just a UI detail.

**Recommended default: query parameters are the canonical representation of filter state; UI filter components are a secondary interface for editing those parameters** — not the other way around.

```
User → Filter component → Query parameters → Visualization
```

rather than keeping filters only in hidden in-memory frontend state. E.g.:

```
/dashboard?model=gemini&benchmark=deepswe&month=2026-09
```

This buys, essentially for free: shareable URLs, bookmarkable views, reproducible states, working browser back/forward, easier debugging, and easier external integration (someone can link directly into a specific filtered view). The UI filter widget then becomes "a nice way to edit the URL," not the source of truth itself.

Also decide:
- Which filters are mandatory vs. optional?
- Can filters combine (AND/OR), and is that combination itself part of the URL state?
- Can the user clear/reset filters back to a known default?
- Do different charts on the same dashboard have independent filters, or does one global filter control the whole dashboard?

## Visualization state and storage

Distinguish two different layers of "what should persist":

- **URL state** — shareable, reproducible visualization state (filters, focused entity, grouping interval, selected chart type). If someone else opens this URL, they should see the same view.
- **Local persistent state** — personal UI preferences that shouldn't leak into a shared link (theme, panel collapsed/expanded, chart ordering the user personally prefers).

The failure mode to design against: dumping everything into local storage (or nowhere, i.e. losing it on refresh) when some of it is actually part of the shareable visualization state and belongs in the URL instead. When in doubt: if two different people opening the same link should reasonably see the same thing, it belongs in the URL. If it's a personal convenience setting, local storage is fine.

## Configuration and precedence

Configuration for the visualizer itself can come from several places, roughly in order of "how programmatic" to "how interactive":

1. **Code constants** — simplest, but requires a code change to adjust.
2. **CLI arguments** — good for scripts/automation.
3. **A config file** (YAML/JSON/etc.) — good when configuration is large or reused across runs.
4. **Query parameters** — best for state that should be shareable/reproducible (this overlaps with the filtering section above).
5. **Interactive UI controls** — best for end-users adjusting things live.

**If more than one of these mechanisms exists, define the precedence order explicitly — don't let it be discovered by accident later.** A reasonable default ordering, most-general to most-specific:

```
Code defaults → Config file → CLI arguments → Query parameters → Interactive UI state
```

Concretely: if a config file says `group_to: 10` but a CLI flag says `--group-to 5`, which wins? If a URL has `?group_to=3` but local storage remembers `group_to=5` from last time, which wins? Both need a defined answer before either mechanism ships — pick a hierarchy (the one above is a reasonable default) and document it in the project's design doc rather than letting whichever code path happens to run last decide it implicitly.
