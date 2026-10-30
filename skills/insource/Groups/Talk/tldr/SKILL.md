---
name: tldr
description: Answer in the shortest honest form instead of the usual full explanation — a word, a phrase, or one short sentence, with no preamble, hedging, or recap of what was done. Use this whenever the user says "tldr", "tl;dr", asks you to be brief, asks for a short answer, a one-word answer, "just tell me yes or no", "in short", "sum it up", or reacts to a normal-length reply with something like "too long", "just answer", "shorter", or "get to the point." Also use it any time the user is clearly asking a plain yes/no/status/confirmation question about something already discussed ("does this work now?", "did that fix it?", "is it done?") and a short answer would fully satisfy them — even without the word "tldr." Always trigger this even if the user's phrasing is casual or in a language other than English.
---

# TL;DR

Say the important part. Nothing else.

## What this skill does

Normally Claude tends to explain: what it did, why, what changed, what to watch for. This skill turns that off. The user wants the answer, not the tour. Give them the destination, not the route.

## How to answer

1. **Find the one thing the user actually needs to know.** Usually it's: yes/no, a number, a name, "done," "not yet," or one short clause. If the honest answer really is one word, use one word.
2. **Cut everything else.** No "I checked and it looks like...", no recap of the steps you took, no "let me know if you have questions," no restating the question back. Don't soften a short answer by wrapping it in a sentence it doesn't need.
3. **Use plain, current, everyday words.** Say "fixed" not "resolved the underlying issue." Say "yes" not "affirmative" or "indeed." Say "won't work" not "is not viable." No jargon or formal/legacy phrasing unless the user themselves just used that term — match their words, don't upgrade them.
4. **Stay honest — always.** Short is not the same as agreeable. If the real answer is "no," "not yet," "it's broken," or "I'm not sure," say that plainly. Never trim a "no" into something that reads like a "yes." Never round up. The whole point of this skill is a true answer stripped down, not a comfortable one.
5. **If the honest answer really is "yes and no," say exactly that — don't blur it into "kind of," "sort of," or "mostly."** These are different answers and mean different things. "Kind of" means the situation itself is partial or unclear. "Yes and no" means two separate, fully true things are both the case at once (e.g., yes it's fixed, but no it's not deployed yet). Pick the one that's actually true — don't default to the soft, vague version because it feels safer or shorter. A real "yes and no" answer keeps both halves clear, each stated fully, not watered down toward the middle.
6. **Add one clause of detail only if the short answer would otherwise mislead.** Example: "yes, but only after a restart." Keep it to a handful of words tacked onto the short answer — not a second sentence, not a new paragraph.
7. **If genuinely nothing needs adding, stop after the short answer.** Don't pad to make the reply feel complete. A one-word reply is a full reply here.

## Examples

**Example 1**
User: does this work now?
Full-length instinct: "Yes — I fixed the null check in the validation function, so now when the form submits with an empty field it shows the error message instead of crashing. You should be good to go."
TL;DR answer: **Yes.**

**Example 2**
User: tldr did the tests pass
Full-length instinct: "I ran the test suite and 42 out of 45 tests passed. The 3 that failed were related to the timeout config, which I think is a separate pre-existing issue unrelated to your change."
TL;DR answer: **Not all of them — 3 failed, looks unrelated to your change.**

**Example 3**
User: is the bug fixed or not, just tell me
Full-length instinct: "I looked into it and made some changes to the retry logic, but I wasn't able to fully reproduce the original issue in my testing, so I can't say for certain it's fixed."
TL;DR answer: **Not confirmed — couldn't reproduce it to check.**

**Example 4**
User: sum up what we decided
Full-length instinct: a five-bullet recap of the whole conversation.
TL;DR answer: **Ship the Redis fix Friday, hold the API change for next sprint.**

**Example 5 — a real "yes and no"**
User: tldr is the feature done
Full-length instinct: "The core functionality is fully implemented and working correctly, but I haven't added it to the production deploy pipeline yet, so it's not live for users."
TL;DR answer: **Yes and no — the code's done, but it's not deployed yet.**
(Not "kind of done" — the code itself is fully, not partially, finished. Two separate true things, both stated.)

## What NOT to do

- Don't say "the short answer is..." or "TL;DR:" as a prefix — just give the short answer.
- Don't apologize for brevity or explain that you're being brief.
- Don't offer to elaborate unless the user asks — that's still padding.
- Don't turn a "no" into "not exactly" or "sort of" just to soften it.
- Don't turn a genuine "yes and no" into "kind of" or "mostly" — say both halves plainly instead of blending them.
- Don't reach for formal or old-fashioned words when a plain modern one says the same thing.
