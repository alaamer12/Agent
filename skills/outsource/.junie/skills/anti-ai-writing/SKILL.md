---
name: anti-ai-writing
description: 22 anti-AI writing rules for any prose a person other than the author will read (emails, posts, decks, reports, CVs). Applies an audience test first; internal notes and docs are exempt. Use when drafting, rewriting, or polishing human-facing text, or when asked to "de-AI" a draft.
---

# Anti-AI Writing

AI-generated prose sounds like AI. People can tell. The tells: perfect grammar, hollow enthusiasm, filler phrases, predictable structure, and a voice that sounds like everyone and no one. If someone reads your draft and thinks "a robot wrote this," the artifact takes a hit and so does your credibility.

These rules are format-neutral: the same whether the artifact is a cold email, a deck, an HTML dossier, or a workshop handout.

## When this fires

The test is one question: **will a person who is not the author read this prose?**

If yes, every rule below applies. If the only readers are the author, Claude, or another LLM, none of them do. Internal docs want density and structure. A de-AI pass tuned for human-facing prose actively degrades them.

Two anchors resolve most cases without thinking:

| Always external (rules fire) | Always internal (rules stay off) |
|---|---|
| Emails, messages, outreach of any kind | Personal notes, journals, scratch files |
| Posts, articles, newsletters | Internal wikis and knowledge-base docs |
| Decks, one-pagers, memos, reports a named person receives | Project ledgers, planning docs, TODO lists |
| CVs, cover letters, application material | Prompts, agent instructions, LLM handoffs |
| Teaching and workshop material | Code comments, commit messages, changelogs |

**These are anchors, not a list.** Most artifacts aren't in either column. When the artifact isn't named above, ask the question, don't look for a match. Path and folder are evidence, never the test: a workshop deck saved in a personal-notes folder is still read by an audience, so the rules fire on it. An internal doc pasted into an outbox folder is still an internal doc.

**When you genuinely cannot tell who reads it, ask the author in one line before drafting.** Don't guess and don't split the difference.

---

## The Rules

### Rule 1: Kill the Filler
Delete these on sight:

| AI Filler | Why It's Bad |
|-----------|-------------|
| "I hope this message finds you well" | Nobody talks like this. It's a signal you have nothing real to say. |
| "I wanted to reach out because..." | Just say the thing. |
| "I'd love to connect" | Vague. Connect about what? |
| "Please don't hesitate to..." | Formal padding. |
| "I trust this email finds you in good spirits" | You don't. |
| "Per our previous conversation" | Say "like we talked about" or just reference the topic. |
| "I'm excited to..." | You're probably not. |
| "Moving forward" / "Going forward" | Delete. The reader knows time moves forward. |
| "Just circling back" | Say "following up on X". Be specific. |
| "Hope you're doing well!" | Only if you actually care and follow up on the answer. Otherwise cut it. |

### Rule 2: Start With the Point
First sentence = why you're writing. No wind-up. No context-setting preamble.

- Bad: "Hi John, I hope you're having a great week. I was thinking about our conversation at the conference last month, and I wanted to follow up on something you mentioned about..."
- Good: "John, you mentioned the Series B is closing in March. Still looking for introductions to LP networks?"

### Rule 3: Write How You Talk
Read it out loud. If it sounds like a press release, rewrite it. Real people use:
- Contractions (I'm, don't, can't, wouldn't)
- Sentence fragments (sometimes)
- Commas or a full stop instead of semicolons (never an em-dash, see Rule 8)
- Short paragraphs: 1-2 sentences in a message, one idea per paragraph in anything longer
- Lowercase where it feels natural (especially on WhatsApp/text)

### Rule 4: One Thought At A Time
Don't stack asks. One point per message, one argument per piece, one point per section.

In a message this is literal: three asks get you one answer, because people respond to the last thing they read and ignore the rest. Longer prose has many thoughts by construction, so the unit is the section rather than the whole artifact. The piece still argues one thing.

If you have multiple things to discuss, lead with the most important one.

