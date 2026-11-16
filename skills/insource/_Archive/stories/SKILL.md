---
name: stories
description: 'Behavior stories for a system application, discovered systematically and written into the verification code itself. One real-world way a system can be entered or broken, told by four facts: cause (T Timeframe / U User / S service-platform / X meta covering all), true frequency (H/M/L/Rare), what the user is PROMISED to see - the promise bar, not ideal behavior, naming what is NOT - and the concrete condition that ends it. Ids [CASE-FREQ-Snumber] like [T-L-S17] head the story string, report-visible via the runner''s own carrier. The accuracy rule: every claim gets who/what exactly, why, under what condition, what is seen - ''Android kills the process via low-memory kill under pressure (see docs/platform.md)'' beats ''the OS terminated it''; name the mechanism, cite the reference, never lecture, never settle for category words. Use: discover what a feature must survive, write story strings, audit tests that state behavior without cause. Not test mechanics (test), not perf (benchmark), not agile ''As a user'' tickets.'
when_to_use: A feature needs its behavior stories discovered, numbered, or written into verification code; a suite exists but its tests don't say who caused what; the user says "write the stories for X", "what can go wrong here - cover it", or mentions story ids. Also /stories.
argument-hint: "[the feature or flow, or 'audit' over existing stories]"
---

# stories - what really happens to this system, told where the code can read it

A system's real life is not its happy path. It is the cache that aged out, the user who force-quits halfway,
the server that answers 200 with a body full of nonsense. A **story** captures one such way the system can be
entered or broken, and lives in the verification code itself - a multi-line string that a person, an agent,
or a CI report can read and know exactly what is promised.

Four facts make a story. A fifth rule makes it readable.

| Fact | The question it answers |
|---|---|
| **Cause** | Who or what starts this - a passage of time (T), a user act (U, happy or sad), the service/platform misbehaving (S)? Named specifically: platform + mechanism + reference, never a category. A meta-story (X) enters one run through all three doors. |
| **Frequency** | How often does this really occur in use - High, Medium, Low, Rare? Frequency is about the world, not about test runtime. |
| **Expectancy** | What is the user PROMISED at that moment? The bar is the promise, not perfection: an interrupted backup honestly promises *redo*, not auto-resume. Say what is not promised when readers might assume it. |
| **End** | The concrete condition that closes the story - "refresh succeeded and the banner is gone", not "works again". |

**The accuracy rule (the one that matters).** Read any sentence of the story and interrogate **every claim in
it** - not just the causer: *who or what exactly did it, why did it happen, under what condition, at what
moment, and what exactly will be seen?* Accuracy is the discipline for every noun in the story:

> "the OS terminated the backup" → `Android terminates the running backup via low-memory kill under process
> pressure (see docs/platform/android-lmk.md)`
> "an error occurred" → `POST /v1/backup/checkpoint returns 500 on the run's third call`
> "the banner goes away" → `the stale-refresh banner is removed from the view once refresh resolves`
> "it becomes stale" → `the load runs 25h after the last cache write; FeedCache.isStale() compares TTL=24h`

Two habits make this cheap:

- **A category is not a thing.** "OS", "server", "network", "eventually", "gracefully" are categories or
  moods - name the concrete actor, endpoint, condition, and moment. If a sentence could describe three
  different causes, it describes none.
- **Cite, don't teach.** When the *why* is a mechanism documented elsewhere (how Android's LMK works, the
  server's failover policy), the story **names the mechanism and drops a reference** - doc-file, code-file
  or symbol, spec section, URL, whatever the project already trusts - and stops there. The string stays
  short; the reason stays auditable. No story paragraph may turn into a platform lecture.

If any sentence cannot answer *who/what, why, exactly when* - because its subject is a whole category, its
reason is unstated, or its expectation is a feeling - the story isn't written yet. It's a rumor.

## The id

