---
name: revoke
description: 'Sanitise an artifact by revoking what ties it to a specific project, person, customer or deployment: the substance survives, the identity does not. Use when a report, spec, config, log, ticket thread, screenshot must leave its origin - inventory what is specific (names, ids, endpoints, secrets, amounts, dates, paths, metadata), choose per item [redact] [pseudonymize] [generalize] [aggregate] [keep] under one consistent substitution map, deciding per entity between placeholder stand-ins ([username]) and reserved fake data (alice@example.com) by the artifact genre; verify nothing leaks (token sweeps, entropy scans, file and image metadata, links, the map itself); and check the text still makes its argument before recording what was lost. Two explicit modes: /revoke partial masks values to a recognizable fragment (A****) for owner-viewing screens like recovery flows - never for secrets, never for shared artifacts; /revoke image treats screenshots and pictures as first-class artifacts - inventory every visible identifier, paint opaque blocks (blur is de-identification, not revocation), strip metadata and embedded thumbnails, render to temp files and look before finalising. Calibrate to the audience: internal share, external public, third-party tool, regulated data. NOT polyglot - polyglot makes a document stack-neutral, revoke makes it identity- and context-neutral. Boundaries: never to hide wrongdoing, evade a legal hold, strip safety or consent notices, or erase accountability from a timeline; the original stays intact; revocation is a disclosure decision, not deletion.'
when_to_use: The user asks to sanitise, redact, anonymise, de-identify, genericise or "remove anything that identifies our project/customer" from a document, passage, config, log, screenshot, image or case study before sharing or reusing it. Also /revoke, /revoke partial (owner-recognition masks), /revoke image (pixel-level redaction of a picture).
argument-hint: "[artifact or path] + [where it is going] | partial: [values] + [who will see them] | image: [image path] (+ regions, else revoke all visible identity)"
---

# Revoke - strip the identity, keep the point

An artifact is tied to its origin by everything that says *who, where, when, how much*. Revoke removes that
tie so the knowledge inside can travel — while the original stays exactly where it was.

**Core principle: revocation is a disclosure decision, not a deletion one.** You are producing a version for a
wider audience. The source of truth is untouched, and every choice is recorded, because a sanitized document
nobody can trace back is a document nobody can correct.

**The second principle, and the one that separates this from blind redaction: the argument must survive.** If the
reader can no longer follow why the thing happened or what to do, you have not sanitized a document, you have
destroyed it. Meaning is preserved deliberately, item by item ([`00`](references/00-what-revoking-is.md)).

## Not the same as `polyglot`

`polyglot` generalizes **across technology**: it removes the assumption that a reader is on one stack. `revoke`
generalizes **across identity and context**: it removes the facts that name the people, tenants, systems,
contracts and dates that produced the artifact. A document can be perfectly polyglot and still leak your
customer list on line one. Do the two in that order.

## Step 0 - Where is it going? That sets the budget

The destination decides how far to revoke and what must survive
([`05`](references/05-purpose-calibration.md)):

| Destination | Aggressiveness | What must survive |
|---|---|---|
| Same team, different repo | low | identifiers that engineers will need to look up |
| Company-wide | medium | role names, system names, the causal chain |
| Public blog, conference talk, vendor forum | high | the mechanism, the numbers rounded to a useful scale |
| A third-party tool, hosted model, or contractor | high, plus policy check | nothing that is someone else's data to hand over |
| Regulated content: personal, health, financial, security | highest, and often not yours to decide | the lesson, without the record |

If the destination is unknown, ask one short question before revoking anything. A different audience is a
different document.

## Step 1 - Inventory what makes it specific

Walk the taxonomy in [`01`](references/01-what-makes-an-artifact-specific.md) and list every item, including
the ones that feel innocent. Two categories people miss, and they are the expensive ones:

- **Non-text surfaces** - filenames, image contents, document metadata, commit hashes, embedded paths,
  hyperlinks, footnotes, code comments ([`03`](references/03-leak-surfaces.md)).
- **Combinatorial identifiers** - nothing in "our 40-engineer fintech in Austin, migrated in Q3 2025" is
  secret, and the combination names the company. Uniqueness, not secrecy, is the test.

## Step 2 - Choose one operation per item

For each inventory row, pick one and say why ([`00`](references/00-what-revoking-is.md)):

- **[redact]** - remove it, show a marker. Use when the value itself is the sensitive part (a key, an address).
- **[pseudonymize]** - stable stand-in: `acme-corp` → `[customer-1]`. Use when the entity must remain
  distinguishable and traceable within the document.
- **[generalize]** - move up a level of abstraction: `"PostgreSQL 14.9"` → `"a relational database"`,
  `"March 3rd 02:14 UTC"` → `"about two hours later"`. Use when the *role* matters, not the identity.
- **[aggregate]** - replace individual values with a group figure: per-customer counts → `"a few dozen"`.
- **[keep]** - explicitly keep. Write the reason. "Kept" that was never examined is how leaks happen.