### Rule 5: Imperfection Is Credibility
A slightly informal, slightly imperfect message reads as human. A polished, perfectly structured message reads as AI or mass-produced. This doesn't mean be sloppy. It means don't over-polish.

### Rule 6: No Emoji Walls
One emoji is fine for tone. Three is a birthday card. Zero is often best in professional contexts.

### Rule 7: End With Something Specific
- Bad: "Let me know what you think!"
- Bad: "Looking forward to hearing from you."
- Good: "Free for 20 min Thursday or Friday?"
- Good: "Want me to send over the deck?"

### Rule 8: No Em-Dashes
The em-dash (—) is the single biggest AI tell right now. Don't use it. Not in emails, not in messages, not anywhere audience-facing.

Use instead:
- A full stop. Two short sentences beat one em-dash splice.
- A comma, when the clauses are tight.
- Parentheses, for a genuine aside.
- A colon, to introduce a list or a payoff.

Spaced hyphens ( - ) are starting to read as AI too. Default to a period. If a "—" shows up in a draft, delete it and re-punctuate.

### Rule 9: Kill the Antithesis Tic (and its cousins)
"It's not just X, it's Y." "Not only X, but Y." "This isn't about X, it's about Y." "Can X but can't Y." These negation-then-pivot and contrast-seesaw lines are pure AI cadence. Detectors key on the formulations themselves, and they survive word swaps intact. Say the point once, positively.

- Bad: "This isn't a monitoring tool, it's a trust layer."
- Good: "It measures the network so institutions don't have to take one operator's word for it."

Other tells to delete on sight:

| Tell | Fix |
|------|-----|
| Rule-of-three triads ("fast, reliable, and scalable") | Keep the one that matters. |
| "In today's..." / "In the world of..." openers | Cut it. Start with the point (Rule 2). |
| "It's worth noting that" / "It's important to note" | Just note it. |
| "delve", "leverage", "robust", "seamless", "landscape", "realm", "deeper" | Plain words: dig into, use, solid, smooth, market, area, more. |
| "game-changer", "unlock", "elevate", "supercharge" | Overclaim. Say what it actually does. |
| "crown jewels" | Name the actual asset. The metaphor hides what you mean. |
| "pivotal" | Plain word: key. Or cut it. Most things aren't. |
| "underscores" | Plain word: shows. |
| "moreover" | Delete. The next sentence doesn't need a runway. |
| "furthermore" | Delete. Same tell as "moreover". |
| Closing on "Ultimately" / "In conclusion" | End on the specific ask (Rule 7). |
| Title Case Headings / "The Power of X: Why Y Works" colon-titles | Sentence case. Say what the section is about. |
| Fractal summaries: "In this section we'll..." / "...as we've seen" | Delete every preview and recap. The reader just read it. |
| Prompt echo: "This essay will explore..." | Delete. Start exploring. |
| `utm_source=chatgpt.com` (or any AI tool) in pasted URLs | Strip the tracking params. This one outs the whole draft. |

### Rule 10: Name the Source or Cut the Attribution
"Experts believe." "Studies show." "Research suggests." "Industry leaders agree." If you can't name the expert, the study, or the leader, the attribution is doing nothing except borrowing authority you don't have.

- Bad: "Studies show most validators underperform after year one."
- Good: "NodeWatch's 2025 operator report put first-year effectiveness at 94.2%, against 97.1% past year two." (Invented example: name a real, checkable source.)
- Also good: "Most validators get worse after year one." (No source beats a fake one.)

### Rule 11: Use "Is" and "Has"
AI dodges plain verbs. It writes "serves as", "features", "boasts", "presents", "represents" where a person writes "is" or "has". The fancy verb is press-release reflex, not precision.

| Instead of | Write |
|------------|-------|
| "The report serves as a summary of..." | "The report summarizes..." |
| "The tool features three modes" | "The tool has three modes" |
| "Barcelona boasts a strong startup scene" | "Barcelona has a strong startup scene" |
| "This represents a shift in..." | "This is a shift in..." (or cut it, see Rule 16) |

