---
name: reveal
description: 'Competitive-intelligence investigation into how unique a project idea actually is: how much of it already exists, who built it, how well it is working, and what genuinely differentiates the proposal. Breaks the idea into search axes (never one query), discovers existing implementations across engines, code hosts, app stores, startup directories, communities, forums, archives and native-language sources - obscure and defunct included, not just the famous names - then investigates each competitor across ten dimensions (name, features, market, language/localization, history, user base, business model, technology, positioning, viability), scores similarity 0-100 with reasons, assesses uniqueness from eight lenses, and ends in a structured, evidence-backed landscape report with a direct verdict. It is an investigation skill, not a validation or encouragement one: it reports reality even when disappointing, and never claims uniqueness from a failure to find a competitor. Triggers: "/reveal", "is this idea taken/already built", "how unique is my project", "find competitors for X", "competitive landscape for X", "has anyone built this". Not a general research dig (mine), not choosing between known options (thebest), not a stack recommendation (techstack), not a local-codebase audit (exmaine); its delegation reuses the subagent brief shape.'
when_to_use: The user wants to know how original a project idea is, who the real competitors are (including ones they have not heard of), how differentiated and viable the idea is against what already exists, or asks to "reveal" / investigate the market for an idea before building it. Also /reveal.
argument-hint: "[project idea, or a path to a brief/README] + [target countries / languages / platforms if known]"
---

# /reveal - find out what already exists, and where the idea genuinely stands

The one question Reveal answers, and answers with evidence rather than reassurance:

> **How much of this idea already exists, who has implemented it, how successful are they, and what makes
> the proposed project different?**

Everything else - the ten dimensions, the similarity score, the uniqueness lenses - is scaffolding to make
that answer honest and checkable. Reveal is not here to tell the user their idea is great or dead; it is
here to show where it actually sits in the world that already exists.

**The load-bearing stance (read it before anything else):** Reveal is an investigation, not a validation or
encouragement skill. Its job is to uncover reality even when the findings disappoint. The single worst
failure it can commit is to report "unique" because it stopped looking early, or to report "taken" because
something shares a name. [`00`](references/00-what-reveal-investigates.md) holds the full never-list and why
each prohibition exists.

Read `references/01` through `08` as the actual method; this file is the map, not a summary - nothing here is
restated there in less detail, and the report shape lives in `assets/`.

## The shape of an investigation

Five stages, in order, each a reference:

1. **Understand the project** - extract its concepts, features, audience, markets, model; break it into many
   search axes, because one query finds only the famous top result
   ([`01`](references/01-understand-the-project.md)).
2. **Discover what exists** - broad, multi-source, multi-language, diminishing-returns search across engines,
   code hosts, app stores, startup directories, communities, archives; the obscure and defunct matter as much
   as the well-funded ([`02`](references/02-discover-projects.md)).
3. **Investigate each competitor across ten dimensions** - name, features, market, language, history, user
   base, business model, technology, positioning, viability - with sources and dates on every claim
   ([`03`](references/03-the-ten-dimensions.md)).
4. **Score similarity and assess uniqueness** - a 0-100 similarity per competitor with stated reasoning,
   competitor classification, then the eight-lens uniqueness verdict that refuses to confuse "many
   competitors" with "bad opportunity" or "no competitors" with "good idea"
   ([`04`](references/04-similarity-analysis.md), [`05`](references/05-uniqueness-assessment.md)).
5. **Report** - the fixed 10-section landscape report with the direct verdict questions answered, built from
   the evidence ledger, not from memory ([`06`](references/06-research-quality-and-evidence.md),
   [`08`](references/08-final-report.md), `assets/report-template.md`).

Run it in whatever the harness allows: parallel subagents when available, the same responsibilities
sequentially when not - the *research duties are mandatory, the delegation is conditional*
([`07`](references/07-delegation-and-harness.md)).

## Where everything lives

| File | Owns | Read when |
|---|---|---|
| [`00-what-reveal-investigates.md`](references/00-what-reveal-investigates.md) | The purpose, the fundamental question, what Reveal is and is not, the operating principles and the never-list | Always, first - it sets the stance every later choice inherits |
| [`01-understand-the-project.md`](references/01-understand-the-project.md) | Phase 1: the extraction checklist, breaking one idea into many search axes, what to ask the user before assuming | Start of every run |
| [`02-discover-projects.md`](references/02-discover-projects.md) | Phase 2: the source map (engines, code hosts, stores, directories, communities, archives), multi-language search, the diminishing-returns stopping rule, access honesty | Phase 2, and again whenever discovery feels thin |
| [`03-the-ten-dimensions.md`](references/03-the-ten-dimensions.md) | Phase 3: dimensions A-J, what each must find, the traps (founding vs launch, downloads vs MAU, company location vs market dominance) | When investigating each competitor |
| [`04-similarity-analysis.md`](references/04-similarity-analysis.md) | The ten similarity axes, the 0-100 bands, per-score reasoning, direct/indirect/alternative/adjacent classification | After the dimensions are filled |
| [`05-uniqueness-assessment.md`](references/05-uniqueness-assessment.md) | The eight uniqueness lenses and the two confusions they exist to prevent | Before writing the verdict |
| [`06-research-quality-and-evidence.md`](references/06-research-quality-and-evidence.md) | The research standards, primary-over-secondary sourcing, the verified/estimated/assumed labels, the evidence ledger | Throughout, and as the final gate before the report is called done |
| [`07-delegation-and-harness.md`](references/07-delegation-and-harness.md) | The research responsibilities, harness-conditional parallelism, adaptive prioritization, cross-research validation, completion criteria | When planning how to run the investigation |
| [`08-final-report.md`](references/08-final-report.md) | The 10 report sections and the eight verdict questions | Phase 5 |
| [`assets/report-template.md`](assets/report-template.md) | The structured report skeleton to fill from the ledger | Writing the report |
| [`assets/evidence-ledger-template.md`](assets/evidence-ledger-template.md) | The per-finding evidence table (claim, URL, date, label, estimate method) | Recording findings, from the first competitor |
| [`examples/case-01-...md`](examples/case-01-regional-gap.md) | A worked investigation where the idea is not unique globally but is underserved in the target market/language | Before scoring, to calibrate the "many competitors, still an opportunity" case |
| [`examples/case-02-...md`](examples/case-02-name-vs-product.md) | A worked case where a name collision and a feature overlap are correctly separated from real competition | When tempted to over- or under-count a competitor |

## Non-negotiables, stated once here so they survive any delegation

- **Broad discovery before conclusions; stop on diminishing returns, not on a comfortable count.**
- **Every claim has a source and a date; every number is labeled fact / estimate / assumption.** Never
  present downloads, visits, followers or stars as active users.
- **Never fabricate a competitor or a statistic to fill a gap.** Report the gap and the limitation instead.
- **Respect access rules; never pretend to have searched private or gated content you could not reach.**
- **Uniqueness is not the same as opportunity, in either direction** - the verdict must hold both truths at
  once.
- **The original spec of what the user is building is not edited by Reveal** - it investigates and reports;
  it does not decide for the user.
