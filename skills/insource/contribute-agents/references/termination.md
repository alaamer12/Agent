# Termination Model

## Time limit vs termination condition

- **Time limit**: a hard stopwatch cutoff supplied by the user (e.g. "run for 3
  minutes", "stop after 20 messages each"). When it's reached, the orchestrator stops
  accepting new messages and shuts the collaboration down immediately, regardless of
  whether the discussion "feels" finished. A time limit expiring is **not** by itself a
  successful outcome — report it as a timeout, not as agreement, unless the user's
  policy explicitly equates the two.
- **Termination condition**: a semantic statement of what "done" means (e.g. "stop when
  they reach agreement", "stop when every objection has been addressed", "stop when the
  leader is satisfied the ground truth has been established"). This is evaluated
  continuously by the leader agent (and, procedurally, by the orchestrator), not by a
  clock.

If the user gives both, treat the time limit as a safety cap that can cut the discussion
short, and the termination condition as what actually defines success. Always report
which one actually ended the run.

## Leader responsibilities

Exactly one agent is the leader (default: Agent 1, unless the user names another). Only
the leader may declare that the termination condition is satisfied. Before doing so, the
leader must verify:

- The required work/discussion the user asked for was actually completed, not merely
  attempted.
- Important disagreements were either resolved or are explicitly documented as open
  (never silently dropped).
- Objections raised during critical review were addressed — either accepted, rebutted
  with reasoning, or explicitly marked as unresolved.
- Cited evidence that was disputed got checked, where the runtime allowed it.
- The user's actual termination condition (not the leader's personal sense that "this
  feels finished") is satisfied.

The leader must not end the discussion just because agents stopped posting for a while —
that may just mean nobody has anything new to say yet, or (in duplex mode) they're
waiting to be addressed. If activity has genuinely stalled without meeting the
termination condition, that's the orchestrator's problem to solve procedurally (e.g. ask
the leader to summarize the stuck point), not a silent, undeclared end.

## The termination statement

When the leader determines the condition is met, it must write an explicit termination
statement into the shared workspace — this becomes the ground-truth conclusion of the
collaboration, not something the orchestrator infers on its own:

```
TERMINATION STATEMENT
Status: COMPLETE
Termination condition: <restate the condition that was satisfied>
Conclusion: <the agreed-upon (or best-supported) outcome>
Key decisions: <the load-bearing decisions made along the way>
Known limitations: <what's still uncertain, unverified, or out of scope>
Evidence: <key citations/sources that held up under review>
The collaboration is terminated because: <explicit justification>
```

The orchestrator watches for this statement (or the time limit) as the sole valid ending
signal. If the collaboration ends via time limit instead, the orchestrator's final
report must say so plainly and should not fabricate a termination statement on the
leader's behalf — report the discussion as it actually stood when time ran out,
including that no formal termination statement was reached if that's the case.

## Emergency termination (stall watchdog)

A time limit and a termination condition don't cover every failure mode: a discussion
can go silent — no new message and no termination statement — without either ever being
reached, because an agent crashed, got stuck in a bad wait loop, or the workspace
mechanism broke. The orchestrator must watch for this independently of the two rules
above.

- **Stall threshold**: if **2 minutes** pass with no new message committed to the shared
  workspace and no termination statement posted, treat this as a stall, not as a valid
  ending. This applies whether or not the user also gave a time limit — a stall can
  happen well before any time limit expires.
- **On stall, do not**:
  - silently end the collaboration and report it as a normal conclusion,
  - fabricate or infer a termination statement on the leader's behalf,
  - quietly restart or replace an agent's reasoning to "unstick" it.
- **On stall, do**:
  1. Check for an obvious infrastructure failure first (workspace file missing/
     corrupted, lock never releasing, a subagent crashed or errored out). If found,
     record it plainly.
  2. Stop the experiment (treat it the same as a timeout for shutdown purposes: stop
     accepting new messages, terminate the subagents).
  3. Report to the user exactly what happened: how long the discussion actually ran,
     the last message and who sent it, whether any agent appeared to have crashed or
     stopped responding, and the likely cause if one is apparent (e.g. an agent waiting
     on the wrong condition, a duplex agent expecting to be addressed by name that never
     was, a broken read/send loop).
  4. Ask the user whether to re-run with adjusted prompting (e.g. clearer persistence
     instructions, a different communication mode, a more explicit initial prompt) or to
     drop the experiment. Do not unilaterally decide to retry on the user's behalf.

This stall watchdog is a procedural safety net, not a substitute for the leader's
termination condition or the user's time limit — it only fires when the discussion has
gone quiet without either of those two ever being satisfied.
