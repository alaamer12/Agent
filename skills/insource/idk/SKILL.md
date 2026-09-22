---
name: idk
description: Use this skill whenever the user directly signals they don't know what they want or need — phrases like "idk", "I don't know", "not sure what I need", "I don't know how to explain it", "I can't put it into words", or similar explicit expressions of uncertainty about their own intent. This is NOT a general clarifying-questions skill — it only triggers on that explicit signal, not on every vague or underspecified request. Once triggered, it guides the user from a fuzzy feeling toward a clear, named intent through a calm, jargon-free conversation, optionally looking around the project's code and docs for clues, and ends with a plain-language review that maps what the user said onto the standard technical term for it.
---

# idk

## The situation this is for

The user knows *something* is off, or wants *something* to change, or has a feeling about the project — but they can't articulate it in technical terms, or they're not sure what they actually want yet. They say "idk" not because they're lazy, but because turning a vague feeling into a concrete, actionable request is genuinely hard, especially across a language or expertise gap. Forcing them to pick from a menu of technical options right away just adds friction on top of the uncertainty.

Your job here is not to extract a spec as fast as possible. It's to sit with the user for a minute, look around if it helps, and talk it through like a thoughtful colleague — until the shape of what they mean becomes clear to both of you.

## Why this needs a different mode than normal clarifying questions

Normal clarifying questions assume the user roughly knows what they want and just needs to fill in details for you. Here, the user isn't sure themselves. If you respond with a technical-sounding question or a menu of options, you're asking them to already know the answer in a form they don't have — which is exactly what "idk" was signaling they don't have. So:

- Don't lead with jargon. If a term is necessary, introduce it gently and explain it in passing, don't assume it.
- Don't present the user with a wall of options to choose from. Ask one plain question at a time, in ordinary language, like you'd ask a friend describing a problem with their car.
- Don't rush to a diagnosis. It's fine to take a few exchanges to get there.
- Don't act on anything yet. Your job in this mode ends when the user's intent is captured and confirmed — not when a fix ships. What happens after is a separate conversation.

## The flow

### 1. Acknowledge, don't interrogate

Open by making it clear that not knowing is a completely normal starting point, and that you'll help figure it out together — not by asking them to specify things, but by talking it through. Keep this short; don't over-explain the process itself.

### 2. Look around before asking too much

Before peppering the user with questions, see if you can find clues yourself. If there's a project available (a codebase, docs, specs, recent files, prior conversation history), take a look:

- Skim relevant file/directory names, recent changes, README or doc files, related code.
- Look for anything that seems to relate to what little the user *has* said, even if it's just a feeling or a vague area ("something about the login feels off" → go look at the login-related files).
- Form a couple of hypotheses from what you find, but hold them loosely — you're gathering context to ask better questions, not to guess and declare victory.

This step is optional and proportional: a quick look is enough, this isn't a full audit. If there's no project to look at (pure conceptual/product conversation), skip straight to asking.

### 3. Ask, one plain question at a time

Use what you found (or the conversation so far) to ask a single, concrete, everyday-language question that narrows things down. Some patterns that work well:

- Point at something specific and ask if that's close: "Is this more about how it *looks*, or about something it *does* that bugs you?"
- Ask for a story instead of a spec: "Can you walk me through what happens right before it feels wrong?"
- Offer a plain-language guess and let them correct it: "It sounds like maybe things are moving too fast for you to follow — is that close, or is it something else?"

Avoid asking more than one question per turn. Let the user's answer shape the next question rather than pre-planning a full interview.

### 4. Keep narrowing until the shape is clear

Keep going conversationally — a few short exchanges is normal and fine — until you can see the *shape* of what the user means: not necessarily the exact technical implementation, but a clear plain-language description of the thing they're pointing at. You'll know you're there when you could describe it back to them in one or two sentences and they'd say "yeah, exactly."

Don't force this to resolve faster than it naturally does. If after a few exchanges it's still fuzzy, that's fine — keep gently narrowing rather than guessing and moving on.

### 5. Close with a plain-language review

Once the intent feels clear, close the loop with a short review message. Restate what the user was pointing at using *their own words and phrasing where possible*, then map it onto the standard term or concept for it, if one genuinely exists — without over-claiming precision if it's a loose fit. Something like the shape of:

> "So what you're describing is [restated in the user's own words/framing] — that's what's usually called [the standard term], and it happens because/it means [one-line plain explanation]."

Don't force a rigid template or a fixed opening phrase — adapt the wording naturally to the conversation. The two things that must be present are: (a) a restatement grounded in the user's language, and (b) the standard name for it, only when one genuinely applies — never stretch a made-up or approximate label onto something that doesn't have a clean standard term; in that case just leave the mapping out and stick with the plain restatement.

After that, stop. Don't pivot into fixing it, writing code, or proposing next steps unless the user asks — the point of this skill is to land on a clear, named understanding of what they mean, not to act on it. If they want to move forward, they'll say so, and that's a new, separate task with its own normal working mode.

## Tone notes

- Calm, warm, unhurried. No urgency, no pressure to "just pick something."
- Short sentences. Everyday words. If you catch yourself about to use a technical term before step 5, either drop it or explain it in the same breath.
- Never make the user feel behind for not knowing — "not knowing yet" is the entire premise of this skill, not a problem to apologize for.
