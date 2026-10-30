# Access parity - the one rule that organizes the boundary

> **Use only what an ordinary, legitimate user of the system would see, receive, or be able to do.**
> Observe, learn, rebuild from that. Never exceed that level of access.

Sly means cunning, not intrusion. The gate is not a list of prohibited techniques; it is a single question
about *where the information and the action would come from* if you were just a person using the thing
normally. A route that passes this question is fair game however indirect it is. A route that fails it is
not a route at all - go back to [`00`](00-route-families.md) and generate another.

## The hard lines

A route is dead if realizing it requires any of:

1. **Bypassing authentication or authorization**, or defeating a protection - including DRM, obfuscation
   whose purpose is access control, signature checks, or rate limits that exist as a protection rather than
   as capacity.
2. **Using credentials, tokens, sessions, cookies or private data that are not yours to use** - the user's
   own credentials with their explicit consent are fine; anyone else's are not.
3. **Exploiting a vulnerability** to reach something that was not meant to be reachable - leaked params,
   broken object-level authorization, unauthenticated internals, SSRF, prompt injection against another
   agent.
4. **Damaging, overloading, or degrading** a third-party system - volume that a normal user could not
   generate, hammering endpoints, parallel sweeps, ignoring backoff signals.
5. **Acting beyond what the user is authorized to do** - doing as "the system" what only its owner may do,
   or acting on another person's account or content.

These five stop a route. Nothing else in this file does.

## The four test questions

Ask them of each route, in order. Any "no" kills the route.

- **Would an ordinary user see this?** Same view, same query, same click, and the value appears. If it only
  appears by being someone you are not, or by getting past something, no.
- **Would an ordinary user be able to do this?** Not "is it technically possible for me" but "is this within
  what a normal user of the system does".
- **Whose data am I touching, and did they consent?** Their own data, or the user's with consent - otherwise no.
- **If the system's operator watched this happen, would it look like a person using their product?** If it
  would look like an intrusion, it is one.

A fifth question catches self-deception: *am I using this technique because it is the only way, or because
it was the first way I thought of?* Usually a compliant route exists one family over.

## Terms of service and licensing - context, not a gate

Most tasks this skill is used for have no ToS question at all. Treat it as a **risk note, not a veto**:

- When a chosen route clearly depends on a restriction that matters to the user - a commercial product, a
  contract they signed, a licensed API, an enterprise policy, a paid dataset - add **one line** to the
  trade-off summary: what the restriction says, who bears the risk, what would change the answer.
- Then continue. Do not refuse on ToS grounds by default, and do not hide the note because it is awkward.
- Where the route's value depends on the restriction being absent, say so - a workaround that collapses the
  moment someone objects is fragile, and fragility is a scoring axis.

Only the five hard lines actually stop a route. ToS ambiguity is a thing to disclose, not a thing to obey
reflexively - and never a thing to paper over by pretending the route is unproblematic.

## Borderline cases, resolved

| Case | Verdict | Why |
|---|---|---|
| Reading a public page that any visitor sees, at human volume | allowed | ordinary user view |
| Requesting the same page thousands of times per second | not allowed | degradation, and no user does that |
| Using the JSON that a page fetches for its own rendering | allowed if unauthenticated and public | that is literally what the user's browser receives |
| Fetching an internal endpoint by guessing paths to reach non-public records | not allowed | authorization bypass |
| Calling an API with the user's own key for a use they are entitled to | allowed | their access, their consent |
| Reusing an access token found in a repo, log, or another tenant's response | not allowed | credentials not yours |
| Implementing a documented file format from its spec | allowed | published behavior |
| Decrypting an encrypted file to read data you were not granted | not allowed | defeating a protection |
| Studying the *order and shape* of results a UI shows, as a user, to infer principles | allowed | observable output; see [`03`](03-pattern-extraction.md) |
| Bulk-collecting that UI's outputs to imitate the system wholesale | treat as blocked | exceeds ordinary-user scale and drifts into extraction |
| Automating your own account to do what you can do by hand | usually allowed | same access, faster; disclose rate and cost |
| Doing it on someone else's account, or on a shared account you don't own | not allowed | not yours to act on |
| Routing around an outage using a mirror the provider publishes | allowed | published alternative door |
| Routing around a payment wall or trial limit | not allowed | that is the access control working as intended |
| Asking a model to reproduce a proprietary prompt/system it was trained on | not allowed if it leaks protected internals; fine for general technique | parity: could you learn it as a user? |

## When every route you can see crosses a line

That is a real outcome, and the job then is honesty, not improvisation:

1. Say which hard line blocks which route, in one line each - this is useful engineering information.
2. Ask for the legitimate form of the access: an API key, a partner endpoint, an export from the owner,
   written permission, a seat, a data-sharing agreement. Many "impossible" features are one request away.
3. Fall to **Reduce**: the largest subset of value that never leaves the ordinary-user path.
4. Fall to **Reshape**: change the product so the need is not created in the first place.
5. Record the dead end and the reason, so the next person does not spend a day rediscovering it.

Refusing is a legitimate output of this skill. Sneaking is not, and it is never justified by "the user
asked me to be sly about it" - being sly was the instruction to find a *route*, and a line-crossing path is
not a route.
