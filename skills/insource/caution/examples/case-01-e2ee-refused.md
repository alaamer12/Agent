# Case 01 — "No" to end-to-end encryption

> The case the skill exists for. Two devices, one answer with a cost the user had not been told, and a re-ask
> that changed the outcome.

## The setting

A small product: notes sync between a phone and a laptop. The agent needs to know how to move the data, and asks:

> "Do you want end-to-end encryption?"

The user answers:

> "No, sounds complicated."

## Screen

| Question | Reading |
|---|---|
| protection declined? | yes — the answer declines a protection the agent offered |
| unbounded growth? | no |
| irreversible? | not yet — nothing has been sent |
| outward-facing? | yes, once two devices talk over a network the traffic leaves the user's control |
| knowledge test | **fails**: "sounds complicated" names effort, not cost. The user has not been told what "no" means |

Grade: **DANGER** — protection off, external exposure, already on the path to being enabled, no awareness.

And note the first mistake: *"Do you want E2EE?"* is the question shape that produces this answer. It asks the
user to price a protection they have not been told the cost of. The card repairs it — but the better fix was the
question ([`02`](../references/02-the-danger-card.md), "Ask so the card is rare" in `SKILL.md`).

## The card

```text
!! DANGER — "No [E2EE], sounds complicated"
What is gone: the server will be able to read every note, and so will anyone who can reach the traffic on a
             shared network
How it fails: anyone on the same Wi-Fi as either device can read the sync payload and capture the session
             token, because the traffic would carry no encryption the server does not hold a key for
If it happens: "Note sync traffic readable on a hotel network: session tokens captured, two accounts taken over,
                reported by users two days later."
Blast radius: every note of every user syncing on an untrusted network, for as long as the feature ships this way
Undo cost: now — one transport change before release. Later — rotate every token, force re-pairing on every
           device, and the notes already read stay read
Cheapest adequate option: keep the "no E2EE" decision, but still encrypt the wire (HTTPS/WSS with pinned
           certificates) — the server can read, the network cannot
```

> **Are you sure?** Reply "yes, accept the risk" to proceed — or pick the alternative and we move on.

## The clarification the card forces

"No E2EE" and "no encryption" are different answers, and the card makes the difference visible:

| Layer | E2EE declined | Still available |
|---|---|---|
| server reads the payload | yes, by design | — |
| network reads the payload | only if transport is also plaintext | **TLS closes this** |
| stored data | as stored | encryption at rest closes this |

Most "no E2EE" answers mean *"I don't want to build key management"*, not *"I want plaintext on the wire"*. The
card is what surfaces that — the user is answering a question they did not realise they were answering.

## Outcome A — accepted

> "yes, accept the risk"

Then: proceed with WSS and continue. No second lecture. The build still does the parts the
answer did not decline — encrypted transport and rotating tokens are not E2EE, and silently omitting them because
the user said "no" to something else would be the opposite failure: **implementing a worse version of the
unprotected variant than the answer asked for** (the authority-line mistake in `dtb`).

Close the loop in one line, in the chat and nowhere else:

> Accepted — proceeding with a server-readable payload over encrypted transport.

That sentence is the whole record. No file, no log, and no promise to revisit it every session. If the user ever
wants the decision to outlive the conversation, that is their call (a `dtb` decision record), not something this
skill creates.

## Outcome B — reconsidered

> "wait, no — I don't want people reading notes. Just don't make me build keys."

Then: TLS, tokens rotated, and (often) encryption at rest from the platform. That is not E2EE, but it is not the
plaintext option either. The card worked exactly as designed: it converted a vague "no" into a priced decision,
and the user picked the cheaper guard. One line closes it: "Taking the guarded option — nothing to warn about."

## What this case teaches

1. **A bare yes/no question about a protection is a trap** — the answer arrives without its cost.
2. **"No" to a named mechanism is not "no" to every guard.** Disambiguate the layer before implementing.
3. **The postmortem headline is what lands.** "Sounds complicated" becomes "tokens captured at a hotel network"
   in one sentence, and the decision changes.
4. **Both outcomes are successes.** Accepted after being told is as valid as reconsidered; the failure is an
   uninformed yes or no, with no moment in the conversation where anyone was told.
