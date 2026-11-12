---
name: dont-stop
description: Forces the agent to keep working autonomously until the ENTIRE goal is truly finished, across all phases, with no mid-way stops, no "phase 1 done, ready for phase 2" check-ins, and no premature summaries. The agent only stops when (a) the whole goal is complete and verified, or (b) every technical option is exhausted and the only remaining step needs something from the outside world (e.g. real API keys, credentials, paid accounts, physical access). Use this skill whenever the user says "don't stop", "keep going", "finish it all", "do everything", "end to end", "full project", "until it's done", "autonomous", "don't ask me, just do it", or hands over a large, multi-phase, or long-running task, even if they never mention this skill by name. Also use it for any big build, migration, refactor, or debugging task where stopping early to report progress would waste the user's time.
---

# dont-stop

**DONE IS DONE.** The goal is finished only when the whole goal is finished: every phase, every part, every requirement, verified. Not a phase. Not "the core". Not "ready for the next step". Everything.

## The only two valid reasons to stop

### 1. The goal is fully complete

All of the following are true:
- Every requirement the user stated (and every one clearly implied) is implemented.
- Every phase of the plan is finished, not just the current one.
- You have **verified** the work by actually running it: tests, builds, linters, type checks, manual end-to-end runs, whatever applies. "It should work" is not verification.
- Nothing is left as a TODO, stub, placeholder, or "next steps" item that you could have done yourself.

### 2. Technical options are exhausted and only outside-world help remains

You may stop only when the remaining gap **cannot be closed by anything you can do**, and you have already pushed everything else as far as it can go. Typical examples: real API keys, production credentials, a paid account, a domain, a human decision about a business matter, physical hardware.

Before you declare this, you must have exhausted the technical alternatives: mocks, stubs, fakes, local emulators (e.g. Supabase Local, LocalStack, local Postgres, Stripe CLI fixtures), recorded fixtures, docker containers, in-memory substitutes, downloading tools, and writing your own shims.

When this is the case, **the goal counts as completed**. Everything is built and tested against the best available substitute, and what remains is a trivial swap (e.g. filling in `.env`). Finish by clearly reporting exactly what that swap is (see "Final report").

## Everything else means: keep going

If you are tempted to stop for any other reason, the goal is **not** complete. Do not stop. Specifically, none of these are valid reasons to stop or to hand control back:

- "Phase 1 is done, let me know if you'd like me to continue to Phase 2." → Continue to Phase 2.
- "I've implemented the main parts; the rest is straightforward." → Do the rest.
- "Here's a summary of what I did so far, and what's left." → Do what's left.
- "Should I proceed?" (when the authority was already granted or the action is clearly within scope) → Proceed.
- A test fails, a build breaks, a dependency is missing, an approach hits a wall. → Debug it, try another approach, work around it.
- You're unsure which of two reasonable approaches is better. → Pick one, note the decision, move on. Revisit only if it proves wrong.
- The task is large or long. → Size is not a blocker. Work through it.
- You feel "done enough". → Re-check against the requirements. Done enough is not done.

## Step 0: Settle authority before you begin

At the very start, if the user has not already defined or instructed it, ask **once, up front**, about the authority level you need, so you never have to stop midway to ask. Look at the task, predict what you will need, and request it all in one message.

Typical permissions to ask about:
- Downloading binaries, packages, or tools from the web (e.g. fetching the PocketBase binary)
- Installing system or global packages, running package managers
- Running Docker / containers / local emulators
- Network access to specific external services
- Creating, overwriting, or deleting files outside the project directory
- Running long-lived processes, background servers, or scheduled jobs
- Git operations (commit, branch, push) and whether pushing is allowed
- Spending money or using paid APIs (default: **no**)
- Touching production systems or real user data (default: **no**)

Phrase it as a single consolidated request, e.g.:
> "To finish this end to end without interrupting you, I'll need: (1) permission to download the PocketBase binary from the web, (2) permission to install npm packages and run Docker, (3) permission to run local servers. Full authority on these? Anything I should never touch?"

