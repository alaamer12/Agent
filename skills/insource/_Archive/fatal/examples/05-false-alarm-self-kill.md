# Example 5 - "It disappeared again!" that was not a crash (from the DemoApp session)

**Prompt:** "After the fix I rebuilt and ran; it's gone again, you didn't fix it."
Run (sample data in `assets/samples/`):
```
python scripts/build_timeline.py assets/samples/heartbeat.sample.log:hb assets/samples/watchdog.sample.log:watchdog --death "2026-03-12 16:43:30"
```
Findings: heartbeat beats at 16:39:43 and 16:41:43 then **stop**; watchdog log has **no** entry after the earlier test kill; Event Log shows an Application Error only for the *old* build (different pid/version); the publish `DemoApp.exe` was rewritten at 16:44:38. The release script runs `Stop-Process -Force` on **every** `DemoApp.exe` (app + watchdog) to free the file lock.
Verdict: class E external kill by the build, not a crash. Evidence: no dump (E0), no new Event 1000 for the new build (E0), heartbeat+watchdog silent together (E1), exe rewrite time (E1).
Report it that way, with the one-line change that avoids the confusion (log a "stopped by release script" marker, or kill the watchdog first / set the clean-exit event).
