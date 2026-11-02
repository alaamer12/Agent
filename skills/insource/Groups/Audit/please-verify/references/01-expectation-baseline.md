# The expectation baseline

Verification without a baseline passes everything. The baseline is the list of things that must be true
before "done" is allowed, **drawn from what the user actually asked for** - never from the code's own
ambitions, and never from the agent's summary of what it did.

## Where the expectation lives, in precedence order

1. **The user's own words in the conversation** - the latest statement wins over older ones; a corrected ask
   replaces the original, and both are read before assuming.
2. **The project's idea/spec documents** - IDEA.md, plans, specs, AGENTS.md obligations. If they exist and
   contradict the conversation, the conversation usually reflects the newest intent - **verify both readings
   if they materially differ, and flag the conflict in the report** instead of silently choosing.
3. **The definition of done the project itself declares** - tests to pass, commands to run, docs to ship.
4. **Conventions the project already enforces** - AGENTS.md rules, stack standards, privacy/glossary rules.
   These count as requirements even when the user did not restate them.

What is *not* a source: the code's own comments about what it intends, the agent's changelog of itself, or
your own assumption of what "a good app" would include. Those are claims to verify, not the bar.

## Turn every ask into observable outcomes

Broad requests are the dangerous ones. "Create a full working app" is not verifiable; it becomes a
checklist of things a person could watch happen:

| Broad ask | Observable outcomes (the baseline) |
|---|---|
| "a full working app" | builds on a clean checkout · launches without crashing · the main flow completes end to end · data persists across restart · the promised error/empty states appear · the project's own docs describe how to run it correctly |
| "this is finished" | every requirement in the conversation/plan has an artifact · the suite runs green in this state · the app starts and the feature is reachable · the definition of done the user stated is met |
| "the export works" | the export produces a file · the file opens in its target application · the content matches the promised columns/format · the empty and failed cases behave as promised |

Each row gets: **requirement · how it will be proven (the evidence level it needs) · where it should exist**.
A requirement with no way to prove it is a gap in the baseline - say so, and verify the part that is provable.

## Naming the bar

Write the baseline in chat before the sweep - five to fifteen lines, numbered:

```text
Done = all of:
  1. App builds (<project build command>) and the build log shows success        [L1]
  2. App launches and the home screen renders                                     [L3-L4]
  3. Screen "Add item" saves an item; it survives a restart                       [L4]
  4. Empty state text matches <the promised copy>                                 [L4]
  5. Test suite passes in this state (<command>)                                  [L2]
  6. README's run instructions reproduce the above on a clean checkout            [L1-L3]
Not part of this verification: <what is explicitly out of scope>
```

The user can then correct the bar *before* the work is judged, which is cheaper than arguing after.

## Conflicts, silence and ambiguity

- **Conflict between sources** (conversation says X, plan says Y): verify the newer, report the older as a
  disagreement to resolve - never pick one silently and call the other "wrong".
- **Silence**: an unstated requirement is an *open item*, not a failure. Keep a separate "unstated /
  not verifiable as specified" list.
- **Impossible or environment-blocked requirements** ("prove it on a phone") are `UNVERIFIED`, with the
  reason and what partial proof was possible (desktop run, emulator, static review).
- **Never raise the bar to be helpful.** "While I'm here, I also checked accessibility and it failed" is
  scope creep in the verdict; put extra observations under a clearly separated "outside the baseline" note.
