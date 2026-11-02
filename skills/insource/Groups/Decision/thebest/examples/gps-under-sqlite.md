# Worked example - GPS radius queries under the SQLite constraint

**The question:** "Which method should we use to find stored GPS points within a radius of a query point -
R-tree, bounding-box scan, or geohash - to power 'things near me' on our mobile app?"

**The constraint, stated up front:** the project's database is **SQLite**. That single fact is not a
preference to weigh - it is the frame. Options that require another engine (PostGIS, a MongoDB geo-index)
are eliminated at listing, with the violation named, and shown so the user sees the filter was honest.

## Step 1 - Frame

- Optimize for: low latency per query at the app's scale, running on-device where the only database is
  SQLite. Secondary: no exotic dependencies the mobile build can't easily ship.
- Hard constraint: SQLite, in-app, bundled.
- Success bar: sub-50ms "near me" query at our real data volume, using only what the bundled SQLite supports.

## Step 2 - Discover (all viable ways, families first)

The families, each with members that survive the constraint:

| family | option | how it works | fits SQLite? |
|---|---|---|---|
| scan | **bbox full-scan** | `WHERE lat BETWEEN ? AND ? AND lon BETWEEN ? AND ?`, no index | yes |
| scan+index | **bbox + composite index** | same predicate, `(lat,lon)` index narrows the scan | yes |
| index | **R-tree** | `VIRTUAL TABLE rtree` spatial index, rectangle-intersection query | yes - if the bundled build enables it |
| bucket | **geohash prefix** | store a geohash column, match on its prefix for the covering cells | yes (plain column + index) |
| extension | **SpatiaLite** | full geo layer with `DISTANCE()`/radius queries | **depends** - needs a loadable extension; on-device builds often can't ship it |
| replatform | **PostGIS / Mongo geo** | purpose-built geo engines | **NO** - violates the SQLite constraint; eliminated, shown anyway |

Three workable finalists after the pre-filter (all documented-fact based, no measurement yet): **bbox+index**,
**R-tree**, **geohash prefix**. SpatiaLite is kept only as a research question ("can our mobile SQLite build
load it at all?" - if not, it's out regardless of how good its geo is).

## Step 3 - Sort each criterion to the right evidence

| criterion | evidence kind | tool |
|---|---|---|
| latency at 12k and at 1M points | **measurable** | `benchmark` |
| does R-tree's index actually get used for a radius-as-rectangle query, or does SQLite full-scan anyway? | **behavioral truth** | `learning-test` (run `EXPLAIN QUERY PLAN` against the real table - docs won't tell you this exact case) |
| is `rtree` compiled into our bundled mobile SQLite? is SpatiaLite loadable there? | **documentable fact** | research (context7 / SQLite & platform docs) |
| geohash prefix misses points just outside the cell edge - how bad at our densities? | **measurable** | `benchmark` (accuracy harness) |
| team comfort / maintenance | **fit judgment** | argument; ask only if it could swing the pick |

The **learning-test** step matters here: an R-tree that looks indexed but isn't being used is the failure
mode that a measured benchmark would silently expose as "R-tree isn't faster" and a naive researcher would
miss entirely. Confirm behavior empirically before trusting the number.

## Step 4 - Run (what the evidence actually says, sketch)

- Research: `rtree` virtual tables are in the standard SQLite amalgamation - available on the mobile builds.
  SpatiaLite is a separate extension not bundled by default → **eliminated on the "no exotic dep" bar**,
  reported as dropped-by-fact.
- learning-test: `EXPLAIN QUERY PLAN` confirms the R-tree query uses `SEARCH TABLE rtree USING INDEX
  (area=?)` - the index is genuinely hit. The bbox+plain-index path uses the index only on the leading
  `lat` column; `lon` is still filtered post-scan.
- benchmark (real 12k-row dump from staging, normal mode, 20 iterations):
  - 12k points, 5km radius: bbox-scan 41ms · bbox+index 12ms · **R-tree 3ms** · geohash 6ms
  - 1M points, same query: bbox+index degrades to ~300ms · **R-tree ~9ms** · geohash ~20ms

## Step 5 - Verdict handed to the user (not enacted)

```text
VERDICT: R-tree (sqlite virtual-table) is likely the best fit for us.
Based on:
  - latency: 3ms at our current 12k / 9ms at 1M (benchmark, normal mode, 20 iters) - beats every option,
    and holds as data grows where bbox+index collapses to ~300ms.
  - behavior verified: EXPLAIN QUERY PLAN (learning-test) confirms the rtree index is actually used for
    the radius-as-rectangle query, not a silent full-scan.
  - fits constraints: rtree ships in the bundled SQLite; no external extension (research, SQLite amalgamation).
Confidence: high - the deciding criterion (latency-at-scale) was measured on real staging data and the
            index-usage assumption was verified empirically, not assumed.
Runner-up: geohash prefix - ~2x slower than R-tree and needs edge-case handling for cells straddling the
           radius, but becomes the pick if we later shard across files where a rtree virtual table won't move.
Flips if:  points stay tiny AND bounded (bbox+index is simpler), or the mobile SQLite build is changed to
           strip virtual-table support (then geohash is the only indexed choice).
Untested:  real device CPU (benchmarked on desktop SQLite, not the phone's SQLite) - acceptable because the
           index-usage behavior that decides the win is CPU-independent; flag before shipping.
Dropped:   SpatiaLite - better geo math but needs a loadable extension the on-device build can't ship
           (documented platform fact, so no benchmark was wasted on it). PostGIS/Mongo geo - violate the
           SQLite constraint outright.
```

Handed over here. The user decides whether to adopt R-tree, weigh the untested real-device risk differently,
or reject it for a reason the evidence couldn't measure - and if they choose otherwise, that choice is
recorded, not argued back.

## Why this is a "thebest" run and not just a benchmark

- The SQLite constraint shaped everything *before* any test - the filter is the method, not an afterthought.
- Only the latency criterion was benchmarked; **whether the index even works** was a `learning-test`,
  **whether the build can ship it** was research. Treating all three as "benchmarks" would have measured a
  solution that can't actually be deployed.
- The result is a recommendation with a named flip-condition and an honest untested item - the material a
  *human* decides on. The agent stops there.
