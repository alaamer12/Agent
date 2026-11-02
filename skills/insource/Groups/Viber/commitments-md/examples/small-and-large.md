# Small and large - both placements worked

> The domains here are illustrative - a website, a content platform, an on-device app. The same shapes apply
> to a CLI tool, a game, a data pipeline or a library; only the dimensions' names change.

## A. Small: "I just want maximum SEO"

The user's whole priority set is one dimension - SEO - and they explicitly do not care about the
implementation cost ("doesn't even care if the site is built in an obscure language"). That fits in
AGENTS.md, as three lines, and needs no COMMITMENTS.md.

```markdown
## 1. Agent Instructions

- ...existing rules...

### Commitments
- Maximum SEO outranks every implementation preference: crawlable content, semantic markup, fast first
  paint. Implementation language and framework are free choices, judged only by this.
- Bar: every content page is fully readable with JavaScript disabled, and appears correctly to a crawler.
```

The document stayed where rules live; the cost of the priority (limited framework freedom) is implied and
small enough to sit in the rulebook. No separate file, no pointer.

## B. Large: a content platform with several competing goals

Input, from a discovery conversation: "Content must rank well on search. It has to be accessible - we serve
people with slow phones and screen readers. We want to ship the reading experience in two months. Long term
we care about cost, and the team knows one framework well but not the fast new one."

This is big: several dimensions, real tensions, phases, bars - COMMITMENTS.md, with a pointer from
AGENTS.md.

### The interview (the questions that mattered)

1. **SEO vs interactivity:** "When rich client interactivity fights crawlable content, which wins?" ->
   SEO wins; SSR-first, interactivity as islands; accept more build complexity.
2. **Ecosystem vs performance (the SolidJS-vs-React shape):** "The team knows one framework; a faster one
   with a thinner ecosystem exists. Which wins?" -> Team knowledge/DX wins; accept slower runtime than the
   faster option; revisit at the scale phase.
3. **Time-to-market vs polish:** "Two months for the reading experience - what may ship rough?" -> Perf and
   a11y pass at a basic bar; search and reading flow must be complete; polish later.
4. **Hard constraints:** "What is never sacrificed?" -> Accessibility floor (keyboard + screen-reader
   usable), content crawlability, user privacy (no third-party trackers).
5. **Compatible pairs:** SEO and accessibility pull together here; listing that stops future tasks from
   trading one for the other.

### The resulting COMMITMENTS.md (excerpt)

```markdown
# Commitments — <content platform>

These are the trade-offs this project resolves the same way every time.

**Last reviewed:** 2026-10-31

## Never sacrificed

- Accessibility floor: every reading surface is keyboard- and screen-reader-usable - the audience includes
  them by design, not as a later upgrade.
- Crawlability of all content - it is the product's growth path.
- No third-party trackers on reading pages - user privacy is not an optimization.

## Priorities, by horizon

**Now (MVP):**

- [time-to-market] > [polish] | horizon: MVP | accept: rough edges in animation and micro-interactions | bar: reading flow + search crawls complete in 2 months
- [SEO] > [client interactivity] | horizon: MVP | accept: SSR complexity, more build steps | bar: every article readable with JS disabled
- [team DX] > [raw runtime performance] | horizon: MVP | accept: slower runtime than the fastest option | bar: team ships on the known framework
- [accessibility] co-primary with [SEO] | horizon: MVP | accept: no trade - both are enforced | bar: keyboard + screen reader passes on reading pages

**Later (v1, scale):**

- [cost] enters the ranking | bar: cost per 1k reads measured
- runtime performance revisited only if reads-per-second targets are missed

## When two goals collide

| When | Choose | Accept | Why |
|---|---|---|---|
| Rich interactivity vs crawlable content | crawlable content | heavier build (SSR) | growth depends on search |
| Faster framework vs known framework | known framework | slower runtime for now | team velocity is the bottleneck at MVP |
| Polish vs shipping in 2 months | ship | rough animation | learning before beautifying |

## Pursued together

- Accessibility + SEO - semantic markup serves both; neither is sacrificed for the other.
- Accessibility + performance - lean pages help both; no trade is allowed between them.

## Measurable bars

| Dimension | Bar |
|---|---|
| SEO | all content crawlable with JS disabled |
| Accessibility | keyboard + screen reader pass on reading pages |
| Time-to-market | reading flow live in 2 months |

## Open questions

1. What is the runtime performance bar at scale (reads per second), and when does it start to outrank DX?
2. Is "cost" a monthly budget number, or a per-read target?
```

And AGENTS.md gains one line in its mandatory context: a row pointing at COMMITMENTS.md with the reading
duty ("read before choosing an approach that trades these dimensions").

### Why this file is not the idea file

It never says what the product is - only **how decisions are made when goals compete**. The idea says "a
reading platform for X"; the commitments say "when SEO and interactivity collide, SEO wins, and here is the
price". Different documents, different owners, different arrows in the same decisions.

## C. A different domain: an on-device translation app

No web anywhere. The competing goals: translation accuracy, battery, offline capability, and a six-week
MVP. The user's decision: works fully offline (non-negotiable), accepts lower accuracy for long sentences
than a cloud model would give, and accepts a bigger install for the offline model. Small enough to live in
AGENTS.md:

```markdown
### Commitments
- Offline-first is a hard constraint: the app never requires the network for translation.
- Accuracy > time-to-market, except: ship the MVP with long-sentence quality below target and improve it
  after launch (accepted gap, tracked).
- Battery > accuracy for background features only; foreground translation may use full compute.
- Bar: a 10-word sentence translates in under 300ms on the reference device; model installs under 120 MB.
```

Four lines, one dimension cluster, no tables, no phases beyond MVP - the rulebook is the right home. The
same content as a big set (multiple languages, device tiers, per-phase bars) would become COMMITMENTS.md.
