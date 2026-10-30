---
name: caution
description: 'Informed-consent gate on the user''s answers: screen every reply (chat, AskUserQuestion, command flags, hook or server input) for a decision whose cost the answerer may not know. Flags the guard, never the goal: storing data on a server, syncing devices or keeping history is the product and gets no card; storing it unencrypted, syncing it in plaintext, or keeping it forever without a cap is what gets flagged. Consequences are not only attacks - data loss, unbounded DB/memory/queue/log growth, irreversible actions, outward-facing contracts, removed safety nets. On a match it raises a visible DANGER mark in the chat, states the failure as a future postmortem headline with mechanism, blast radius and undo cost, names the cheapest adequate alternative, and re-asks once; then it accepts the answer, closes the loop in one line, and never re-opens it. Writes no files and keeps no log - the conversation is the record. A severity ladder keeps it quiet on recoverable calls and informed answers - not risk theater.'
when_to_use: Any answer, choice, confirmation or instruction from the user that removes a protection, accepts unbounded growth or cost, is hard to undo, commits something outward-facing, or declines an option the agent offered (especially "no" to encryption, auth, backups, limits, validation, retention caps). Also when the agent is about to ask a yes/no question whose "yes" or "no" has a serious consequence.
argument-hint: "[the answer or decision to screen — or the question about to be asked]"
---

# Caution

> An answer is a decision. Sometimes the person giving it did not know what it would cost.
> Make the cost visible once — then let them own the decision.

Caution is **not** a veto and **not** a debate about the product. The user decides; the skill guarantees only
one thing: that the decision was made **with its cost on the table**, in front of them.

## The guard, not the goal

The most common way this skill becomes useless is by questioning the product. Do not.

| The user says | Verdict |
|---|---|
| "The data lives on our server." | **No card.** That is the business and the data model. A server can be attacked — so can a phone. Flagging this is noise. |
| "Store it on the server **unencrypted**." / "No encryption at rest." | **Card.** The protection was declined, not the architecture. |
| "The phone and laptop should sync." | **No card.** Syncing is the feature. |
| "Skip E2EE, just send it over the LAN." | **Card.** Two devices now trust every network between them. |
| "We keep chat history." | **No card.** Retention is a product decision. |
| "Keep everything forever, no deletion, no cap." | **Card.** Unbounded growth, and people's old messages forever — a cost and a consent problem. |
| "It's a public API." | **No card.** |
| "The admin endpoints are public and unauthenticated." | **Card.** A boundary that should exist does not. |

The test: **could a competent engineer make the same business choice and never hit this failure?** If yes, the
failure comes from the *missing guard*, and that is what the card names. If no, you are arguing with the
product — stop. Flag the missing seatbelt, never the decision to drive.

## The four steps

```text
1 screen   every user input: did it remove a guard, accept unbounded cost, or lock something in?
2 grade    DANGER (interrupt + re-ask) · WARN (one line) · NOTE (say nothing) · CLEAR (nothing)
3 card     mechanism · future postmortem headline · blast radius · undo cost · cheapest adequate option
4 re-ask   exactly once, then accept the answer and say what happens next
```

No files, no log, no directory. The conversation is the record.

### 1. Screen every answer

Four cheap questions, answered in seconds — that is why this can run on every input:

1. Did the answer **remove or decline a protection**? (encryption, auth, validation, backup, limit, retention
   cap, review, test, timeout, rollback)
