---
name: remember-conversation
description: 'Recover a previous conversation after context compaction or loss, when earlier details a task depends on are no longer in the active context, or the user asks to "remember"/"recover" a past session. Discovers how the environment stores conversations (built-in history capabilities before file hunting); locates the session by id, title, date, or distinctive content, distinguishing originals from summaries and derivatives; inspects the real format (JSONL, Markdown transcripts) first; recovers at the needed depth — full fidelity (messages, tool calls+outputs, errors, ordering) or surface-level discussion — with no silent omission; processes long transcripts by sequential chunking on record boundaries, delegating ranges to sub-agents only when it clearly helps. The objective is the ORIGINAL conversation, never an approximate reconstruction or summary of conclusions; inaccessible sources are stated as limits, never invented. Triggers: remember, recover the conversation, resume lost session, context compacted.'
---

# remember-conversation — recover the original, not an approximation

Context compaction, session loss, or a new terminal can make earlier
conversation content unavailable in the active window while the **original
is still stored somewhere**. This skill's job: find that source, understand
its format, and recover it as faithfully as the requested depth requires.

**The objective is to recover the original conversation — never to mistake
a summary, compaction note, or memory-based reconstruction for it.** If the
source is gone or unreadable, state the limitation plainly and stop; do not
invent plausible details to fill the gap.

## When to use

- Context was compacted/partially lost and earlier details matter.
- The agent has lost track of what happened earlier in the session.
- The user asks to remember, recover, reconstruct, or inspect a past
  conversation.
- The current task depends on earlier decisions, instructions, tool runs,
  errors, or research no longer directly visible.
- The agent suspects needed information exists in a prior conversation that
  the current context cannot reliably supply.

First check: **is the conversation actually still accessible?** Accessibility
determines everything — recovery if yes, honest limitation statement if no.

## Step 1 — Discover the environment's recovery mechanisms

Investigate how *this* environment stores conversations instead of
assuming; harnesses differ and the agent must not presume any specific
tool exists. **Inspect existing capabilities before hand-rolling:**

1. Identify the current harness and any built-in session-history capability
   (a `session-history`-style skill, a `/resume` command, an exported
   transcript facility).
2. Check available skills, scripts, commands, utilities, and MCP tools that
   expose conversation data.
3. If a supported mechanism exists, prefer it over manual file hunting or
   format reverse-engineering — it is more reliable.
4. Fall back to filesystem/database inspection only when built-ins are
   absent or insufficient — and then for the current environment, look up
   its documented layout (for this harness: `references/qoder-storage.md`,
   verified paths and parse recipes).
5. New environment discovered? Record its layout in a reference the same
   way — with verification status — rather than trusting memory of paths.

## Step 2 — Locate the correct conversation

Distinguish the target from other stored sessions using available signals:
session id (prefer it — reliable when present), title/summary metadata,
timestamps/date ranges, distinctive user messages, technical details,
project/task association. Grep candidates by content *before* parsing them.

- **Multiple plausible matches and the distinction matters** → ask the user
  which; never silently pick an uncertain session.
- **Derivatives are not the original**: summaries, compaction snapshots,
  context notes, exported reports, and plans may *lead* to the original
  session, but when recovery is requested they are not substitutes for it.

## Step 3 — Inspect and parse the real format

Open the actual source and determine how it encodes the conversation
**before** reconstructing. Formats include JSONL session records, JSON
arrays/objects, Markdown or plain-text transcripts, structured event logs —
examples, not an exhaustive list. Establish the schema:

- how user and assistant messages appear (and that **not every record is a
  visible message** — routing, config, title, and state records coexist;
  one conversational turn may span several records);
- tool calls, their arguments, their results, and how they link;
- ordering signals (timestamps, sequence/uuid + parent links);
- system/developer instructions, attachments, continuation records;
- derived content (compaction summaries) vs original.

Preserve what you recovered: original order (never reorder by topic), the
tool-call↔result relationship, timestamps/ids where relevant, the
distinction between original messages and notes, and identification of
missing, truncated, or malformed records. Undecodable content is reported
as a limitation, not guessed into existence. Partial exports are never
treated as complete conversations.

## Step 4 — Choose the recovery depth

Full-fidelity parsing of a huge session is expensive; match effort to need.
If the user's request doesn't already establish depth, ask one concise
question, e.g.:

> Full detail — including tool calls, outputs, research steps, errors and
> intermediate actions — or mainly the discussion: user messages and agent
> responses with key decisions?

- **Full-fidelity**: recover user/assistant messages, tool calls +
  arguments, outputs, intermediate steps, errors/failed attempts and
  corrections, research queries and sources, in-conversation decisions,
  timestamps/order/references. Do **not** silently drop "repetitive"
  execution detail.
- **Surface-level**: user requests, assistant responses, decisions,
  clarifications, the discussion's evolution, conclusions, unresolved
  questions. Tool detail may be omitted when not needed — but substance is
  still preserved: a detailed discussion must not collapse into a few
  generic conclusions.
- **Explicit instructions outrank defaults**: "complete transcript" never
  gets summarized away; "just the main discussion" never triggers full
  tool-output grinding.

## Step 5 — Process long conversations reliably

**Preferred strategy: sequential, ordered chunking of the original source.**
Divide into consecutive manageable ranges (records 1–500, 501–1000, … —
sizes chosen from the format, record sizes, tool limits, and context
capacity) and per chunk: read the original records; interpret structure;
recover at the chosen depth; keep content concrete (never replace specifics
with generalized summaries); track the exact range processed; continue
without skipping or duplicating; at the end, verify full coverage of the
required range.

Split on **structural boundaries** — complete records for JSONL, heading/
code-block-safe points for Markdown — never arbitrary character positions.

## Step 6 — Sub-agents: alternative, not default

Delegate to sub-agents only when parallel processing materially improves
speed or the source is too large for efficient single-agent work — not
automatically. Each assignment gets (per the sub-agent skill's brief shape):
the source conversation, its **exact non-overlapping range**, the required
depth, the output format, the demand to preserve concrete details and
references, and any boundary context needed to interpret the range — plus a
little adjacent context where a turn spans chunk edges. Dispatch in
background where that convention exists; the parent merges the chunk reports
in original order and reconciles overlaps itself.

## Final principle

> Recover the original conversation as faithfully as the user requires.
> Prefer direct, sequential inspection of the source, use existing recovery
> capabilities when available, and never mistake a summary or an incomplete
> reconstruction for the complete conversation.
