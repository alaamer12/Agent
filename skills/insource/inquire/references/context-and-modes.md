# Context, TL;DR, and modes

## The context must be comprehensive

The context is not a summary and not a reflection of the latest message. It is everything the user needs to understand what the questions are based on, drawn from the **whole conversation** and from what you inspected.

Cover, as relevant:

| Section | What goes in it |
|---|---|
| Goal | What the user is trying to achieve, in their terms, including why. |
| Background | How the conversation got here: earlier requests, changes of direction, things tried. |
| Environment | OS, platform, versions, hosting, tools, existing code, account limits. State how the same task would differ on another platform when it matters. |
| Constraints | Budget, deadlines, team skills, compliance, performance targets, things the user ruled out. |
| Decisions already made | Each one with where it came from ("your first message", "your config file"). |
| Open items | What is still undecided and which question settles it. |
| Assumptions | Decisions you made yourself because they had no consequence, so the user can object. |
| Terms | Any term the questions use that a non-expert might not know. |

Use headings, a table for environment or status, and a diagram for the current state or the process being decided. Gather facts first (read files, run version commands); never guess an environment detail.

## TL;DR

- 1 to 5 bullets that summarise the context above it.
- It adds no new information and never replaces the context.
- A reader who only reads the TL;DR should still know the situation and what is being asked.

## Verbose mode (default)

Verbose shows the full picture: every micro-step, every micro-detail, the knowledge needed to decide. Verbose is **not** padding.

Include, per element:

- **Context**: all sections above, with a process or architecture diagram and a status table.
- **Question** (`about`): what is being decided, in full sentences, including what happens in each situation. (`why`): the honest reason you are asking and what the answer changes. (`terms`): every concept that may be unclear. `vis`: a table, diagram, or list that helps compare.
- **Option** (`d`): what it is and how it works. Pros and cons, or the facet shape that fits. A diagram, code, or table when it shows a difference. A numbered `steps` block when the option has a setup procedure, with real commands.

Filler to cut even in verbose: restating the question, "it is worth noting", "as you may know", hype ("powerful", "seamless"), hedging without a reason, apologies, and sentences that repeat the line above.

## Concise mode

Same schema. Context: a short paragraph plus one table or diagram. Questions: `about` in one or two sentences, `why` in one line, `terms` only when needed. Options: a one-line description, 1 to 2 pros and cons or facets, rich content only when it clarifies a difference. Never drop the "why", the recommended order, or the custom answer.

## Language and `ui`

Write all content in the user's language. For non-English pages set `"lang"` and add a `"ui"` object translating the interface strings you want changed. Missing keys fall back to English. Keys:

`ctx, tldr, rec, choice ("{a} of {b}" placeholders), newopt, one, many, fu, hi, why, terms, own, ownm, owns, ph, pick, pros, cons, copy, copied, ctrlc, ans ("{a} of {b}"), submit, skph, skhint, skip, skneed, sent, skipped, close, nosrv, nosrv2, src, verbose, concise, codearia, diagram, msgaria, ownaria`

Example (Arabic): `"lang":"ar","ui":{"ctx":"السياق","tldr":"الخلاصة","rec":"موصى به","submit":"إرسال الإجابات","skip":"تخطي مع رسالة"}`. Code, ASCII diagrams, and commands stay left-to-right automatically.

Use the real current date for `date`.
