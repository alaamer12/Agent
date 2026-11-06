# Placeholder or fake data - two styles of stand-in, one decision

A revoked value gets replaced by something. There are exactly two families of "something", they look
different, they read differently, and picking between them is a per-artifact decision, not a house style:

| Style | Form | Declares | Reads as |
|---|---|---|---|
| **placeholder** | `[username]`, `<username>`, `[payment-provider]` | "a real value was here; you will not see it" | honest absence - the document admits it was sanitized |
| **fake data** | `alice@example.com`, `+1 555 0142`, a generated silhouette avatar | "this is a stand-in that keeps the shape" | living example - the artifact keeps its flow and runnability |

## The question that decides

**Does the artifact's genre claim truth, or does it demonstrate?**

- **Truth-claiming - postmortems, reports, timelines, tickets, real configs: placeholder.** A fake date in
  an incident timeline is not sanitization, it is a fabricated fact; a reader cannot tell which lines are
  history and which are your invention. The artifact already asserts "this happened", so every stand-in must
  visibly be a stand-in.
- **Demonstrating - tutorials, docs examples, UI mockups, test fixtures, runnable snippets, screenshots for
  a design review: fake data.** `[api_key]` inside a curl example breaks copy-paste, `<customer-1>` in a
  rendered profile card defeats the point of showing the card, and a fixture full of brackets stops being
  valid-shaped data. The artifact asserts "this is how it works", and shape carries that.
- **Mixed artifacts split by surface, not by taste**: the postmortem's prose gets placeholders; its embedded
  repro-config block gets fake data marked as the example it is. One entity, one style everywhere it appears,
  but different surfaces of one document may live in different genres.

## The rules that keep fake data from becoming a new leak

1. **Use reserved name-spaces, never plausible collisions.** `example.com`/`example.org` (RFC 2606),
   `203.0.113.0/24` and friends (RFC 5737), `+1 555 01xx` test numbers, the Alice/Bob/Carol convention,
   Jane/Q Public Doe. An invented `<jhon>` might be someone's actual colleague, and a real-looking address
   might be someone's actual domain - a fake that resolves to a real entity is worse than a placeholder,
   because it *asserts* the wrong thing. Plausible-but-uncollidable is the bar; documented conventions clear
   it, improvisation usually does not.
2. **The fake must not inherit the original's structure.** Same length, same first letter, same
   domain pattern, same surname-initial as the real value - that is the `[acme-corp-redacted]` failure
   wearing a convincing costume. `amr.muhammed@school.edu` → `alice@example.com` is a fake; `ahmed.m@school.edu`
   is the original with a hat on.
3. **Record the style in the map, per entity**: `real-name -> alice@example.com (fake)`,
   `real-name -> [user-1] (placeholder)`. The map already exists to make revocations traceable
   ([`02`](02-substitution-discipline.md)); a style column is what stops a future editor from treating the
   fake as fact, and it is the record that proves the fake was chosen, not drifted into.
4. **Never fake a value the reader is meant to trust as measured.** Aggregate figures, durations that carry
   the lesson, version numbers that caused the bug: if the number teaches, generalize or band it
   ([`00`](00-what-revoking-is.md)), do not invent a number. Fake *identifiers*, never *evidence*.
5. **One line of insurance in demo artifacts**: "names and values in examples are fictional" costs nothing
   and closes the "was that real?" question for good readers.

## Faces and avatars

The image surface has the same two styles ([`08`](08-image-redaction.md)): the placeholder form is the
opaque block or a gray circle; the fake form is a generated silhouette or a neutral placeholder portrait.
Fake wins when the layout must read as a real conversation (a design review of the chat UI); placeholder
wins when the artifact claims truth (the incident screenshot). The collision rule bites hardest here: a
generated face must not be *someone* - stock illustration, not a plausible photo of a person who might exist
in the audience's world, and never a lightly-modified crop of the original.

## And partial masks are a third thing

`A****` is neither placeholder nor fake - it is *real data, partially shown*, which is why it has its own
mode and its own entropy rules ([`07`](07-partial-masking.md)) and never belongs in a shared artifact
outside that mode.
