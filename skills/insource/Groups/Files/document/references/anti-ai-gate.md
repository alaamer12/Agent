# Anti-AI Gate (De-AI Prose Rules)

When drafting, rewriting, or rephrasing prose that a human other than the author will read, apply this gate.
AI-generated prose has unmistakable tells: hollow enthusiasm, filler phrases, predictable cadence, and generic corporate voice. This gate enforces authentic, human cadence while preserving information density and factual claims.

## The Audience Test
The gate fires based on one question: **Will a person who is not the author read this prose?**

| Always external (gate applies) | Internal / Developer notes (gate stays off) |
|---|---|
| Emails, outreach messages, pitches | Personal scratch notes, journals |
| Articles, blog posts, newsletters, guides | Internal architecture wikis, technical notes |
| Decks, reports, memos, public product docs | Project ledgers, planning docs, TODOs |
| CVs, cover letters, application material | Prompts, agent specs, instructions |
| Workshop, training, and client deliverables | Code comments, commit messages, schemas |

---

## The Anti-AI Rules

### 1. Kill the Filler
Delete boilerplate openings and empty courtesies:
- Cut: "I hope this message finds you well", "I wanted to reach out because...", "I'd love to connect", "Please don't hesitate to...", "Moving forward", "Just circling back".
- Rule: Just state the point directly.

### 2. Start With the Point
First sentence = reason for writing. Zero context-setting wind-up.

### 3. Write How You Talk
Read out loud. If it sounds like a synthetic press release, rephrase:
- Use natural contractions (`I'm`, `don't`, `can't`, `wouldn't`).
- Use commas or a period rather than semicolons.
- Keep paragraphs short (1–3 sentences).

### 4. One Thought At A Time
Do not stack competing asks or arguments. One main point per message/section.

### 5. Imperfection Is Credibility
Slightly informal and concise reads human. Over-polished, perfectly symmetrical structure screams machine generation.

### 6. No Emoji Walls
Zero emojis in formal documents; at most one for tone in casual messaging. Never bullet with emojis.

### 7. End With Specifics
- Bad: "Let me know what you think!" / "Looking forward to hearing from you."
- Good: "Free for 15 min Thursday?" / "Want me to send the updated spec?"

### 8. No Em-Dashes (—)
The em-dash is the number one tell in modern LLM output. Never use it in audience-facing prose.
- Replace with a period (two crisp sentences).
- Replace with a comma (tight clauses).
- Replace with parentheses (genuine aside).
- Replace with a colon (introducing a list or payoff).

### 9. Kill the Antithesis Tic and Stock Words
Avoid contrast-seesaw cadences:
- Cut: "It's not just X, it's Y", "Not only X, but Y", "This isn't about X, it's about Y", "Can X but can't Y". State the truth once, positively.
- Eliminate banned stock AI words:
  - *delve, leverage, robust, seamless, landscape, realm, deeper, game-changer, unlock, elevate, supercharge, pivotal, underscores, moreover, furthermore*.
  - Rule-of-three triads ("fast, reliable, and scalable" -> keep the single trait that matters).
  - Openers like "In today's fast-paced world..." -> delete.
  - Fractal recaps ("As we've seen...", "In this section we will explore...") -> delete.
  - Colon title clichés ("The Power of X: Why Y Matters") -> use plain sentence case.

### 10. Name the Source or Cut Attribution
Never write "Studies show", "Experts agree", or "Research suggests" without naming the specific study, author, or organization. If you cannot name the source, state the claim plainly or drop it.

### 11. Plain Verbs ("Is" and "Has")
AI reaches for grandiose verbs where humans write simple ones:
- Replace "serves as a summary of" with "summarizes".
- Replace "features three modes" with "has three modes".
- Replace "represents a major shift" with "is a shift".

### 12. Repeat the Right Word
Do not rotate through four forced synonyms ("developers... engineers... builders... creators") within one paragraph. Use the clear, accurate word consistently.

### 13. No Bold Headers on Plain Bullets
Do not write "**Performance:** Performance improved by 30%." Just write "Performance improved by 30%."

### 14. One Hedge, Not Two (Protect Factual Caveats)
- Cut stacked stylistic hedges ("could potentially create", "may eventually unlock" -> pick one).
- Protect real factual caveats: "unaudited", "estimate", "unconfirmed", "as of Q3" are essential technical qualifiers. Never strip factual caveats.

### 15. Earn Numbers & Cut Present Participle Glosses
- Only use numbered lists when items have a natural, discrete sequence. Never pad a list to hit "5 key takeaways".
- Cut trailing `-ing` analysis clauses: "...reflecting a commitment to excellence and symbolizing progress" -> delete. Show concrete facts instead.

### 16. Never Ship Placeholders
Search drafts for `[`, `XX`, and `TODO`. Never release a text with unpopulated slots.

### 17. Colon, Not Period, on Bullet Labels
When a bullet begins with a brief label, join with a colon:
- Bad: "**Intros.** Years of networking."
- Good: "**Intros:** years of networking."

### 18. No Mid-Sentence Bold for Emphasis
Never bold words mid-sentence (`**critically**`, `**the key insight**`). The sentence structure itself must carry the emphasis. Bold is strictly structural (headings, table headers).

### 19. Vary Sentence Rhythm (Burstiness)
LLMs generate monotonous 15–20 word sentences. Intentionally vary rhythm: combine very short punches (under 6 words) with descriptive compound sentences (25+ words).

### 20. Commit and Ground in Concretes
Avoid reflexive "both-sidesing" where every statement is cushioned with an automatic counterpoint. Ground abstract claims in concrete details: specific tool names, real numbers, dates, and locations.

---

## Anti-AI Pass Checklist for Rephrasing
When rephrasing or cleaning a draft:
1. Did you delete filler openings and closing cliches?
2. Did you strip all em-dashes (`—`)?
3. Did you remove negation-pivot antithesis and stock buzzwords (*delve, leverage, seamless, robust*)?
4. Did you eliminate mid-sentence bolding?
5. Did you verify that factual caveats and technical definitions were protected?
6. Does the output sound like a clear human speaking with purpose?