The rule that catches most bad revocations: **distinct entities must stay distinct.** If three services
collapse into `[service]`, the causal chain dies. And a stand-in must not accidentally assert something false
— generalizing "we use the free tier" into "a small deployment" is a claim the document no longer supports.

When the chosen operation is a stand-in, there are two styles of it - the honest bracket `[username]` and the
reserved fake `alice@example.com` - and the artifact's genre (claiming truth vs demonstrating) decides which,
by rules ([`09`](references/09-placeholder-or-fake-data.md)).

## Step 3 - Apply one map, consistently

Build the substitution map once and apply it everywhere, including code blocks, filenames, and image
captions ([`02`](references/02-substitution-discipline.md)). Placeholder naming matters: `[customer-1]`,
`[payment-provider]`, `[REDACTED-SECRET]` read as deliberate; `XXX`, `REDACTED`, `█████` read as a document
being vandalized. Keep the map **outside** the shared artifact - it is the re-identification key, and it is
routinely leaked in a footnote, a commit message, or the same repo.

## Step 4 - Verify, do not trust your own diligence

Run the mechanical checks in [`04`](references/04-verification.md) before calling it sanitized:

- every original token absent - search the exact strings, including case variants and split forms;
- no high-entropy leftovers (keys, tokens, UUIDs, base64 blobs) and no precise dates or amounts that re-identify;
- metadata and non-text surfaces actually cleared;
- no partial redaction that reveals shape (`a**@acme.com` tells you the domain) - unless the artifact *is* a
  `/revoke partial` owner-view screen, where the shape is the point and [`07`](references/07-partial-masking.md)
  governs instead;
- the map is not anywhere inside the artifact;
- `scripts/revoke.py scan <file>` finds candidates you missed, and
  `scripts/revoke.py verify --map map.yaml --out sanitized.md` fails loudly on leaks, collisions, and
  placeholders used for two different entities.

Then the human test: **read the sanitized version once as a stranger.** Does the argument still hold? Would
you be able to act on it? List what was lost, honestly, in the record.

## Step 5 - Record it