Keep the specific verb only when it carries meaning "is" can't.

### Rule 12: Repeat the Right Word
AI rotates synonyms to dodge repetition: "developers... engineers... practitioners... builders", all in one paragraph, all meaning the same thing. Real writers repeat the clearest word.

If a noun is the right word three times in a paragraph, use it three times. Forced variation reads as thesaurus abuse, and it makes the reader stop to work out whether the four words mean four different things.

### Rule 13: No Bold Headers on Bullet Items
The shape: every bullet opens with a bold label that then repeats itself.

- Bad: "**Performance:** Performance improved by 40%."
- Good: "Performance improved by 40%."

Strip the label and write the point. If the items genuinely need headers to make sense, they aren't bullets. They're paragraphs.

### Rule 14: One Hedge, Not Two
"Could potentially create." "May eventually unlock." "Might ultimately transform." Either word alone is fine. Stacked, they cancel out, and the sentence asserts nothing while sounding careful.

Pick one. If you mean "could create", say that. If you mean "potentially creates", say that. Both together is filler.

Carve-out: stacked hedges are style. Factual caveats are information. This rule kills the first and protects the second.

"Unconfirmed", "reported", "unaudited", "estimate", "as of March", "single-source": these label what you know and how well you know it. Keep every one intact, in every version of the artifact. A de-AI pass may never strip a caveat off a research dossier or a financial doc. Voice is not a licence to overclaim. When a sentence reads hedged because the fact is genuinely uncertain, the hedge stays.

### Rule 15: Earn the Number
"Three key takeaways." "Five things to know." "Here are the top seven." AI reaches for numbered lists because they're structurally safe, then pads to hit the number.

Use a numbered list only when the content actually has that many discrete, parallel items. If you're stretching to reach the number, the list shouldn't exist. Two real points beat five with three invented.

### Rule 16: Cut the "-ing" Glosses
Strings of present participles doing pseudo-analysis: "symbolizing the region's commitment to progress, reflecting decades of investment, and showcasing a new era of collaboration." They say nothing.

The same move shows up without the "-ing": "this represents a broader shift", "the decision symbolizes a commitment to excellence", "it speaks to a larger trend in the industry". If the significance is real, show the consequence. Otherwise cut the sentence.

- Bad: "The partnership reflects a growing focus on validator transparency."
- Good: "Since the partnership, the operator publishes per-client effectiveness monthly. Nobody else in the sector does."

### Rule 17: Never Ship a Placeholder
`[Your Name]`, `[INSERT SOURCE URL]`, `[Describe the specific section]`, `2025-XX-XX`, `<!-- add citation -->`. A visible placeholder is proof the draft was pasted without editing. It's the most expensive tell on this list: it costs the reader's trust in one glance.

Before sending, search the draft for `[`, `XX`, and `TODO`. Fill it in or delete the sentence. Never send a draft with a slot still open.

### Rule 18: Colon, Not Period, on Bullet Labels
When a bullet leads with a short label, AI ends the label with a period and runs the explanation as a separate sentence. A person writes a colon. The colon reads as "here's what this label means". The period reads as a sentence, which the next clause then contradicts by continuing.

- Bad: "**Intros.** Years of conferences and operator network."
- Good: "**Intros:** years of conferences and operator network."

Fix the period to a colon and lowercase the start of the gloss, or drop the label and write the point as a plain sentence. The unbolded form is the same tell: "- Intros. Years of conferences and operator network."

Carve-out: when the label is a full sentence on its own rather than a label introducing a gloss, the period is correct. For the unbolded form, only flag a leading fragment that is clearly a label (a 1-4 word noun phrase, no verb). A short complete sentence opening a bullet is fine.

### Rule 19: No Bold-for-Emphasis in Prose
Bolding words or phrases mid-sentence to add emphasis is an AI tell: **the key insight**, **critically**, **this changes everything**. A person writing an email or a paragraph almost never reaches for bold; the sentence itself carries the weight. If a word needs bold to feel important, rewrite the sentence so it doesn't.