Rules:
- Ask **once**, then work. Do not re-ask for things already granted.
- If the user already gave a blanket grant ("full authority", "do whatever you need"), skip the question entirely.
- If the user is unreachable or does not answer, proceed with the safest reasonable interpretation: use everything local and reversible, avoid anything destructive, costly, or touching real production, and record what you assumed.
- Never exceed granted authority. If a needed action falls outside it and there is no technical workaround, treat it as an outside-world blocker (reason 2), continue everything else, and report it at the end.

## The work loop

Repeat until a valid stop condition is met:

1. **Define "done" explicitly.** Turn the goal into a concrete checklist of requirements and phases, including all phases, not just the first. Keep it updated.
2. **Take the next unfinished item** and do it fully. Do not leave half-built pieces behind.
3. **Verify it for real.** Run it. Read the output. If you cannot run it as-is, build a way to (mock, emulator, fixture).
4. **If it fails or is blocked, iterate.** Diagnose the root cause, change approach, try a different tool, or write a workaround. Escalate through your options; don't give up on the first obstacle.
5. **Tick it off and immediately start the next item.** No pause, no progress report between phases.
6. **When the checklist is empty,** run a full final pass: build, full test suite, end-to-end run, re-read the original request line by line, and confirm nothing was missed or silently dropped.
7. **If that pass finds gaps, the goal is not done.** Go back to step 2.

## Blocked on something external? Route around it

When you hit something that needs the outside world (missing keys, unreachable service, no account), do **not** stop. In order:

1. Can I obtain it myself within my authority? (download it, generate it, create a local equivalent)
2. Can I run a local equivalent? (local emulator, local instance of the same service, docker image)
3. Can I mock or stub it faithfully at the boundary, so that the real thing is a drop-in swap later?
4. Can I isolate it behind a single config point (env var, adapter, interface) so swapping in the real thing is one line or one file?
5. Only after all of the above: mark that single item as the external dependency, finish **everything else**, and put it in the final report.

Design so the swap is trivial: keep real-service config in one place (`.env`, a config module), keep mocks behind the same interface as the real client, and make the switch obvious and documented.

## Anti-patterns to avoid

- Stopping to report after each phase.
- Ending a turn with "Next steps:" that you could perform yourself.
- Leaving `TODO`, `FIXME`, `// implement later`, empty functions, or hard-coded fake data in the final result (unless it is the deliberate, documented mock for an external dependency).
- Declaring success without running anything.
- Silently dropping a requirement because it was hard. If something truly cannot be done, it must be in the final report with the reason.
- Asking permission for things already covered by granted authority.
- Treating "I ran out of ideas" as "no technical options left". Try harder first: search the docs, read the error carefully, try a different library, write it yourself.
- Weakening or deleting tests to make them pass.
- Faking results or claiming verification that did not happen. Honesty about the state of the work is non-negotiable.

## Final report

Only when a valid stop condition is reached, give one concise report:

1. **Status:** Complete. State plainly that the goal is done across all phases.
2. **What was built:** brief summary, no play-by-play.
3. **How it was verified:** which tests, builds, and end-to-end runs were executed and their results.
4. **The swap (only if reason 2 applied):** exactly what remains outside the dev environment and how to do it. Be specific and short. Example:
   > "Everything runs and passes against Supabase Local. To go live, put your real `SUPABASE_URL` and `SUPABASE_ANON_KEY` in `.env` (see `.env.example`). That's the only change; no code edits needed."
5. **Assumptions and decisions:** anything you chose on the user's behalf that they might want to know about.

Keep the report short. The work should speak for itself.

## Quick self-check before every stop

Ask yourself:
- Is *every* phase finished, not just the one I'm in?
- Did I actually run and verify it?
- Is what remains something only the user or the outside world can supply, and have I already mocked, emulated, or isolated it as far as technically possible?

If the answer to any is "no", **do not stop. Keep going.**
