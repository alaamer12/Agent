---
name: revoke
version: 1.1.0
author: Amr
specialized: none
description: 'Sanitise an artifact by revoking what ties it to a specific project, person, customer or deployment: the substance survives, the identity does not. Use when a report, spec, config, log or screenshot must leave its origin: inventory what is specific (names, ids, endpoints, secrets, dates, paths), choose per item [redact] [pseudonymize] [generalize] [aggregate] [keep] under one substitution map, verify nothing leaks (token/entropy sweeps, metadata, the map), and check the argument survives. No findings, no changes: with nothing identifying, the artifact ships byte-identical with a clean report; cosmetic rewording is editing, not revocation. Modes: /revoke partial masks values to fragments (A****) for owner-view screens - never secrets; /revoke image paints opaque blocks over visible identifiers (blur is not revocation), strips metadata. Not polyglot (stack-neutral); revoke is identity-neutral. Never to hide wrongdoing, evade a legal hold, strip safety notices or erase accountability; the original stays intact.'
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

**The third principle, aimed at the most common failure in practice: no findings, no changes.** An inventory
and scan that surface nothing identifying are a complete, correct result. The artifact ships **byte-identical**
and the deliverable is the clean report. Generalizing harmless public product names, softening numbers that
identify nobody, or rewording for "transparency" touches no identity tie — that is editing dressed as
sanitizing, and it is never the output of this skill ([`06`](references/06-boundaries-and-misuse.md)).

## Not the same as `polyglot`

`polyglot` generalizes across technology, `revoke` across identity and context, and the order between them is
fixed. The distinction, and why neither pass makes the other safe: [`00`](references/00-what-revoking-is.md).

## Step 0 - Where is it going? That sets the budget

The destination decides how far to revoke and what must survive; the five destination levels, each with its
aggressiveness and its survivors, are tabulated there with the detail
([`05`](references/05-purpose-calibration.md)).

If the destination is unknown, ask one short question before revoking anything. A different audience is a
different document.

## Step 1 - Inventory what makes it specific

Walk the taxonomy in [`01`](references/01-what-makes-an-artifact-specific.md) and list every item, including
the ones that feel innocent. Two categories people miss, and they are the expensive ones:

- **Non-text surfaces** - filenames, image contents, document metadata, commit hashes, embedded paths,
  hyperlinks, footnotes, code comments ([`03`](references/03-leak-surfaces.md)).
- **Combinatorial identifiers** - nothing in "our 40-engineer fintech in Austin, migrated in Q3 2025" is
  secret, and the combination names the company. Uniqueness, not secrecy, is the test.

**Zero rows is a valid inventory outcome.** If the taxonomy walk and `scripts/revoke.py scan` surface nothing
that pins the artifact to an origin, the run ends here: skip Steps 2-4, hand back the artifact unchanged, and
record the clean result - what was scanned, which surfaces were swept ([`03`](references/03-leak-surfaces.md)),
the date ([`04`](references/04-verification.md) §D has the clean variant). Public product names, generic role
labels and standard ports are [keep] material ( [`01`](references/01-what-makes-an-artifact-specific.md) §9),
not work to invent.

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

- **`/revoke partial`** - the mask that only the owner can finish: what the mode is, in short, and its full
  discipline ([`07`](references/07-partial-masking.md)).
- **`/revoke image`** - revoking pixels, not just prose: what the mode is, in short, and its full discipline
  ([`08`](references/08-image-redaction.md)).

## Boundaries - these stop the job, not style it

Read [`06`](references/06-boundaries-and-misuse.md) before touching anything in this list: the boundaries, each
in one line, are recorded there above the full stop table.

## References

| File | Owns | Read when |
|---|---|---|
| [`00-what-revoking-is.md`](references/00-what-revoking-is.md) | The five operations, what each preserves and costs, the meaning-survival rule, how this differs from polyglot and from anonymisation claims | Step 2, always |
| [`01-what-makes-an-artifact-specific.md`](references/01-what-makes-an-artifact-specific.md) | The inventory taxonomy, including innocuous-but-identifying categories and combinatorial leaks | Step 1 |
| [`02-substitution-discipline.md`](references/02-substitution-discipline.md) | Map construction, placeholder naming, entity distinctness, protecting code and config examples, guarding the map itself | Step 3 |
| [`03-leak-surfaces.md`](references/03-leak-surfaces.md) | Where data hides outside the prose: metadata, images, filenames, hashes, links, comments, tone | Step 1 and Step 4 |
| [`04-verification.md`](references/04-verification.md) | The mechanical and human checks, the residual-risk question, and how to report what was lost | Step 4 |
| [`05-purpose-calibration.md`](references/05-purpose-calibration.md) | Audience levels, what must survive at each, and the questions to ask when the destination is vague | Step 0 |
| [`06-boundaries-and-misuse.md`](references/06-boundaries-and-misuse.md) | The stop list: concealment, legal holds, protective content, accountability, third-party data, originals, theatre, and why a clean empty run is a complete output | Step 0 and whenever tempted |
| [`07-partial-masking.md`](references/07-partial-masking.md) | The owner-view mode: head/tail fragment choice as threat model, entropy floors, the never-for-secrets rule, why partial output must not leak into shared artifacts | Only under `/revoke partial` |
| [`08-image-redaction.md`](references/08-image-redaction.md) | Pixel revocation: visible-identifier inventory, block-vs-blur honesty, corner/edge coverage, embedded thumbnails and multi-frame traps, the temp-render-then-look loop | Only under `/revoke image`, or whenever an image is in the artifact set |
| [`09-placeholder-or-fake-data.md`](references/09-placeholder-or-fake-data.md) | The two stand-in styles and the genre question that picks between them, reserved name-spaces, the no-structure-inheritance rule, fake identifiers never fake evidence | Step 2, whenever a stand-in is chosen |

## Examples and script

Cases in `examples/` show the operations on real-shaped artifacts, including one where over-revoking killed
the point, one where the leak was in a PNG's metadata, and one where the correct output was no changes at all.
Read them after your own inventory, not instead of it:

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
| [`case-09`](examples/case-09-clean-exit-no-changes.md) | technical explainer with public names only | empty inventory ships the artifact byte-identical with a clean report |

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
