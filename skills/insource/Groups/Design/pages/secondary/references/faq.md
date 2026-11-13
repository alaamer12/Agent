# FAQ

Answers to questions people actually ask. The evidence rule is the page's whole identity: an FAQ
written from imagined questions is a marketing list wearing a support mask.

## Must include

1. **Real questions only** - the source is support tickets, the pre-sales inbox, community posts,
   the store reviews. If the project is pre-launch: say which questions ARE answered by which
   document instead (a "start here" routing list), or skip the page - the filter is the user's
   (ASK: "what do people actually ask?").
2. **Answers with owners** - each answer: the direct fact in 2-4 sentences, then the canonical
   pointer when the fact lives elsewhere ("refund windows: full rules in Refund Policy"). One
   owner per fact: the FAQ restates nothing that a policy document owns - it routes.
3. **Grouping** - 3-6 clusters (getting started, money, data, account, platform); the page grows
   by adding a question to a cluster or a cluster when a fifth keeps forming.
4. **Dates** - "answered as of [date]" on anything that can age (pricing, limits, platforms).
5. **Search or jump** - past ~15 questions the flat accordion stops working; a text-search box on
   the one file (static, per `engineering.md`) beats an infinite accordion.

## Placement

The accordion fits an FAQ better than anything else (and unlike contracts, folded answers carry no
consent risk - placement itself remains the user's decision, see `presentation.md`'s rule: shapes
are examples, not a menu): questions in the DOM, content pre-rendered, collapsed by default,
deep-linkable per question (`#how-do-i-export-data`) so a support reply can cite a single answer.
Schema [FAQPage JSON-LD] helps these questions rank where users type them.

## Writing professionally

- Question in the user's words ("can I use it offline?"), not the brand's; answer starts with the
  yes/no/number, then the nuance.
- Tone follows the project's voice document (agents-md §23) - the FAQ is where voice is most
  visible.

## Ask the user - never invent

The actual question set; which answers have policy owners (then the answer is a link, not a
restatement); anything about limits/pricing/roadmap (roadmap questions: answer "not stated" or
skip - never leak a maybe into a FAQ).
