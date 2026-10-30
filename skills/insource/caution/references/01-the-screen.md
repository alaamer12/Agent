# The screen — how to check every answer without becoming a nuisance

> **Illustrative, not exhaustive.** The questions below are the reflex, not a legal test. An unlisted
> consequence is still a consequence.

The screen has to run on **every** user input, so it has to be cheap: four questions, answered from the answer's
own words, in about two seconds. Everything expensive — the card, the arithmetic, the postmortem headline —
happens only after the screen says the answer might be costly.

## The four questions

| # | Question | A yes looks like |
|---|---|---|
| 1 | Did it remove or decline a **protection**? | no encryption, no auth, no validation, no backup, no limit, no timeout, no rollback, no review, no test |
| 2 | Did it accept **unbounded growth**? | keep forever, no cap, no TTL, no pagination, retry forever, log everything, cache it all |
| 3 | Is it **irreversible or expensive to undo**? | delete, drop, overwrite, migrate, publish, sign, send, force-push |
| 4 | Does it **commit something outward-facing**? | public API, wire format, URL, package name, licence, vendor, other people's data |

Any yes → go to the knowledge test. All no → CLEAR, move on.

## The knowledge test

The trigger is **consequence × ignorance**, not consequence alone. Read the answer, and ask: *does this sentence
show that the person knows what it costs?*

| Answer | Reading | Grade |
|---|---|---|
| "No E2EE, sounds complicated." | cost not named, reason is effort | DANGER |
| "No E2EE — plaintext on the LAN is fine, this runs on an isolated VLAN." | cost named, scope named | NOTE |
| "Keep events forever, storage is cheap." | cost named but wrong (it is not cheap at that rate) | DANGER — show the arithmetic |
| "Keep events 90 days, that's our policy." | informed | CLEAR |
| "Just drop it, it's a scratch DB I made an hour ago." | informed, reversible | CLEAR |
| "Drop it, the app doesn't read it." | *claims* safety, no evidence | check first — one grep decides CLEAR vs DANGER |

Three rules keep this honest:

- **Do not profile the user.** The evidence is the sentence in front of you, not their title, history, or how
  fast they type. The same words from a beginner and an expert get the same screen; they may get different grades
  because one of them usually names the cost.
- **"I know" is data.** Once the user states awareness, do not re-litigate that topic in the session.
- **A wrong cost estimate is a knowledge gap.** "Storage is cheap" is an awareness failure dressed as awareness:
  grade on the arithmetic, not on the confidence.

## The severity matrix

| | user names the cost | user shows no awareness |
|---|---|---|
| **exposure external / irreversible / already growing** | NOTE | **DANGER** — card, ask once |
| **recoverable but expensive** (hours–days to undo) | NOTE | **WARN** — one line, then continue |
| **small, bounded, minutes to undo** | CLEAR | CLEAR |

Read the three axes when a case is borderline:

- **Exposure** — can someone who is not the user reach it? (Public network, other tenants, the internet, another
  team.) Internal-only and single-user lowers the grade one step.
- **Reversibility** — minutes → CLEAR, hours/days → WARN, cannot be undone or only before a point of no return →
  DANGER.
- **Growth** — is it already accumulating, or would it only matter after a deliberate scale change? Bounded
  input → WARN; a rate with no ceiling → DANGER when the first pain date is inside the project's horizon.

Grade **down** when your own evidence is weak. A card you cannot defend is worse than a NOTE you can; the user
learns to discount the mark, and it stops working for the case that matters.

## False positives — the ten that destroy trust

1. **The product's shape.** A server, accounts, sync, history, a public API. Architecture is the user's call.
2. **A trade-off the user already stated.** Their sentence named the cost; that is consent, not ignorance.
3. **Scope that is genuinely local.** A prototype, a scratch database, a throwaway script, `localhost`.
4. **Reversible in minutes.** A flag, a config value, a file that is in version control.
5. **A policy the user is relaying.** Raise it with the policy's owner; do not card the messenger.
6. **A preference.** Tabs, naming, colour, framework taste — the agent may have an opinion; it is not a risk.
7. **A decision already answered.** Asking again is how a warning becomes a joke.
8. **An answer that added a guard.** Say "good" in one clause, or say nothing; never grade it as risk.
9. **Something you cannot explain.** If you cannot name the mechanism in one sentence, verify or drop it.
10. **Your own uncertainty about the product.** "This might not scale" without a rate is a suspicion, not a
    finding. `benchmark` it or leave it.

## Where the screen runs, per medium

| Medium | The moment | Common miss |
|---|---|---|
| Chat reply | before the next tool call, not after | reading the message, starting work, screening later |
| Tool result (`AskUserQuestion`, forms) | on the **result** — the selected option, not your summary of it | treating the UI's short label as the whole answer |
| Command / skill arguments | while parsing, before the body runs | a `--no-verify` or `--skip-checks` flag that never appears in chat |
| Hook or server-side confirmation | before the effect executes | the effect runs in the same call as the confirmation |
| Relayed answer ("the user said …") | treat as a **claim**; ask if it is unclear | accepting a paraphrase of a DANGER-grade decision with no verification |
| Spec, ticket, or doc handed over as input | when you first act on it | the risk is in a line nobody quoted back |
| No answer at all | when the card went unanswered | proceeding with the risky default because silence is not dissent |

**Screen your own questions too.** When you draft a yes/no question, check whether one of the answers has a
serious consequence. If it does, put the cost into the option (SKILL.md, "Ask so the card is rare") — that is the
cheaper intervention: it prevents the uninformed answer instead of catching it.

**Screen your own proposals.** The agent generating options is not neutral: offering "fast path (no validation)"
as an unmarked option is how a risky default gets chosen. Any option the agent offers carries the same
disclosure duty as an answer.

## When the user is annoyed

Expected, and not a failure of the skill — a failure of calibration if it repeats.

- Once: "Noted — accepted, moving on." Then move on, in the same message.
- If the user says they knew, drop that topic to NOTE for the session. Do not test them again.
- If the user says "stop warning me", stop carding that *class* for the session, keep noting risk silently, and
  say which classes you are no longer raising so the change is visible rather than silent.
- Never both apologise and repeat the warning; that is the worst of both.
- Remember what you already asked **in this conversation**. A second card on the same topic in the same session
  is always a mistake, even without a log to check — the thread is the record.

## Cheap to run, expensive to ignore

The screen costs four checks and usually zero output. The card costs seven lines and fires rarely. What is
expensive is the alternative: a decision nobody knew the price of, discovered as an incident, with no moment in
the conversation where anyone was ever told.
