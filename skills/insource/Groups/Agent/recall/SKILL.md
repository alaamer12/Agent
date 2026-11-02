---
name: recall
description: 'Recall, in two modes, on one rule: report only what you can actually find. Mode A answers "do you remember when I said X?", "did I mention Y?", or /recall <topic> from what is really present - live context, plus past-chat or memory tools when present: open with Yes, No, or Partly, quote the user''s own words verbatim on a Yes, 1-5 lines, never an invented memory. Mode B recovers a conversation that compaction, a lost session, or a new terminal made unavailable: prefer the harness''s own history mechanism over file hunting, locate the session by id, title, date, or distinctive content, inspect the real storage format before parsing, and recover at the requested depth - full fidelity (tool calls, outputs, errors, order) or the discussion - chunking long transcripts on record boundaries. The objective is the ORIGINAL conversation, not a summary or reconstruction; inaccessible sources are stated as limits, not guessed. Escalates A to B when the answer is missing from context but plausibly in an earlier session.'
when_to_use: The user asks whether you remember, recall, or were told something earlier ("do you remember when I said…", "did I mention…", "what did I tell you about…"), or invokes /recall; or context was compacted or the session was lost and the current task depends on earlier decisions, instructions, tool results, errors, or research no longer visible.
argument-hint: "[what you asked earlier, or the session to recover]"
---

# recall

> Report only what you can actually find. **"Not found" is a complete answer** — a plausible memory is not.

Both modes share that spine. Mode A costs seconds; Mode B can cost a lot, so never start it before the cheap
check has failed.

## Pick the mode

| Signal | Mode |
|---|---|
| "Do you remember when I said X?" / "Did I mention Y?" / `/recall the deploy timeout` | **A — answer** |
| Context was compacted, the session closed, or a detail the task depends on is no longer visible | **B — recover** |
| Mode A finds nothing, and the answer plausibly lives in an earlier session | say what you checked, then **B** |
| The user wants a durable fact stored or promoted into `AGENTS.md` | not this skill — the harness's memory skill |

## Mode A — answer from what is actually there

1. **Look before writing.** Search the current conversation for the statement asked about. If the environment
   has a memory or past-chat search capability and the question could be about an earlier session, use it. Do
   not rely on a plausible guess: if you did not find it, you do not remember it.
2. **Classify what you found.**
   - **Yes** — you located the exact statement or instance asked about.
   - **Partly** — you have something related, or the gist, or an approximate version — not the specific detail.
   - **No** — no trace in context or memory.
3. **Reply.** 1 line for a clean Yes/No, up to ~5 when there is real nuance. Never longer. First word is
   **Yes** / **No** / **Partly** (or the natural equivalent in the conversation's language).
   - **Yes** → quote the user's own words **verbatim**, exactly as written — no cleanup, no paraphrase — so they
     can see the recall is real.
   - **Partly** → say plainly what you hold and what is missing. Do not fill the gap.
   - **No** → say so, briefly. No apology padding, no offer to guess.

Hard rules: never fabricate a quote or a memory; the verbatim rule applies only to the user's own past words
(this conversation or a memory tool), never to text you are inventing or a third party's writing; one short
clarifying question at most, and only when two different memories could be the one asked about; no commentary
about the skill itself.

```text
User: "Do you remember when I said I hate mushrooms?"   (found verbatim earlier)
Reply: Yes — you said: "I hate mushrooms, please never suggest them."

User: "Do you recall what I said my job was?"          (only a vague mention)
Reply: Partly. You mentioned working in finance, but never gave the exact job title.

User: "Did I tell you my dog's name?"                  (nothing found)
Reply: No — you haven't mentioned a dog's name in this conversation.
```

## Mode B — recover the original conversation

Full procedure, format notes and chunking rules:
[`references/recovery.md`](references/recovery.md). The short version, in order:

1. **Discover first, then dig.** Identify this harness's built-in history capability (a session-history skill,
   `/resume`, an exported transcript) and prefer it over filesystem hunting. Only fall back to inspecting
   storage — and when you do, determine the layout by looking, not from memory of paths
   (for this harness: [`references/qoder-storage.md`](references/qoder-storage.md), verified 2026-10-23).
2. **Locate the right session.** Prefer the id; otherwise title, date range, distinctive user messages, technical
   details. Grep content *before* parsing. Several plausible matches that matter → ask; never silently pick.
   Derivatives (summaries, compaction snapshots, exported reports, plans) may *lead* to the original — they are
   not substitutes for it.
3. **Read the real format before reconstructing.** Not every record is a visible message; one turn can span
   several records. Preserve original order, the tool-call↔result link, ids and timestamps, and the split between
   original messages and notes. Undecodable, truncated, or missing records are reported, not guessed in.
4. **Pick the depth to the need.** Full fidelity (messages + tool calls + outputs + errors + intermediate steps,
   nothing silently dropped) or the discussion (requests, responses, decisions, unresolved questions). Ask one
   concise question when the request does not already settle it; explicit instructions outrank defaults.
5. **Chunk sequentially** on structural boundaries (complete records for JSONL, heading/code-block-safe points for
   Markdown), track the exact range processed, verify coverage at the end, skip nothing, duplicate nothing.
6. **Sub-agents are the alternative, not the default** — only when parallel range processing clearly saves time or
   the source is too large for one agent. Each gets its own non-overlapping range, the depth, the output format,
   and the duty to keep specifics; the parent merges in original order.

If the source is gone or unreadable, state the limitation and stop. That is the deliverable, not a failure.

## Rules that hold in both modes

- **Evidence before output.** Every claim names where it came from: a line in this conversation, a record index, a
  file. No location → it is `No`, `Partly`, or a labeled limit.
- **The original beats any summary.** A reconstruction dressed as the transcript is the worst outcome of this
  skill, because it is trusted.
- **Precision about scope.** "You never stated a job title" is a fact about the record; "you are an analyst" is a
  guess. Only the first is said.
- **Never leak around the edges.** Recovered transcripts can hold secrets, credentials, and personal data — quote
  the minimum needed to prove the recall, and redact values when relaying.
- **New environment discovered?** Record its layout in `references/` the same way, with a verification date. Do
  not trust remembered paths.

## Boundaries

| Not this | Go instead |
|---|---|
| Keeping durable memories, reviewing them, promoting them into `AGENTS.md` | the harness's memory skill (its `/remember`) |
| writing the project's rules or the instruction file | `agents-md` |
| the inventory of reusable units a task should reuse | `units-md` |
| answering from general knowledge, no memory question involved | just answer, and say it is not from their history |
| proving a past decision was made with evidence | `postmortem` §17 / the project's decision records |

## Files

| Path | Owns |
|---|---|
| [`references/recovery.md`](references/recovery.md) | Mode B in full: discovery order, locating, format inspection, depth choice, chunking, sub-agent briefs, failure limits |
| [`references/qoder-storage.md`](references/qoder-storage.md) | this harness's session layout and verified parse recipes (re-verify after harness updates) |
