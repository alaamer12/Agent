# The discovery walk

Stories are not invented; they are found. A system already contains every door it can be entered through -
the walk lists them, then each door becomes a candidate story and gets its four facts honestly answered.

## T - timeframe doors: enumerate the clocks

Grep for every time value that *exists in code*, not in your imagination:

- cache TTLs and staleness checks (`TTL=24h`, `isStale()`), session/token expiries, trial windows;
- retry and backoff horizons (when does "trying" become "gave up");
- scheduled events (nightly sync, daily rollup) and their grace periods;
- user-visible ages ("posted 3 days ago" logic), rate-limit windows, cooldowns;
- the system clock itself - a story for when it's wrong is an S story (see below), but a story for clock
  *advance* past each constant is T.

For each constant: **what does the user see in the moment after crossing it?** That moment is the story.
Write both sides for the important ones - crossing (stale banner appears) and not-crossing (fresh cache, no
banner, rows from cache) - the negative story is what stops "helpful" code from firing banners on fresh data.

## U - user doors: enumerate the verbs

Every command is three doors:

- **happy** - intended use, intended order; usually H frequency;
- **abandoned** - the user starts and leaves: force-quit, closes the tab, loses the app mid-flow (the OS
  killing the process under memory pressure is S, the user killing it is U - name which);
- **mistaken/hostile** - double-taps, confirming the wrong thing, input out of contract. Not every command
  needs one; write it where the mistake is *expensive* (delete, overwrite, pay).

Walk the actual screens/commands, not a feature list - a verb that exists in the UI but "nobody uses" is
still a door.

## S - service/platform doors: enumerate the uncontrolled

List everything your code trusts from outside:

- **server endpoints** - for each: the wrong-*kind*-of-success story (200 with a missing field, a stale
  cached copy, a half-migrated shape) is rarer than the 500 and much more missed, because nothing looks
  failed;
- **process/platform lifecycle** - OS watchdog, sleep/hibernate mid-write, low-memory kill, disk full at
  file 3 of 5, permission revoked mid-flow;
- **time and identity** - clock skew vs server time, restored backup on a new device, two devices same
  account;
- **connectivity** - offline at start, dropped at the worst possible moment (mid-commit, not mid-download).

For each: how can it betray us *specifically*? "Server error" is not a story; "checkpoint returns 200 with
`state: null`" is. Apply that same depth to **every claim in the story, not only the causer** - the why,
the when, and the what-you-see get the identical treatment. For platform subjects that means naming the
concrete mechanism with a reference - **"Android terminates the process via low-memory kill under memory
pressure (see `docs/platform/android-lmk.md`)"** - not "the OS killed it", not "the platform reclaimed
resources". The reference carries the mechanism's explanation; the story only cites it
(doc-file, code-file/symbol, spec section, URL - whatever this project already trusts). One causer per
sentence; if a sentence could be Android's LMK *or* iOS's jetsam *or* a package-update restart, they are
two stories with two references, because their promises can differ at the exact interruption instant.

## Frequency: from the world, not the test run

- **H** - on the main road; every active user hits it weekly (happy path, common switch).
- **M** - routine friction: token expiry, offline at least once a month per user.
- **L** - happens to most installs eventually, rarely per user: cache aged out, app killed mid-flow.
- **R** - needs misfortune or malice to arrange: malformed 200, clock skew, hostile double-tap on the
  expensive confirm.

Be honest - frequency decides attention (an H story with a weak end condition is a shipping bug; an R story
is not worthless, it is just allowed a cheaper arrangement). Do not inflate R to H to justify writing it,
and do not drop L stories because "users don't do that" - the ones who do, do it loudly.

## The promise-bar question - expectancy without perfectionism

For each story ask, in this order:

1. *What do we tell the user happens in this moment?* That is the bar. Write it as what will be **seen**
   (banner, label, one-tap redo), not what is internally true.
2. *What might the reader assume we promise that we do not?* Name it as not-promised when the assumption is
   likely ("the promise is honesty, not resume"), short - one clause.
3. *What is the concrete end?* The predicate a machine can check: "banner gone after refresh succeeded",
   "redo completes and backup file verifies", "status repaints on the next valid poll". If you cannot state
   an end, the story isn't scoped - split it or park it as a question to the user.

The end condition is per case, including the meta: an X meta-story ends only when *every door* reaches the
shared end state.

## Meta-stories (X): same run, three doors

Write one when several triggers must land in the same place (interrupted backup: time, user kill, server
500 - same honest partial + one-tap redo). The meta checks the *sameness*; keep the individual door stories
where each also has its own detail to protect. A meta is not a replacement for coverage - it is the seam
test that the coverage didn't drift into three different promises.

## Audit mode - reading an existing suite the accuracy way

Flag every test whose name/string cannot answer: **who or what exactly did this, why, under what condition,
and what is the promise?** Common finds:

- category subjects: "the OS kills it", "the server errors", "network drops" → name the platform and its
  mechanism with a reference, name the endpoint and the exact wrong response, name the drop point
  (mid-commit vs mid-download);
- missing reasons: "the cache becomes stale" *why* - which check, comparing what, after how long? Stated
  once with the mechanism's name + reference, never explained in place;
- actor-less voice: "the session expires", "an error is handled" → who expires it, who handles it;
- feeling-words as expectations: "gracefully", "properly", "safely" → replace with what is *seen* ("shows
  'status unavailable'; never renders the garbage as truth");
- promise inflation: the string says "gracefully recovers" where the code only proves "does not crash" →
  lower the claim to the observed bar;
- story-less tests: assertions present, no story told → they are verification without a promise; write the
  story or merge the test into one.

Propose rewrites (id included), show the map before editing, never renumber history.
