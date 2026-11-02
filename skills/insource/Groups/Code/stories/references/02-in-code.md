# The story string in code, per language

The record is one organized-prose string: id first, then cause-and-frequency, then the promise, then (when
worth spelling) how it runs and ends. What is *required* is that the prose sits **with the executable steps**
and survives into the run report - the exact carrier differs by runner, and the honesty of the report is
what you optimize for.

> The carriers below are examples across runner families, not an exhaustive or mandatory list. Hybrid or
> unlisted setups are fine - any project already printing story text in its failure output satisfies the
> rule; the rule is about the report, never about a specific API.

## Where the string lives

| Language / runner family | Carrier | Why |
|---|---|---|
| JS/TS (Vitest, Jest, Playwright) | the test title itself - template strings are multi-line and printed by reporters | one artifact: the name IS the story |
| Python (pytest, unittest) | the test's docstring - pytest reports it with failures (`--show-capture`), `pytest --collect-only -q` lists ids | docstring is the standard place for "what this test means" |
| Go (`testing.T`) | names can't hold newlines: short title `Test_TS17_StaleBanner` + `t.Log`/`t.Helper` printing the full story string as the first statement (or a table-driven `story` field logged via `t.Log`) | keeps the prose in the test binary's output, not a comment |
| JVM (JUnit 5, Kotlin test) | `@DisplayName("""multi-line string""")` - shown in IDE and CI reports | the annotation exists exactly to carry human text |
| Rust (libtest) | names can't be prose: doc comment `///` on the `#[test] fn` plus a one-line id summary in the fn name; if the report must show it, wrap with a small custom test harness or print the string from a registry test - libtest hides stdout without `--nocapture`, so pick honestly | acknowledges libtest's weak report instead of faking a carrier |
| Anything else | id + short name, full string as the first logged line of the test body | the rule: the story must appear in the failure report, not only in source |

The anti-pattern in every language: the story as **comments** above the test. Comments vanish from CI
output, get separated from the steps they describe, and rot silently when someone edits the body. If a
reader sees only the failure report, they must still get the story.

## The shape (soft order, no keywords required)

```
[CASE-FREQ-S<number>] Short title that survives being the only line a reporter shows

  Cause paragraph: who or what does it, under what exact condition, and how often it really happens.
  Promise paragraph: what the user should SEE. The bar is the promise; name what is NOT promised when
                      the assumption is likely.
  Run/End (optional): the sequence and the predicate that closes the story - only when they add
                      precision; a two-line story that ends in one clause ends in one clause.
```

Not a schema. `STORY:`/`TRIGGER:`/`END:` labels are forbidden as requirements (they turn prose into form
filling and invite empty filler); a project may *choose* them as convention - then use them consistently,
as an option, not this skill's default.

## References inside the string - cite, don't teach

When the *why* of something is a mechanism explained elsewhere, the string names the mechanism and drops a
reference in one clause - `(see docs/platform/android-lmk.md)`, `(see core/FeedCache.isStale(), TTL=24h)`,
`(Android 14 behavior change, developer.android.com/…)`. Choose whatever this project already trusts: a
doc-file, a code-file or symbol, a spec section, a URL. Then stop.

- **In**: the mechanism's *name* + the pointer. `Android terminates the backup process via low-memory kill
  under memory pressure (see docs/platform/android-lmk.md).`
- **Out**: the mechanism's *explanation*. No story paragraph may become an LMK lecture - the reference is
  what keeps the story short while keeping the reason auditable.
- Keep references to one clause per claim; two references in one sentence usually means the claim should
  split into two stories.

## Worked carriers

**TypeScript / Vitest:**

```ts
test(`[S-R-S20] Checkpoint answers 200 with state:null - status says unavailable, not nonsense
  The app polls POST /v1/backup/checkpoint; the server replies 200 (a *successful* call) with
  state:null - not a 500, not a timeout: success wearing garbage. Rare; the last bad deploy did it.

  What you should see: "status unavailable". The app does NOT crash and does NOT render
  "-1 items" as if it were real. End: the next valid poll repaints the real status.
`, async ({ app, server }) => {
  server.mock("/v1/backup/checkpoint", { status: 200, body: { state: null } });
  await app.pollStatus();
  await expect(app.statusLabel()).toHaveText("unavailable");
  server.mock("/v1/backup/checkpoint", { status: 200, body: { state: "running", items: 3 } });
  await app.pollStatus();
  await expect(app.statusLabel()).toHaveText("running");
});
```

**Python / pytest:**

```python
def test_s17_stale_banner(app, clock):
    """[T-L-S17] Stale feed shows refresh banner
    The user opens the app 25h after the last feed write; the cache TTL is 24h, so the
    staleness check fires on load. Time caused this - nobody touched anything. Most launches
    hit a fresh cache.

    What you should see: a refresh banner with cached rows still painted underneath. End:
    refresh succeeded and the banner is gone (or dismissed).
    """
    seed_cache(app, FEED_V1, age="25h")
    app.open()
    assert app.banner("stale-refresh").visible
    assert len(app.feed.rows()) == len(FEED_V1)
    app.tap_refresh()
    assert not app.banner("stale-refresh").visible