- Emails and messages: no bold anywhere, ever. Many mail pipelines are plain text, and bold markup arriving as literal asterisks is worse than the tell.
- Docs, decks, and reports: bold stays structural only (headings, table headers, defined labels per Rule 18). Never decorative, never mid-prose emphasis.
- This extends Rule 13 (no bold headers on bullets) from bullets to all running prose.

### Rule 20: Vary the Rhythm (burstiness)
AI writes uniform 15-20-word sentences in rectangular paragraphs, and detectors and readers both key on it. Force a spread: at least one sentence of 6 words or fewer, at least one of 25+, paragraphs of visibly different lengths, and at most one single-line paragraph per piece. "X is A. X is B. X is C." staccato runs get merged into one sentence or reframed.

Read the draft's shape before its words. If every paragraph is the same height, the rhythm is the tell, whatever the vocabulary.

### Rule 21: Commit (kill uniform positivity)
AI text measures dramatically more certain and more positive than human text, and it auto-balances every claim with its counterpoint. Both are tells. Take a side and stay there; let one thing be annoying, unresolved, or mildly disappointing. A piece where everything is upbeat and every claim gets a "however" reads machine-made even with perfect vocabulary.

This is the style-side complement of Rule 14's carve-out: genuine factual caveats stay; reflexive both-sidesing goes.

### Rule 22: Concrete Beats Abstract
If the first three sentences evoke nothing you can picture, inject a thing, place, number, or name. "A client" / "a tool" / "a city": name it. Numbers get texture: $43, 11 months, 4:30am, v2. Not "significant savings" or "recently". Invented example people are a tell of their own (AI defaults cluster on Emily/Sarah); use real names or none.

---

## The de-AI pass itself

The meta-test is information density: in human writing every word has intention behind it; AI text reads empty even when polished (it's what Pangram's Max Spero checks before running any detector). If a sentence would survive deletion with nothing lost, delete it.

Fixes that fail (don't do these when humanizing a draft):

- Thesaurus-swapping every flagged word. Weird synonyms read as AI-plus-effort.
- Scattering random typos. Errors must read as casualness, never carelessness, and only where the register tolerates them.
- Scrubbing personality along with the tells. A flat, tell-free text is still AI-shaped. The goal is voice, not absence.
- Shrinking every long sentence. Humans write long sentences; they just don't write only 18-word ones.
- Inventing facts, stats, or quotes to sound specific (Rule 10 still governs).
- Word-level scrambling that leaves sentence shapes alone. The FT tested a humaniser: the output was less polished but the rule-of-three and "can X but can't Y" formulations survived untouched, plus a new rambling run-on. Detectors match word placement, frequency, and sentence/paragraph patterns in combination, so changing a few words beats nothing. Rewrite the structure (break the triad, kill the seesaw, vary the rhythm) or don't bother.

Human markers worth adding (sparingly, where the voice supports them): a parenthetical aside with attitude; one "honestly" / "I think" / "to be fair"; a sentence starting with And, But, or Because; a mild complaint or unresolved edge; an irrelevant-but-true detail in an anecdote; a dropped Oxford comma in casual registers; uneven list items.

---

> **Provenance.** This is a versioned export (v1.2, 2026-09-01) of a privately maintained canonical file. Rules 10-18 are adapted from [avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing) by Conor Bronsdon (MIT), reworded. Deliberately not imported from upstream: its Node scorer (this is a rules file, not a detector) and its ChatGPT-only citation fingerprints (`citeturn0search0`, `oai_citation`), which never fire on Claude output. v1.1 added Rules 19-22, the de-AI-pass section, and four Rule 9 rows (Title Case, fractal summaries, prompt echo, utm_source), distilled from Ruben Hassid's "How to bypass AI detectors" (X Article, 2026-07-23); its certainty/positivity figures are the article's, unverified. v1.2 adds "can X but can't Y" and "deeper" to Rule 9, the information-density meta-test, and the humaniser/structure lesson in the de-AI pass, distilled from "Did AI write this? It's getting harder to tell" (Elaine Moore, Financial Times, 2026-08-29).
