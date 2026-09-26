---
name: contribute-agents
description: Coordinate multiple AI subagents that collaboratively work on a task, critique each other's reasoning, and converge on a documented conclusion. Use when the user wants two or more agents to discuss, debate, review, or jointly solve a problem (e.g. "have two agents argue about X", "run a panel of reviewers on this design", "make agents challenge each other's evidence") and wants a supervised discussion with an explicit termination condition and a final report.
license: N/A
compatibility: Requires a host agent/runtime capable of spawning and monitoring subagents (e.g. an agent-orchestration tool). Falls back to a file-based shared workspace when subagents can only communicate via the filesystem.
metadata:
  category: multi-agent-orchestration
  role: orchestrator
---

# Contribute Agents

Orchestrate a supervised, multi-agent collaboration: several subagents work on the same
task from different personas, communicate through a shared workspace, critically review
each other instead of agreeing by default, and stop only when an explicit termination
condition is met. You (the calling agent) act as the **Observer/Orchestrator** — you set
up the collaboration, delegate the subagents, monitor them, and produce the final report.
You never inject your own reasoning into their discussion.

This skill defines the **coordination protocol** (roles, workspace format, criticism
rules, termination rules). It intentionally does **not** invent a spawning or messaging
API: use whatever subagent-spawning and monitoring capability your runtime actually
provides (e.g. a "spawn subagent" tool). If the runtime cannot spawn independent
subagents at all, fall back to simulating each persona yourself, sequentially, using the
same protocol, and say so explicitly to the user.

## Step 1 — Gather configuration from the user

Before doing anything, make sure you know (ask if genuinely ambiguous, otherwise pick
sensible defaults and state them):

- **Task/topic**: what the agents must work on or discuss.
- **Number of agents** and, ideally, **their personas** (e.g. senior architect, security
  engineer, skeptical reviewer). If the user doesn't specify personas, choose ones that
  give genuinely different perspectives on the task — not the same prompt with different
  names.
- **Leader agent**: which agent can declare termination. Default: Agent 1.
- **Communication mode**: `duplex` (respond only when addressed) or `full-duplex` (post
  freely into the shared space). Default: full-duplex for open debates, duplex for
  strictly turn-based collaboration.
- **Working directory**: current working directory, or a fresh temporary directory when
  isolation from the real project is preferable (e.g. experiments, throwaway debates).
- **Termination condition** — see Step 2. This must be explicit; do not assume "3
  messages" or "agents went quiet" means done unless the user said so.
- **Agent/model choice**: use the runtime's fast/cheap iteration-tier model by default
  (many agents may run, often in parallel, so cost matters), unless the user asks for a
  specific model/agent implementation that the runtime actually supports. Never
  hard-code a model name the runtime doesn't offer.

## Step 2 — Set the termination model

Distinguish clearly between two different things:

- **Time limit**: a hard stopwatch cutoff (e.g. "run for 3 minutes"). When it expires,
  stop immediately regardless of discussion state.
