# Census briefs — dispatch contract for the read-only auditors

Two dispatch paths; pick one, never both:

- **crosscheck installed and the corpus needs orthogonal lenses:** delegate discovery to it, take
  its findings document into Stage 2. deep-audit then owns only decisions, plan, waves.
- **Otherwise, brief the census agents directly** with the contract below (Explore-type or
  equivalent read-only agents; fall back to general agents told to edit nothing).

## Slice design

Slices must not overlap in AREA, and each agent owns one ANGLE plus one surface set. A proven 3-way
split for a mixed corpus:

1. **Structure auditor:** taxonomy/tier boundaries — which passages live in the wrong kind of home.
2. **Domain auditor:** one content domain end-to-end (e.g. money, identity, sync) across every
   artifact type that touches it, including ground-truth code/prototype/config.
3. **Governance auditor:** the surfaces the first two skip by design — decision ledgers, rulebooks,
   indexes, changelogs, assumption lists, entry tools' own state; plus the drift sweep against the
   first two's domains.

Every brief states what the OTHER agents cover, so nobody re-audits it and gaps get named instead of
assumed covered.

## Brief skeleton (fill, do not improvise)

```
=== MANDATORY CONTEXT (project rulebook applies; read the listed docs in full) ===
Phase/scope: <DR/IP, what is provisional>.
You are READ-ONLY. Do NOT edit, create, or delete anything. A write tool is unavailable to you —
your report goes INLINE in your returned result; do not attempt to file it.
Teammates may be editing this tree concurrently: report only what you read; never "fix" or revert.

=== TASK ===
Corpus: <exact paths>. Breadth: VERY THOROUGH — read files end to end, not excerpts, on everything
in scope; grep is for locating, reading is for judging.
Hunt defect classes: <list from defect-taxonomy.md, or the file path + "read it first">.
Cite file:line for every finding; an uncited finding is dropped.
Do not propose edits — propose DESTINATIONS (where content belongs), the plan owner decides moves.

=== OUTPUT CONTRACT ===
<report format from defect-taxonomy.md> +
Questions for the owner: anything undecidable from the corpus comes back as a question with options.
Never bake an assumption into a destination.
What is FINE: name the correct content you deliberately did not flag, so the plan never churns it.
Returned report: dense, under N words; full tables allowed; no narrative padding.
```

## Why each clause exists (learned the hard way)

- **Inline-only:** Explore-type agents have no write tool; a brief demanding a report file produces
  an apology and an inline dump anyway — write the contract correctly the first time.
- **"grep locates, reading judges":** pattern-matched findings without the surrounding read generate
  false positives on history lines (strikethroughs, changelog entries, deliberate counter-examples).
- **"destinations, not edits":** parallel writers corrupt each other's state and the merge; parallel
  READERS never can.
- **"What is FINE":** without it, the next execution pass re-litigates correct content and the audit
  damages the corpus it audited.
- **"Questions for the owner":** the census agent's guess becomes the plan's silent decision — the
  whole point of deep-audit is that weight-bearing calls go to the human.
- **Rulebook binding:** subagents inherit the project's own agent rules (its rulebook/AGENTS file)
  exactly like the main agent; scope narrows actions, never obligations.