Three lines minimum, more if the artifact is consequential: what was revoked and at which operation, which
audience it was cleared for, where the untouched original lives, and the re-check condition ("redo if the
incident gets a second root cause"). Put it where the project already keeps such records.

## Explicit modes - `/revoke partial` and `/revoke image`

Entered by name, each with its own reference read in full before acting. Neither relaxes Steps 0-5; they
change what the operations are applied *to*.

**`/revoke partial` - the mask that only the owner can finish.** For recovery/confirmation screens where
showing `A****` or `****4821` lets the owner recognize their own value while strangers get a fragment worth
nothing. It is deliberately the inverse of the Step-4 shape rule, valid only under the owner-viewer
assumption: head-vs-tail is a threat-model choice per field, masked parts keep their entropy, credential-class
values get no fragment at all, and the result must never be copied into a shared artifact
([`07`](references/07-partial-masking.md)).

**`/revoke image` - revoking pixels, not just prose.** Screenshots and pictures are first-class artifacts:
the agent looks, inventories every visible identifier (avatars, faces, name labels *wherever they repeat* -
header, quoted replies, toasts), and treats each region with an operation translated into pixels. Opaque
flattened blocks are the redaction; blur is de-identification and gets recorded as such; the file is re-encoded
with metadata and embedded thumbnails stripped; every frame of a multi-frame file is treated. With no region
list given, the default is the document default - revoke everything that identifies. The non-negotiable loop:
render to a temp file, look at the result (this agent has eyes; zoom the edges), fix coverage misses, and only
then produce the final ([`08`](references/08-image-redaction.md)). `scripts/revoke_image.py` is the default
mechanics - the script applies the spec, the agent decides it; any tool that meets the same obligations
(opaque paint, flatten, strip, every frame) is equally valid.

## Boundaries - these stop the job, not style it

Read [`06`](references/06-boundaries-and-misuse.md) before touching anything in this list.

- **Never to conceal.** Revoking to hide wrongdoing, dodge an audit, defeat a legal hold, or erase a required
  record is not sanitization. The artifact's *disclosure* is your subject; its *existence* is not.
- **Never strip protective content**: safety warnings, consent notices, license headers, deprecation dates,
  the reason a value must not be edited.
- **Never launder accountability out of a timeline.** Replace names with roles - `[on-call]`,
  `[database-owner]` - so *who did what* remains knowable while *who* stays private.
- **Never revoke data that is not yours to disclose.** If the artifact contains another party's personal or
  customer data and you lack authority, say so and stop; a sanitized copy handed to a third party is still a
  disclosure.
- **Never destroy the original.** Produce, don't overwrite.
- **No redaction theatre.** A document with six black boxes and one unique surviving detail is not sanitized.
  If you cannot revoke enough to make it safe, the answer is "this cannot be shared", which is a legitimate
  deliverable.

## References

| File | Owns | Read when |
|---|---|---|
| [`00-what-revoking-is.md`](references/00-what-revoking-is.md) | The five operations, what each preserves and costs, the meaning-survival rule, how this differs from polyglot and from anonymisation claims | Step 2, always |
| [`01-what-makes-an-artifact-specific.md`](references/01-what-makes-an-artifact-specific.md) | The inventory taxonomy, including innocuous-but-identifying categories and combinatorial leaks | Step 1 |
| [`02-substitution-discipline.md`](references/02-substitution-discipline.md) | Map construction, placeholder naming, entity distinctness, protecting code and config examples, guarding the map itself | Step 3 |
| [`03-leak-surfaces.md`](references/03-leak-surfaces.md) | Where data hides outside the prose: metadata, images, filenames, hashes, links, comments, tone | Step 1 and Step 4 |
| [`04-verification.md`](references/04-verification.md) | The mechanical and human checks, the residual-risk question, and how to report what was lost | Step 4 |
| [`05-purpose-calibration.md`](references/05-purpose-calibration.md) | Audience levels, what must survive at each, and the questions to ask when the destination is vague | Step 0 |
| [`06-boundaries-and-misuse.md`](references/06-boundaries-and-misuse.md) | The stop list: concealment, legal holds, protective content, accountability, third-party data, originals, theatre | Step 0 and whenever tempted |
| [`07-partial-masking.md`](references/07-partial-masking.md) | The owner-view mode: head/tail fragment choice as threat model, entropy floors, the never-for-secrets rule, why partial output must not leak into shared artifacts | Only under `/revoke partial` |
| [`08-image-redaction.md`](references/08-image-redaction.md) | Pixel revocation: visible-identifier inventory, block-vs-blur honesty, corner/edge coverage, embedded thumbnails and multi-frame traps, the temp-render-then-look loop | Only under `/revoke image`, or whenever an image is in the artifact set |
| [`09-placeholder-or-fake-data.md`](references/09-placeholder-or-fake-data.md) | The two stand-in styles and the genre question that picks between them, reserved name-spaces, the no-structure-inheritance rule, fake identifiers never fake evidence | Step 2, whenever a stand-in is chosen |

## Examples and script

Cases in `examples/` show the operations on real-shaped artifacts, including one where over-revoking killed
the point, and one where the leak was in a PNG's metadata. Read them after your own inventory, not instead of
it:

| Case | Artifact | The lesson |
|---|---|---|
| [`case-01`](examples/case-01-incident-report-to-public-postmortem.md) | incident report → public postmortem | keep causality, generalize infrastructure, drop the customer name entirely |
| [`case-02`](examples/case-02-production-config-to-reusable-snippet.md) | prod config → shared snippet | comments and example values leak as loudly as keys |
| [`case-03`](examples/case-03-ticket-thread-to-pattern-doc.md) | support thread → pattern documentation | roles instead of names; dates instead of timestamps |
| [`case-04`](examples/case-04-over-revoked-argument.md) | a spec that stopped making sense | meaning-survival failure, and the fix |
| [`case-05`](examples/case-05-screenshot-and-metadata.md) | screenshot + PDF hand-off | the non-text surface nobody re-reads |
| [`case-06`](examples/case-06-cannot-be-shared.md) | what "no viable sanitized version" looks like | reporting the stop instead of shipping a leak |
| [`case-07`](examples/case-07-partial-mask-recovery-screen.md) | account-recovery screen | head-vs-tail per field, the refused password fragment, prose around the masks re-identifying |
| [`case-08`](examples/case-08-chat-screenshot-image-revocation.md) | chat screenshot | block vs blur, the avatar corner that leaked past a tight box, the temp pass that caught it |

- `scripts/revoke.py` - `scan` finds candidate specific data (emails, URLs, IPs, keys, tokens, UUIDs, private
  key headers, paths, precise dates and money, internal hostnames) so your inventory is not memory-based;
  `verify` checks a sanitized file against a substitution map - leaks, split forms, high-entropy leftovers,
  placeholder collisions, two entities sharing one placeholder, the map itself being embedded. Exit 0 clean,
  1 findings, 2 usage or read error. No argument runs the self-test - nine verify fixtures plus four scan
  checks, thirteen in total. On Windows use `python`, not `python3`. Output is ASCII.
- `scripts/revoke_image.py` - the pixel mechanics for `/revoke image`: `info` lists frames and the metadata
  surface, `redact` applies a region spec (block/mosaic/blur, padded boxes, background-matched block color),
  strips metadata, flattens, re-encodes, treats every frame, and refuses to write over the original; `check`
  reports metadata/thumbnail findings on a produced file. Needs Pillow in a **project-local venv** (never the
  global interpreter - the script prints the exact commands); any other tool meeting the same obligations
  works too, the loop matters more than the library. Exit 0/1/2 as its sibling. No argument runs the
  self-test - synthetic avatar+name fixture, seven checks. On Windows use `python`, not `python3`.
  **Verification status:** self-test and a real four-variant run (block/blur x normal/partial on a chat
  screenshot) executed against Pillow 13.0.0 in a temp venv on 2026-11-06; the temp-inspection pass caught
  and fixed a real coverage miss, so the loop it documents is the loop that worked.