```

**Go:**

```go
func Test_TS17_StaleBanner(t *testing.T) {
    t.Log(`[T-L-S17] Stale feed shows refresh banner
The user opens the app 25h after the last feed write; the cache TTL is 24h ... (full story string)`)
    ...steps...
}
```

**JVM (Kotlin / JUnit 5):**

```kotlin
@DisplayName("""[T-L-S17] Stale feed shows refresh banner
  The user opens the app 25h after the last feed write; the cache TTL is 24h, so the
  staleness check fires on load. Time caused this - nobody touched anything.

  What you should see: a refresh banner with cached rows still painted underneath.
  End: refresh succeeded and the banner is gone (or dismissed).""")
@Test
fun staleFeedShowsRefreshBanner() {
    seedCache(feedV1, age = 25.hours)
    app.open()
    assertTrue(app.banner("stale-refresh").isVisible)
    app.tapRefresh()
    assertFalse(app.banner("stale-refresh").isVisible)
}
```

## Meta-stories (X) in code

One test, the doors shown as named sub-runs so the report identifies *which* door failed. The sub-run
naming device per family - `[Playwright test.step]`, `[Go t.Run]`, `[JUnit 5 @ParameterizedTest with
names]`, `[pytest subtests fixture, or one test per door sharing a helper]`, or plain sequential log lines
where the runner offers nothing - all satisfy the same rule: the failure line names the door.

Example, Playwright family:

```ts
test(`[X-M-S21] Interrupted backup - time, user kill, and server 500 must all land the same way
  The same run entered through three doors: the nightly window passes at 50%, the user
  force-quits at file 2 of 5, the checkpoint call 500s at file 3. All three must end at the
  same promise: honest partial state + one-tap redo that finishes. Auto-resume is NOT promised.
`, async ({ app, clock, lifecycle, server }) => {
  for (const [name, cut] of [
    ["T via nightly window", () => viaTimeframe(app, clock)],
    ["U via force-quit",     () => viaUserKill(app, lifecycle)],
    ["S via checkpoint 500", () => viaServerError(app, server)],
  ]) {
    await test.step(name, async () => {
      await cut();
      await expect(backupState(app)).toBe("partial-not-done");
      await app.tapRedo();
      await expect(app.backup.verified()).resolves.toBe(true);
    });
  }
});
```

The same meta, Go family - `t.Run` gives each door its own report line:

```go
func Test_XS21_InterruptedBackupAllDoors(t *testing.T) {
    t.Log(`[X-M-S21] Interrupted backup - time, user kill, and server 500 must all land the
same way ... (full story string, naming each door's exact condition)`)
    doors := map[string]func(*appHarness){"T-nightly": cutByNightly, "U-forcequit": cutByKill, "S-checkpoint500": cutByServerError}
    for name, cut := range doors {
        t.Run(name, func(t *testing.T) {
            h := newHarness(t)
            cut(h)
            if got := h.backup.State(); got != "partial-not-done" {
                t.Fatalf("state = %s, want partial-not-done", got)
            }
            h.app.TapRedo()
            if !h.backup.Verified() {
                t.Fatal("redo did not finish")
            }
        })
    }
}
```

The `CASES` content lives in the prose (naming each door and its exact condition), not as a field.

## Registry and numbering

- One counter per project, never reused, never renumbered after a defect cited an id.
- Where the counter lives is the project's choice (a line in the feature's docs, a constant in the test
  helper, the issue tracker) - what matters is that two agents minting stories at the same time can see
  it. If the project has none, put a one-line registry comment at the top of the story file:
  `// stories: last id S21`.
- Grep-friendliness is the point: `[S17` must find the story string, the test, and any bug noted against it.