- **Termination condition**: a semantic condition (e.g. "stop when they agree", "stop
  when all objections are resolved", "stop when the leader is satisfied"). This is
  evaluated continuously, not by a clock.

A time limit is not automatically success. If both a time limit and a termination
condition are given, the time limit is a safety cap; the termination condition is what
actually defines "done". Read `references/termination.md` for the full leader/
termination-statement protocol before you delegate the leader agent.

## Step 3 — Prepare the shared workspace

Every collaboration needs one deterministic, append-only shared workspace so subagents
never silently overwrite each other's contributions. Read
`references/protocol.md` for the full message format, ordering rules, and directory
layout, and decide upfront:

- workspace root (CWD or a fresh temp dir)
- the conversation/log file(s) subagents will read and post to
- whether you need write-serialization for concurrent full-duplex posting

If your runtime lets subagents run shell commands and the workspace is a plain text
file, you can reuse `scripts/collab_log.py` (see "Scripts" below) instead of building
your own serialization from scratch. If subagents can only communicate by returning
text to you (no shared filesystem access), you become the relay: collect each
subagent's message, append it to the shared log yourself, and pass the updated log to
the next subagent invocation.

## Step 4 — Build each subagent's prompt (three-part structure)

Never send all subagents the same prompt. For every subagent, compose a prompt from
three parts — see `references/prompting.md` for full guidance and templates:

1. **Persona & Context** — who they are, their expertise, the task, and relevant
   project/background info. Before writing this part, check whether the `persona-context`
   skill is available (it may live in the system's global skills or inside the current
   project, e.g. as a project-local skill directory) and read it first if so — it defines
   how to construct a deep, behavior-driven persona instead of a shallow "you are a senior
   X" label. Use it for every subagent's Part A. If it isn't available, fall back to the
   lighter guidance in `references/prompting.md` directly.
2. **Humanized Collaboration Instructions** — how to talk like an engaged colleague, not
   a checklist-following bot: react to what was actually said, acknowledge good points,
   disagree respectfully, ask real follow-up questions, separate facts from assumptions,
   admit uncertainty, avoid restating things already said.
3. **Critical Review Protocol** — the mandatory criticism rules (Step 5 below), phrased
   for that persona.

## Step 5 — Enforce criticism, not contrarianism

This is the most important behavioral requirement of the skill. Every subagent prompt
must instruct the agent to:

- Never treat another agent's claim as true just because it was stated confidently.
- Actively probe: validity of reasoning, unjustified assumptions, missing information,
  hidden edge cases, contradictions, simpler alternatives, whether evidence actually
  supports the conclusion, whether a cited source could be outdated or misread.
- Label each objection by strength: **confirmed flaw**, **likely concern**, **unverified
  assumption**, **missing information**, **alternative possibility**, or **disagreement
  without sufficient evidence** — do not silently upgrade a hunch to a fact.
- When an agent cites external evidence, it must include the URL. Any agent that relies
  on that evidence must not accept it on faith: inspect the source (fetch it if the
  runtime allows) and check whether it truly supports the claim, whether the relevant
  part was read correctly, and whether it's current/authoritative. If the runtime has no
  web/fetch access, the agent must say the claim is **unverified**, not pretend it
  checked it.
- When an agent agrees with another, it must say *why* the proposal survived review, not
  just "I agree".
- Never invent a flaw purely to appear critical; criticism must be evidence-based and
  constructive, and should suggest a correction or a concrete way to verify when
  possible.
- The goal is reaching the best-supported conclusion, not winning the argument. Every
  subagent must actively search for evidence and alternative explanations before
  restating or defending its own prior claim — instruct them explicitly to go look
  (re-check the source, search the web, re-read the issue, consider a case they hadn't
  thought of) rather than just responding to score a point. Update or abandon a position
  when the search turns up something that weakens it; do not defend an assumption just
  because it was said first.

## Step 6 — Launch and supervise

1. Initialize the shared workspace (empty log / opening message if the protocol calls
   for one).
2. Delegate each subagent with its full three-part prompt, its communication mode, and
   explicit instructions to keep participating (read → react → post → repeat) rather
   than finishing after one message, if the mode requires ongoing back-and-forth.
3. While they run, monitor: activity, whether an agent stalled or crashed, whether the
   discussion is circular/repetitive, whether unresolved objections are piling up, and
   progress toward the termination condition. Do not correct them, feed them technical
   answers, or suggest which side is right — that would corrupt the experiment. Allowed
   interventions are purely procedural (e.g. asking the leader to summarize a stuck
   disagreement, or asking one agent to go verify a disputed claim independently).
4. Stop the collaboration when either the time limit expires or the leader posts a
   proper termination statement (see `references/termination.md`) confirming the
   termination condition is satisfied — whichever the user's policy specifies.
5. **Emergency termination (stall watchdog)**: if **2 minutes** pass with no new message
   and no termination statement, that's a stall, not a valid ending — do not report it as
   agreement or quietly close it out. Stop the experiment, check for an obvious
   infrastructure failure (crashed subagent, broken lock, missing workspace file), and
   report to the user exactly what happened (last message, who sent it, likely cause).
   Then ask the user whether to re-run with better prompting (e.g. clearer persistence
   instructions or a different communication mode) or drop it — never decide that
   yourself. Full protocol in `references/termination.md`.
6. If a subagent crashes or the workspace mechanism fails: do not silently take over its
   reasoning or restart in a way that loses messages. Preserve what exists, record the
   failure, and report it.

## Step 7 — Produce the final report

Read the full shared workspace/log (reconstruct chronological order if it's stored
newest-first) before writing anything — the report must reflect the actual conversation,
not a guess from the prompts you sent. Report to the user:

- What was discussed and the overall outcome (agreement, partial agreement, or
  documented open disagreement — do not force a false consensus).
- **Per-agent path summary**: for each subagent/persona, summarize the distinct path its
  reasoning took through the discussion — its opening position, what it challenged or
  got challenged on, where it changed its mind (and why), and its final position. This
  must show how each agent's reasoning *diverged* from the others, not just repeat what
  each one said in order.
- Each persona's key contributions and how their criticism changed the discussion.
- Agreements vs. unresolved disagreements, clearly separated.
- Conclusions split into confirmed / strong deduction / hypothesis (mirroring the
  criticism labels from Step 5).
- **The ground truth reached**: the actual conclusion(s) the agents converged on (or, if
  they didn't converge, the best-supported position and why consensus wasn't reached).
- Whether the termination condition was actually met, and by whom/how it was declared.
- **Suggested next step(s)**: concrete, actionable follow-up the user should take given
  what the agents concluded (e.g. verify a hypothesis, implement a proposed fix, run a
  benchmark, ask a maintainer) — derived from the discussion's unresolved questions and
  conclusions, not generic advice.
- Basic stats if useful (message counts per agent, duration, whether anyone stalled).

## References

- `references/protocol.md` — shared workspace layout, message format, ordering,
  duplex vs full-duplex mechanics.
- `references/prompting.md` — the three-part subagent prompt structure with templates
  and a worked example.
- `references/termination.md` — time limit vs termination condition, leader
  responsibilities, and the required termination statement format.

## Scripts

- `scripts/collab_log.py` — optional, generic, dependency-free helper for a
  file-based shared workspace when subagents communicate by running shell commands
  against a plain text log. Provides `read` and `send` subcommands, one lock file per
  log file, atomic temp-file-then-rename writes, and monotonically increasing sequence
  numbers with newest-message-first ordering. Only use it if the runtime's subagents can
  actually execute shell commands; otherwise relay messages yourself as described in
  Step 3. Run `python scripts/collab_log.py --help` for usage.