2. Did it **accept unbounded growth**? (rows, memory, queue depth, log volume, retries, cost, retention)
3. Is it **irreversible or expensive to undo**? (delete, migrate, overwrite, publish, sign, force-push)
4. Does it **commit something outward-facing**? (public API, wire format, licence, vendor, other people's data)

Then the knowledge test: **did the answer itself show awareness of the cost?** "No E2EE — I know it means
plaintext on the LAN, we're on an isolated VLAN" is an informed choice → NOTE, not DANGER. "No E2EE, sounds
complicated" is a knowledge gap → DANGER. The trigger is *consequence size* **×** *ignorance*, not consequence
size alone. Full catalogue: [`00`](references/00-what-counts-as-a-risk.md).

### 2. Grade it

| Grade | When | Behaviour |
|---|---|---|
| **DANGER** | a guard is off **and** the exposure is external, irreversible, or already growing unbounded — and the user shows no awareness | stop, show the card, ask once |
| **WARN** | real cost but recoverable, or the user is partly aware | one line inline, then continue the work |
| **NOTE** | the user named the trade-off, or the cost is small and bounded | no interruption, no visible output |
| **CLEAR** | business shape, reversible detail, or the answer *added* a protection | nothing |

When unsure between DANGER and WARN, read the undo cost: cheap to reverse → WARN. It fires only where the user
can still change their mind profitably, and stays quiet everywhere else — this is the anti–risk-theater rule
([`01`](references/01-the-screen.md)).

### 3. Show the Danger card

```text
!! DANGER — <the decision, in the user's own words>
What is gone: <the protection that stops existing from now on>
How it fails: <mechanism — who does what, to which data, with numbers if you have them>
If it happens: "<postmortem headline a year from now>"
Blast radius: <who or what, how much, how long>
Undo cost: now <…> · later <…>
Cheapest adequate option: <the smallest thing that removes the exposure>
```

Then, as the actual question:

> **Are you sure?** Reply "yes, accept the risk" to proceed — or pick the alternative and we move on.

Rules for the card: name the mechanism, never the adjective ("traffic is readable by anyone on the same Wi-Fi",
not "it is insecure"); quantify in the user's units (rows/day, GB/month, $, minutes of downtime); the
postmortem headline is what makes the cost real — one sentence, past tense, as if the incident already happened.
Seven lines maximum. When you cannot quantify, say what you *would* watch to find out
([`02`](references/02-the-danger-card.md)).

### 4. Re-ask once, then accept

- **Once per decision.** Ask, read the answer, proceed. Never re-open it in the same session because you still
  disagree — that is nagging, and it teaches the user to click through your warnings.
- **A confirmation ends it.** "Yes, accept the risk" (or any clear yes after the card) → do the work; mention
  the consequence at most once more if it materialises.
- **Never block reversible work while waiting** for the confirmation; only a destructive-now action waits.
- **Never moralise, never repeat the lecture, never add a second warning sign to the same decision.**
- If the user reacts with annoyance or "I know", drop to NOTE for the rest of the session on that topic — they
  told you their awareness level; believe them.
- If the user *changes* the answer, take the new one without ceremony; the card did its job.
- **One line closes the loop.** After a clear yes: "Accepted — proceeding; the cost we discussed is <one clause>."
  That sentence is the whole record; do not write it to a file, and do not repeat it in later turns.

## Ask so the card is rare

Most Danger cards are avoidable: put the cost **inside the question**, before the answer exists.

| Instead of | Ask |
|---|---|
| "Do you want E2E encryption?" | "Traffic between phone and laptop: encrypt it (extra key exchange, some setup) or send it as-is (readable by anyone on the same Wi-Fi)?" |
| "Should we keep history?" | "Keep history for 30 days (bounded storage) or forever (storage grows ~<n> MB/day, and old messages stay reachable)?" |
| "Add authentication?" | "Admin actions: require a login, or leave them open to anyone who finds the URL?" |

An answer to a question that named its cost is an informed answer — it skips straight to NOTE/CLEAR.

## Mediums — screen the input wherever it arrives

| Medium | Where the screen happens | How the mark appears |
|---|---|---|
| Chat reply | the moment you read the message, before acting | the card, in the reply |
| `AskUserQuestion` / questionnaire tool | the tool **result**, not just the visible option | card before the next action |
| Skill or command arguments (`/x --no-auth`) | argument parsing, before the skill body runs | one-line WARN or card |
| Hook-injected or server-side confirmation | before the effect executes | card in the response that carries it |
| Relay from another agent or user ("the user said skip backups") | the relay is a claim, not the user's words — verify or screen it | card if unverified: "screened as their answer, confirm?" |
| Written spec, ticket, or doc that arrives as input | when you act on it | reference the line, then the card |
| Silence / no answer to a DANGER card | do not proceed with the risky default | treat as unanswered; ask once, then choose the reversible path and say so |

## Make it actually always-on

Two mechanisms, in order of strength:

1. **Pin it** so it applies unprompted in every session — `node ../theskills/scripts/theskills.mjs pin caution
   --when "any answer, choice, or confirmation from the user that changes scope, removes a protection, or costs
   money or data"` ([`theskills`](../theskills/SKILL.md)). Optional, per-repo, and only if the user asks for it:
   this skill itself writes nothing.
2. **A session-start or prompt-submit hook** that injects the four screen questions. This is a harness config
   change: propose it, never install it silently.

Honest limits, so nobody relies on more than exists: a skill is **advisory** — an instruction in context, not
an enforcement path, and a model under pressure can skip it. The screen is four questions precisely so that
running it on every input costs almost nothing; the card is the only expensive part, and it fires rarely.

## Anti-patterns

- **Cautioning the product** — server storage, accounts, public APIs, syncing, retention as a concept. The
  user's clarification is a rule here: flag the missing protection, not the architecture that needs it.
- Crying wolf: a DANGER on anything with a theoretical downside trains the user to ignore you.
- Repeating a warning the user already answered, or stacking a second warning on the same decision.
- Vague fear ("this is a security risk") with no mechanism, no blast radius, no undo cost.
- Refusing to proceed after the user accepted ("I can't let you do that"). Caution informs; it does not govern.
- Claiming a warning was "logged" or "recorded" when nothing anywhere stores it — or writing files the user did
  not ask for. The chat is the record; if a decision truly must outlive the session, say so and let the user
  choose the decision record (`dtb`), do not create one on your own.
- Blocking reversible work while waiting for an answer to a card.
- Screening only chat and missing the tool result, the command flag, or the relayed instruction.

## Boundaries

| Not this | Go instead |
|---|---|
| finding vulnerabilities in code or config | `security-scan`, `antipattern` |
| the user wants their own thinking attacked | `grill-me` |
| deciding the engineering approach yourself | `dtb` (it already asks before irreversible calls) |
| writing the incident after it happened | `postmortem` (an accepted risk you disclosed is evidence for §17) |
| documenting a change that removed a guard | `diffs`, `commit` — state the accepted risk in the message |
| settling a performance or cost claim with numbers | `benchmark` |

## References

| File | Owns |
|---|---|
| [`references/00-what-counts-as-a-risk.md`](references/00-what-counts-as-a-risk.md) | the guard-not-goal rule in depth, the shape-vs-protection table, the consequence classes (protection, growth, irreversibility, contracts, authority, silence, compliance, resilience, compounding debt), detection cues |
| [`references/01-the-screen.md`](references/01-the-screen.md) | the cheap always-on test, the knowledge test, the severity ladder, the false-positive catalogue, handling annoyance, where the screen sits per medium |
| [`references/02-the-danger-card.md`](references/02-the-danger-card.md) | card template, writing the future postmortem headline, quantification, what to say when you cannot quantify, renderings, length caps |

## Cases

| Case | Situation | The point |
|---|---|---|
| [`examples/case-01-e2ee-refused.md`](examples/case-01-e2ee-refused.md) | "No" to E2EE between a phone and a laptop | the full card, the re-ask, both outcomes |
| [`examples/case-02-retention-without-bound.md`](examples/case-02-retention-without-bound.md) | "keep every event forever, we have space" | inflation with no attacker at all — growth, cost, deletion duties |
| [`examples/case-03-shape-not-risk.md`](examples/case-03-shape-not-risk.md) | server storage; a dev-database drop by its owner | the restraint that keeps the skill trustworthy |

## Assets

- [`assets/templates/danger-card.md`](assets/templates/danger-card.md) — copyable card, with the WARN, NOTE and
  "already accepted" variants.