```
[CASE-FREQ-S<number>]     examples:  T-L-S17   U-H-S18   S-R-S20   X-M-S21
CASE:  T timeframe · U user · S service/platform · X meta-story (covers T+U+S in one run)
FREQ:  H high · M medium · L low · R rare
<number>: sequential per project, never reused; the story string of an X-meta lists the doors it covers.
```

The id lives at the head of the story string, so grepping `[S17` finds the story, the test, and any defect
noted against it. Keep the counter in one place (a registry line in the feature's docs or the test file
header) so two agents never mint the same number twice.

## Discovering the stories (before writing any)

Walk the system for its doors, not for its features. The full procedure with the probing questions:
`references/01-discovery.md`. The shape:

- **Timeframe (T):** list every time constant that exists in the code (TTLs, expiry windows, retry horizons,
  nightly slots). Each one is a story boundary - write the story of crossing it, and of what happens *not*
  crossing it.
- **User (U):** list every verb the user has (every command, every confirm button, every way to leave).
  Each gets its happy story; the dangerous few get their abandon/mistake stories.
- **Service/Platform (S):** list everything outside your control (server endpoints, OS process lifecycle,
  disk, network, clock skew). For each, ask *how can it betray us specifically* - wrong enum, half-file,
  wrong system time - and name each betrayal's exact actor and mechanism with a reference ("Android
  low-memory kill under pressure, see `docs/platform/android-lmk.md`"), never the bare category ("the OS
  killed it"). Interrogate every claim in the story the same way - the why, the when, the what-you-see.
- **Merge to meta (X):** when several doors must land on the same end state, one meta-story checks the
  sameness; keep the individual stories if each door also has its own detail to protect.

Rate frequency from real use, then set the expectancy bar by asking *what do we actually tell the user they
will see* - and write the ending as a predicate a machine can check.

## Writing the string - organized prose, not a schema

The story is a short, organized description sitting in the test's **report-visible record** - the title
string where runners print titles, the docstring or logged string where they don't
(`references/02-in-code.md` maps the carriers): cause-and-frequency paragraph first, then what you should
see, then optionally how it runs and ends. Order roughly cause → promise → end, because that's how it's
judged; but it stays prose - a story that needs no sequence paragraph does not grow one to fill slots, and
none of `STORY:/TRIGGER:/END:` are required keywords.

The story string itself is language-free; its *carrier* is not. One sketch of the string, then how the same
text rides different runners is `references/02-in-code.md` (JS/TS titles, pytest docstrings, Go `t.Log`,
Rust/Java/JVM doc-and-output - plus anything else, the rule is the report, not an API):

```text
[T-L-S17] Stale feed shows refresh banner
  The user opens Basr 25 hours after its last feed write; the feed cache TTL is 24h, so the
  staleness check FeedCache.isStale() fires on load. Time caused this - nobody touched anything.
  Most launches hit a fresh cache; this one does not.

  What the user should see: a banner offering refresh, with the cached rows still painted
  underneath while it sits there. That is the whole promise - no silent background refetch,
  no skeleton forever. The story ends when the refresh succeeded and the banner is gone, or
  the user dismissed it.

  (executable steps follow, in the project's own runner idiom)
```

## Boundaries

| Not this | Go instead |
|---|---|
| How to structure the assertion, one-reason-to-fail, suite mechanics | `test` |
| Measured numbers, perf comparisons | `benchmark` |
| Choosing between approaches with evidence | `thebest` |
| "As a user, I want..." PM tickets, INVEST, Gherkin - this skill's stories live in code, not in a backlog tool | ordinary PM work |
| Feature docs | `document` |

## Files

| Need | Load |
|---|---|
| The discovery walk: where T/U/S stories hide, frequency rating, promise-bar questions | `references/01-discovery.md` |
| The story string per language: where the text lives when names can't be multi-line, registry upkeep | `references/02-in-code.md` |
| Full worked set: the backup flow across all four cases + vague→accurate rewrites | `examples/backup-flow.md` |
