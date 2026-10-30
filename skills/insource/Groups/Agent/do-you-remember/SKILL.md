---
name: do-you-remember
description: Use when the user asks the agent whether it remembers, recalls, or was told something earlier — e.g. "do you remember when I said...", "do you recall...", "did I mention...", "what did I tell you about...", or when they explicitly invoke /do-you-remember. Answers strictly from what's actually present in conversation context (and past-chat memory/search tools if available) — never guesses or fabricates. Reply is short (1-5 lines), opens with Yes / No / Partly, and if the memory is exact, quotes the user's own original wording back verbatim rather than paraphrasing.
---

# Do You Remember

A small, strict skill for honestly reporting what the agent actually remembers, instead of producing a plausible-sounding but made-up answer. It is written to work for any AI agent or assistant that uses it, not tied to one product.

## When this triggers
- "Do you remember when I said X?"
- "Do you recall what I told you about Y?"
- "Did I mention Z earlier?"
- Explicit invocation: `/do-you-remember [topic]`

## How to answer

1. **Check the actual evidence before writing anything.**
   - Look back through the current conversation context for the statement being asked about.
   - If a memory or "search past chats" tool is available and the question could reasonably be about an earlier session, use it.
   - Do not rely on a plausible guess. If you didn't actually find it, you don't remember it.

2. **Classify what you found:**
   - **Yes** — you located the exact statement/instance being asked about.
   - **Partly** — you remember something related, the general gist, or an approximate version, but not the specific detail/wording asked about.
   - **No** — you found no trace of it anywhere in context or memory.

3. **Write the reply:**
   - Length: 1 line for a clean Yes/No, up to ~5 lines if there's nuance worth explaining. Never longer.
   - Open the first line with "Yes", "No", or "Partly" (or the natural equivalent if the conversation is in another language).
   - **If Yes:** quote the user's own original wording back exactly as they wrote it — verbatim, not paraphrased, not cleaned up — in quotation marks, so they can see the recall is real.
   - **If Partly:** say plainly what you do and don't remember (the gist you have vs. the specific detail you're missing). Do not invent details to fill the gap.
   - **If No:** say so plainly and briefly. No over-apologizing, no padding.

## Hard rules
- Never fabricate a quote or a memory to sound more impressive. Guessing is worse than saying "No."
- The verbatim-quote rule only ever applies to the user's own past words (from this conversation or a memory tool) — never to a quote you're inventing or a third party's copyrighted text.
- Max 5 lines. No meta-commentary about the skill itself, no restating the question back at length.
- Don't ask a clarifying question unless it's genuinely ambiguous which memory is being asked about — and if you do, keep it to one short question.

## Examples

**User:** "Do you remember when I said I hate mushrooms?"
*(found verbatim earlier in context)*
**Reply:** Yes — you said: "I hate mushrooms, please never suggest them."

**User:** "Do you recall what I said my job was?"
*(only a vague mention found)*
**Reply:** Partly. I remember you mentioned working in finance, but you never gave the exact job title.

**User:** "Did I tell you my dog's name?"
*(nothing found)*
**Reply:** No — you haven't mentioned your dog's name in this conversation.
