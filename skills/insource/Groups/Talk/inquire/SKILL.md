---
name: inquire
description: Build a rich, interactive question page (HTML) when the agent must get several important decisions from the user before or during work. Use it when there are 2 or more open questions whose answers change the project, design, architecture, or approach, and the user needs context, trade-offs, diagrams, or examples to choose well. Also use it when the available question tools are too limited (few questions, short text, no visuals). Triggers include "ask me questions first", "clarify before you start", "what do you need from me", planning a project, picking a tech stack or architecture, configuring something with real trade-offs. Do NOT use it for one quick question (ask in chat) or for questions whose answer can be inferred or looked up.
---

# Inquire

Inquire turns "I need to ask the user some questions" into one HTML page the user can read, understand, and answer. The page carries full context, explanations, trade-offs, diagrams, branching follow-ups, and a way to skip and steer.

The user must understand every statement and every option. The questions exist to settle **important decisions**, not to collect trivia.

## Modes

| Mode | Use when | Meaning |
|---|---|---|
| **verbose** (default) | always, unless the user asks otherwise | Show every micro-step and micro-detail with full knowledge. Verbose means complete, never padded: no filler, no restating the question, no hype, no hedging. |
| **concise** | the user says "short", "concise", "quick", or similar | Main point plus one supporting line. Fewer visuals. Same structure. |

The mode changes depth only. The content schema, branching, and delivery are the same.

## Workflow

1. **Gather context first.** Re-read the whole conversation. Inspect files, configs, versions, and the platform when you can. Never ask what you can look up. See `references/context-and-modes.md`.
2. **Brainstorm every potentially relevant question**, then **filter hard**. Keep a question only if the answer changes a decision, cannot be inferred, and has a real consequence or preference. See `references/when-to-ask.md`.
3. **Design the questions**: order options by your preference (first = recommended), choose single or multiple choice, choose the trade-off shape that fits (pros/cons, advantages over a named alternative, "choose it when"), and add follow-ups. See `references/question-design.md`.
4. **Add rich content** wherever it improves understanding: in the context, in the question, and inside options. Diagrams must carry meaning. See `references/rich-content.md`.
5. **Add branching** where an answer opens new questions, options, or decisions. See `references/branching.md`.
6. **Write `content.json`** (schema below), then validate and build:
   ```
   python3 scripts/check_questions.py content.json            # fix every ERROR and WARN
   python3 scripts/build.py content.json --out inquire.html   # verbose by default; add --mode concise
   python3 scripts/check_page.py inquire.html                 # optional browser smoke test (needs Playwright)
   ```
7. **Deliver** and wait for the answers. See `references/protocol.md`.
8. **Read the answers**, state the decisions back in one short list, and continue the work. If the user skipped, read their message first and rethink. See `references/protocol.md`.

## Content schema (`content.json`)

```json
{
  "title": "Subject of the questions",
  "date": "6 October 2026",
  "lang": "en",
  "context": ["paragraph", {"k":"h","t":"Heading"}, {"k":"table","h":[],"r":[[]]}],
  "tldr": ["short summary of the context, 1 to 5 bullets"],
  "qs": [{
    "id": "scheduler", "type": "single", "q": "The question?",
    "about": "What is being decided.", "why": "Why the agent is asking.",
    "terms": [["Term", "Plain explanation"]],
    "vis": [ "blocks shown inside the question" ],
    "when": {"q": "earlier-id", "is": [1]},
    "opts": [{
      "t": "Option title", "d": "Description",
      "pros": ["..."], "cons": ["..."],
      "facets": [{"h": "Advantages over X", "tone": "good", "i": ["..."]}],
      "vis": [ "blocks shown inside the option" ],
      "when": {"q": "earlier-id", "is": [0]}
    }]
  }]
}
```

- **Blocks** (usable in `context`, `qs[].vis`, `opts[].vis`): a plain string is a paragraph; objects are `h`, `ascii`, `code`, `table`, `list`, `steps`, `chart`, `src`. Details and examples are in `references/rich-content.md`.
- **Inline markup** in any text: `` `code` ``, `**bold**`, `==highlight==`.
- **`facets`** replace `pros`/`cons` when another shape fits the question. Tones: `good`, `bad`, `info`, `neutral`.
- **Do not add an "Other" option.** The page always adds "Write your own answer" and shows "Recommended" and "My choice n of m" itself.
- **Language**: write everything in the user's language. If it is not English, set `lang` and provide `ui` translations (keys listed in `references/context-and-modes.md`). RTL languages switch the layout automatically.

## Hard rules

- Never ask obvious, trivial, or inferable questions. If a detail has no preference and no consequence, decide it yourself and list it under assumptions in the context.
- The context is comprehensive and covers the whole conversation. The TL;DR summarises it and never replaces it.
- Every option the user could pick must be understandable on its own: what it is, what it costs, what it gives up.
- Never invent sources, prices, versions, or benchmarks. Look them up, or label figures as illustrative. Cite only real URLs.
- Put the preferred option first. Do not rank by what is easiest for you.
- Do not tell the user how to answer in the question text. The page already explains the controls.
- If the answers could not change what you do next, do not ask.

## Files

- `assets/template.html`: the page engine (do not edit per run; content goes in JSON).
- `scripts/build.py`, `check_questions.py`, `serve.py`, `check_page.py`
- `examples/`: `backup-verbose.json`, `backup-concise.json` (branching, diagrams, tables, code, charts), `tech-stack.json` (trade-offs between two named alternatives).
- `references/`: the six guides linked above.
