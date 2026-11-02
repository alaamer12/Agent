# Recovery procedure (Mode B, in full)

For recovering a conversation that is no longer in the active context. Read this when the cheap check failed and
the original may still exist in storage. The objective is the **original** conversation — never a summary,
compaction note, or approximate reconstruction.

## Contents
- Step 1 — Discover the environment's recovery mechanisms
- Step 2 — Locate the correct conversation
- Step 3 — Inspect and parse the real format
- Step 4 — Choose the recovery depth
- Step 5 — Process long conversations reliably
- Step 6 — Sub-agents: alternative, not default
- Failure and limits

## Step 1 — Discover the environment's recovery mechanisms

Investigate how *this* environment stores conversations instead of assuming; harnesses differ and no specific tool
may exist. Inspect existing capabilities before hand-rolling:

1. Identify the current harness and any built-in session-history capability (a `session-history`-style skill, a
   `/resume` command, an exported-transcript facility).
2. Check available skills, scripts, commands, utilities, and MCP tools that expose conversation data.
3. If a supported mechanism exists, prefer it over manual file hunting or format reverse-engineering — it is more
   reliable.
4. Fall back to filesystem/database inspection only when built-ins are absent or insufficient — and then look up
   the *documented* layout for that environment (for this harness: [`qoder-storage.md`](qoder-storage.md), with
   verified paths and parse recipes).
5. New environment discovered? Record its layout in a reference the same way — with verification status — rather
   than trusting memory of paths.

## Step 2 — Locate the correct conversation

Distinguish the target from other stored sessions using whatever signals exist: **session id** (prefer it — reliable
when present), title/summary metadata, timestamps or date ranges, distinctive user messages, technical details,
project or task association. Grep candidates by content *before* parsing them.

- **Multiple plausible matches and the distinction matters** → ask the user which; never silently pick an uncertain
  session.
- **Derivatives are not the original.** Summaries, compaction snapshots, context notes, exported reports and plans
  may *lead* to the original session. When recovery is requested, they are not substitutes for it.
- **Titles drift.** A session's title can describe its first topic; verify by content.

## Step 3 — Inspect and parse the real format

Open the actual source and determine how it encodes the conversation **before** reconstructing. Formats include
JSONL session records, JSON arrays/objects, Markdown or plain-text transcripts, structured event logs — examples,
not an exhaustive list. Establish the schema:

- how user and assistant messages appear — and note that **not every record is a visible message**: routing,
  config, title, and state records coexist with them, and one conversational turn may span several records;
- tool calls, their arguments, their results, and how they link to each other;
- ordering signals (timestamps, sequence/uuid plus parent links) — do not trust file order alone;
- system/developer instructions, attachments, continuation records;
- derived content (compaction summaries) versus original.

Preserve what you recovered: original order (never reorder by topic), the tool-call↔result relationship,
timestamps and ids where relevant, the distinction between original messages and notes, and an identification of
missing, truncated, or malformed records. Undecodable content is reported as a limitation, not guessed into
existence. Partial exports are never treated as complete conversations.

## Step 4 — Choose the recovery depth

Full-fidelity parsing of a huge session is expensive; match effort to need. If the request does not already
establish depth, ask one concise question:

> Full detail — including tool calls, outputs, research steps, errors and intermediate actions — or mainly the
> discussion: user messages and agent responses with key decisions?

| Depth | Recover | Notes |
|---|---|---|
| **Full fidelity** | user/assistant messages, tool calls + arguments, outputs, intermediate steps, errors and failed attempts, corrections, research queries and sources, in-conversation decisions, timestamps/order/references | Do **not** silently drop "repetitive" execution detail — it is usually where the mechanism lives |
| **Surface-level** | user requests, assistant responses, decisions, clarifications, how the discussion evolved, conclusions, unresolved questions | Tool detail may be omitted when not needed — but substance is still preserved: a detailed discussion must not collapse into a few generic conclusions |

**Explicit instructions outrank defaults:** "complete transcript" never gets summarized away; "just the main
discussion" never triggers full tool-output grinding.

## Step 5 — Process long conversations reliably

**Preferred strategy: sequential, ordered chunking of the original source.** Divide into consecutive manageable
ranges (records 1–500, 501–1000, … — sizes chosen from the format, record sizes, tool limits, and context capacity)
and per chunk: read the original records; interpret structure; recover at the chosen depth; keep content concrete
(never replace specifics with generalized summaries); track the exact range processed; continue without skipping or
duplicating. At the end, verify full coverage of the required range.

Split on **structural boundaries** — complete records for JSONL, heading/code-block-safe points for Markdown — never
arbitrary character positions. Record the count consumed per range so the boundaries are provable.

## Step 6 — Sub-agents: alternative, not default

Delegate only when parallel processing materially improves speed, or the source is too large for efficient
single-agent work — not automatically. Each assignment gets, in the shape the sub-agent skill requires: the source
conversation, its **exact non-overlapping range**, the required depth, the output format, the demand to preserve
concrete details and references, and a little adjacent context where a turn spans a chunk edge. Dispatch in
background where that convention exists. The parent merges the chunk reports **in original order** and reconciles
overlaps itself; a worker's summary is not the transcript.

## Failure and limits

Report, do not improvise:

| Situation | What to say |
|---|---|
| No storage mechanism found and no accessible files | the source is unavailable; state what you checked |
| Files exist but the format is undecodable | the format could not be parsed; show the sample line and the schema you could not resolve |
| Only a derivative survives (a summary, an export) | recovered the derivative, explicitly *not* the original, and name what is lost |
| Partial export or truncated records | recovered range X–Y of Z; these records are missing or cut |
| Secrets or personal data in the recovered text | quote the minimum that proves the point; redact values |
