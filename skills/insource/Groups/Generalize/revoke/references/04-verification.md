# Verification - proving you removed it, and reporting what you broke

Two questions, and both have to be answered before the artifact leaves. Did anything survive, and does the
document still do its job? Most self-assessed sanitization passes the first question in the reviewer's head
and fails the second silently.

## A. Leak checks (mechanical, run them)

1. **Token absence.** Every original string in the map, searched in the output - case-insensitively, and
   including split forms: `acme-corp`, `Acme Corp`, `acme_corp`, `ACME`, `acme.corp`. The script does this;
   `grep -i` alone misses compounds.
2. **Shape scan.** Emails, URLs, internal hostnames, IPs, UUIDs, private-key headers, JWT-shaped strings,
   long base64 runs, key prefixes, connection strings. Anything high-entropy is presumed a secret until named.
3. **Residual numbers.** Precise dates, timestamps, counts, money, percentages. Each is a candidate
   combinatorial identifier at the audience level you chose.
4. **Partial-mask audit.** Any `***` or truncated form: does the surviving shape confirm a guess?
5. **Placeholder hygiene.** Two entities sharing one placeholder (distinctness collapse), one entity with two
   placeholders, a placeholder that is a substring of its original, the map embedded anywhere in the artifact.
6. **Non-text sweep.** Metadata, filenames, images, links, code comments, footnotes
   ([`03`](03-leak-surfaces.md) has the list).
7. **Diff review.** Read the change list rather than re-reading the document; a diff of 40 substitutions is
   reviewable, a rewritten 8-page doc is not.
8. **Independent pass.** If the artifact matters, someone who was not in the room reads it and says who they
   think it is about. Their success is your report.

## B. Meaning checks (the argument survived test)

- **Cold read.** Read the sanitized version with fresh eyes and, for each section, answer: could a reader act
  on this? Where no, name it.
- **Distinctness test.** Replace each placeholder in your head with "thing A/B/C" - does the causal chain
  still resolve? If the timeline collapses, you merged entities that had to stay separate.
- **Truthfulness test.** Every generalized statement must remain true of the original. "Free tier" → "a small
  deployment" is an invented claim; "a low-traffic configuration" is defensible if volume was actually low.
- **Quantitative lesson test.** If the lesson involves magnitude, some magnitude must survive: rounded
  (`~2h`), banded (`tens of minutes`), or relative (`40x the p99`).
- **Code test.** If the artifact contains runnable material, does it still run or compile as an example?
  Placeholder'd code that silently changed behavior is a worse trap than a leak.

## C. Residual risk, stated plainly

Nothing reaches zero. Say which one you accepted:

```text
RESIDUAL: low | medium | high - one line why
  e.g. "names and hosts revoked; the incident sequence is distinctive enough that
        a former employee of the customer could still recognise it"
```

If residual risk is medium or high for the stated destination, the correct output is a recommendation to not
ship this version, plus what would make it safe - fewer details, a merged narrative, or a rewritten abstract
that keeps the lesson.

## D. What to report

Compress to something a reviewer can check in a minute:

```text
ARTIFACT  : <original> -> <sanitized>        CLEARED FOR: <destination level>
INVENTORY : <n> specific items                KEPT-EXPLICITLY: <n> with reasons
MAP       : redacted <n> | pseudonymized <n> | generalized <n> | aggregated <n>
CHECKS    : token absence <pass> shape scan <pass> metadata <pass> meaning read <pass>
LOST      : <what the reader can no longer do>  e.g. "exact p99 numbers, per-customer volumes"
RESIDUAL  : <level> - <one line>
ORIGINAL  : untouched at <location>           MAP RETAINED: with the source, not here
```

The `LOST` line is the one agents omit and reviewers need. Sanitization always costs the reader something;
naming the cost is what makes the artifact trustworthy rather than merely clean.

## E. When verification is not yours to do

Personal data, security findings not yet disclosed, and regulated content carry decisions above your
authority. Produce the sanitized draft and the residual-risk statement, hand both to whoever owns the
disclosure, and stop there ([`06`](06-boundaries-and-misuse.md)). A confident "it's anonymised now" from an
agent is not a clearance.
