---
name: explain
description: Explain things in the easiest way to understand, defining any heavy or technical word the moment it's used — e.g. "zero-day (a security flaw nobody has fixed yet)". Use this whenever the user asks you to explain, simplify, clarify, break down, or "explain like I'm new to this", or says a previous answer was too technical, confusing, full of jargon, or hard to follow. Also use it proactively whenever your own answer is about to use a specialized or industry-specific term (security, finance, medicine, law, engineering, programming, etc.) and the user hasn't signaled expert familiarity with that field.
---

# Explain

## Why this exists

The gap between an expert explanation and a clear one is almost never about the ideas — it's about the words. A correct, complete answer can still fail the reader if it's built out of terms they have to stop and look up. This skill's job is to close that gap: say the true thing, but say it so a smart, motivated person with no background in the topic can follow it on the first read.

This is not "dumbing down." Nothing gets less accurate. The technical term is usually still there — it's just never left to stand alone. The skill is deciding, sentence by sentence, whether a word is going to cost the reader something, and paying that cost for them instead of passing it on.

## The core technique: inline definitions

The moment a heavy word appears, define it right there, briefly, in the same breath — don't make the reader wait for a glossary, a footnote, or a "we'll get to that later."

**Pattern:** `term (plain-language meaning)` — a few words, not a paragraph, dropped in right after the term appears.

> A zero-day (a security flaw nobody has fixed yet) is especially dangerous because...

> The system uses OAuth (a way to log in using an account you already have, like Google or GitHub) instead of...

> Her contract has a non-compete clause (a rule stopping her from working for a rival company for some time after she leaves).

Keep the inline definition to one short phrase or clause — just enough that the reader doesn't need to stop and search. If a term genuinely needs more than that to land, define it briefly inline first, then expand in the next sentence with an example or analogy. Never let the deep-dive version replace the quick one; the quick one is what keeps the reader moving.

### What counts as a "heavy word"

A term is worth defining if a reasonably curious adult outside that field would plausibly not know it on sight. Use judgment, calibrated to two things:

1. **The field, not just the word.** Jargon is heavy by default in the field it comes from (a term is more likely to need defining in security, finance, medicine, law, or engineering than in everyday cooking or sports, where the same reader has more built-in context).
2. **What the person has already shown they know.** If they used the term first, or the conversation shows real fluency in the topic, don't define it — that reads as condescending. Calibrate up for evident experts, down for evident beginners, and default to defining when unsure — a quick aside costs an expert nothing, but skipping it can lose a beginner completely.

Don't define: everyday words, terms the person already used unprompted, or a term you just defined a few sentences ago in the same answer (define once per term per answer, not every repetition).

Do define: acronyms and initialisms, domain-specific jargon, "insider" shorthand, numbers or units without context (e.g. what a given latency number actually means for the user), and any word doing real technical work in the sentence.

## Other moves that make explanations easy to follow

Inline definitions solve the vocabulary problem. These solve the structure problem — use them alongside inline definitions, not instead of them.

- **Short sentences.** One idea per sentence. If a sentence needs a semicolon or three commas to hold together, split it.
- **Concrete before abstract.** Lead with a plain-language example or a real-world analogy, then generalize — not the other way around. "A firewall is like a security guard that checks everyone at the door" lands before "a firewall filters network traffic based on rules."
- **Active voice.** "The server rejects the request" beats "the request is rejected by the server" — active voice keeps the actor visible and the sentence shorter.
- **Say the most important thing first.** Don't make the reader wade through setup to find the point.
- **One term per concept.** Don't call the same thing by two different names in one answer (pick "user" or "customer," not both) — switching names makes the reader wonder if you mean something different.
- **Use headings and short paragraphs for longer explanations**, so the reader can scan and re-find things, not just read linearly.

## What NOT to do

- Don't strip out the real term and replace it with only the plain version — the reader still needs the correct word if they're going to look things up later, ask a follow-up, or talk to someone else about it. Give both: the term *and* its meaning, together.
- Don't write a separate "Glossary" section that dumps every term at the end — by the time the reader gets there they've already stumbled past the words they didn't know. Define at first use, inline.
- Don't over-explain terms the person clearly already knows — that reads as talking down to them, not as helpful. Match the explanation to the reader, not to a fixed floor of simplicity.
- Don't pad the definition into a mini-lecture. One short phrase is usually enough; save the fuller explanation for if they ask a follow-up.

## Quick example

**Before (unexplained):**
> The API returns a 429 if you exceed the rate limit, so implement exponential backoff with jitter.

**After (this skill applied):**
> If you send requests too fast, the API replies with a 429 error (a standard code meaning "you're sending too many requests, slow down"). The fix is exponential backoff (waiting a little longer before each retry, doubling the wait time each time you fail) with jitter (adding a small random delay so many clients don't all retry at the exact same moment).
