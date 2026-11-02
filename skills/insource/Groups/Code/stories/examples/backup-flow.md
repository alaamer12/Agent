# Worked set - the backup flow, start to finish

One feature (Basr backing up 5 photo files to app storage), walked, numbered, and written. The point is the
process end to end - and the story string is the artifact; the syntax wrapping it is whichever runner the
project has (carriers in `references/02-in-code.md`).

## 1. The walk (what the doors were before any story was written)

| Door | Kind | Exact condition | Real frequency |
|---|---|---|---|
| tap Start, one run completes | U-happy | all 5 files copy | H |
| user force-quits mid-backup | U-abandon | OS task-swipe at file 2 of 5, third write half-flushed | L |
| double-tap Start | U-mistake | second tap within 300ms while first run active | M |
| nightly window passes mid-run | T-timeframe | 02:00 slot ends at 50% | L |
| checkpoint endpoint 500s | S-service | POST /v1/backup/checkpoint → 500 on the 3rd call | M |
| checkpoint 200 with nonsense | S-service | 200, `state:null`, `items:-1` | R |
| disk full at file 3 | S-platform | ENOSPC during third copy | R |
| Play Store update restarts the app mid-run | S-platform | updater replaces the APK, process respawn at file 3 (see `docs/platform/android-updates.md`) | L |

Eight doors; the flow gets seven individual stories + one meta. (The ENOSPC one is written as its own story,
R-frequency, because its promise differs from the others: partial file cleanup is specific to disk-full.
The Play Store restart shares S23's promise - honest partial + one-tap redo - so it stays a listed door,
not yet a story: it earns its own id when its detail (an update-time resume prompt) needs guarding on its
own. A door held is honest; a door silently merged is coverage drift.)

## 2. The promise bar, asked per door

- Happy (H): progress + done-state that names what was backed up. Ends: file exists, done-label true.
- Force-quit (L): **honest partial + one-tap redo** - explicitly *not* resume; the redo must complete the
  whole backup. Ends: fresh full backup verified.
- Double-tap (M): the second tap changes nothing (in-flight guard), no second run. Ends: one backup file,
  not two.
- Nightly-window pass (L): same promise as force-quit - it is the same kind of interruption, and that's
  what makes it a meta member, not a special story.
- 500 on checkpoint (M): "backup could not be verified - retry" - visible, pressable. Ends: retry succeeds
  or error stays honestly on screen.
- Nonsense 200 (R): "status unavailable", never a crash, never the garbage rendered as truth ("-1 items").
  Ends: next valid poll repaints.
- Disk full (R): names the file that failed, frees-space help, no silent skip. Ends: either complete after
  user frees space, or user cancels with partial state flagged.

## 3. Ids minted

`U-H-S22` happy · `U-L-S23` force-quit · `U-M-S24` double-tap · `T-L-S25` nightly window · `S-M-S26` 500 ·
`S-R-S27` nonsense-200 · `S-R-S28` disk-full · meta `X-L-S29` interrupted-backup-across-doors (S23, S25, S26
are its three doors - each keeps its own story too, because each has a detail the meta can't carry).

## 4. One story in full, the way it ships - same string, two carriers

The story text is the artifact; the runner wraps it. TypeScript/Vitest:

```ts
test(`[U-L-S23] User force-quits at file 2 of 5 - next launch says partial, redo is one tap
  The user swipes Basr away from the recent-apps list while the backup is halfway: files 1-2
  copied, the third write half-flushed, nothing marked complete. Low frequency - most installs
  never do it - but every install that does remembers.

  What the user should see on next launch: an honest partial state. NOT "backup complete" -
  the promise is truth plus a one-tap redo. Auto-resume is explicitly not promised: we expect
  the user to redo, so the redo path IS the story's goal.

  Ends when the offered redo runs and a full backup verifies: 5 files, no partial marker left.
`, async ({ app, lifecycle }) => {
  await app.openBackup();
  await app.tapStart();
  await app.waitForProgress(50);
  await lifecycle.forceQuit();
  await app.relaunch();
  await expect(app.backup.statusLabel()).toHaveText(/incomplete/i);
  await expect(app.backup.doneLabel()).toBeHidden();
  await app.tapRedo();
  await expect(app.backup.verified()).resolves.toBe(true);
});
```

The identical story in the Go family (`t.Log` carries what the name cannot):

```go
func Test_ULS23_ForceQuitMidBackup(t *testing.T) {
    t.Log(`[U-L-S23] User force-quits at file 2 of 5 - next launch says partial, redo is one tap
The user swipes Basr away from the recent-apps list while the backup is halfway: files 1-2
copied, the third write half-flushed, nothing marked complete. Low frequency.

What the user should see on next launch: an honest partial state. NOT "backup complete" -
the promise is truth plus a one-tap redo; auto-resume is not promised.
Ends when the offered redo runs and a full backup verifies: 5 files, no partial marker left.`)

    app.OpenBackup(); app.TapStart(); app.WaitForProgress(50)
    lifecycle.ForceQuit(); app.Relaunch()
    if got := app.Backup().StatusLabel(); !strings.Contains(got, "incomplete") {
        t.Fatalf("status = %q, want honest partial", got)
    }
    app.TapRedo()
    if !app.Backup().Verified() {
        t.Fatal("redo did not produce a verified full backup")
    }
}
```

Same prose in pytest docstrings or JUnit `@DisplayName` - see `references/02-in-code.md` for the carriers.

## 5. The same door written badly, and the rewrite that fixes it

| Vague (rejected) | What it hides | Accurate (accepted) |
|---|---|---|
| "the app is closed mid-backup" | who closed it - user? OS? updater? different promises | "the user swipes Basr from recents at file 2 of 5" |
| "the OS terminated the backup" | *which* OS, by what mechanism, where that's written down | "Android terminates the backup process via low-memory kill under memory pressure (see `docs/platform/android-lmk.md`)" - mechanism named, explanation left in the reference, not the story |
| "cache becomes stale" | stale per which check, after what, why | "launch 25h after last write; TTL 24h; `isStale()` fires on load" |
| "server returns malformed data" | malformed how - 500? timeout? poison success? | "checkpoint returns 200 with `state:null`, `items:-1` - success wearing garbage" |
| "the app handles it gracefully" | graceful = what seen, and ends where | "shows 'status unavailable'; never renders the garbage as truth; ends when next valid poll repaints" |

The left column fails one test: read the sentence and interrogate every claim - **who/what did it, exactly,
why, under what condition, and what will be seen?** - if any answer needs a detective or is a whole category
("OS", "server", "gracefully"), rewrite until it doesn't. Where the answer's *why* is a documented
mechanism, name it once and cite; never lecture.
