# Voice and tone — the same facts, restated

Research-grounded (brand-voice guides and developer style guides converge on the same model).
Options in [brackets] are examples, not a closed menu; hybrids and unlisted voices are valid.

## The model

- **Voice** is the project's stable personality — how it sounds in *every* text. Constant.
- **Tone** is the voice adapted to one reader and one situation — warm in a tutorial, neutral
  in a reference, brisk in troubleshooting, confident in a pitch. Variable, per context.
- A README therefore has one *voice* (the project's) spoken at one chosen *tone-register*
  (the reader-and-purpose the user picks). Different README styles are not different truths —
  they are the same facts, reordered and re-registered.

A usable voice profile, once per project: a purpose statement, 3–5 behavioral principles
("precise, plain, confident, never condescending"), and short preferred/banned word lists
("preferred: 'installs in', 'runs on'; banned: 'seamless', 'cutting-edge', 'powerful'").
If the project already has one (docs style guide, CONTRIBUTING), adopt it; don't invent a rival.

## What actually changes when the voice changes

Nothing in the fact layer. Five levers only:

| Lever | Minimal-setup | Engineering | Deep DX | Marketing/showcase |
|---|---|---|---|---|
| **Leads with** | install command | what it is + install | architecture map, build matrix | the problem lived, then the payoff |
| **POV / verbs** | imperative ("run", "set") | indicative + imperative mix | imperative + explanatory | second person's future ("you get", "stop doing X") |
| **Sentence length** | shortest | medium | longer where mechanism needs it | short, rhythmic, benefit-shaped |
| **Evidence adjectives** | none | only measured ones ("42 kB bundle") | trade-off adjectives ("verbose but debuggable") | strongest *provable* ones, or none |
| **Sections kept** | name, why-in-2-lines, prereqs, install, run, config-minimum | + usage, limits, testing | + build/dev flow, branch & channel navigation, contribution path, release rhythm, who-depends-on-what | + capabilities as outcomes, visuals, comparison vs status quo, install kept short and late |

The four registers are a *menu of emphases*, not templates: content still comes from repository
evidence only (sections 2, 6, 7 of SKILL.md bind every voice).

## Voice-specific guardrails

- **Marketing/showcase voice does not buy the right to invent.** Every aspirational line still
  traces to evidence: features implemented, benchmarks that exist, screenshots that exist. Benefit
  framing is *selection and ordering*, never claim inflation. (The skill's "no generic AI writing"
  rule still applies: no "seamless/robust/cutting-edge" without concrete meaning.)
- **Deep DX voice must not bury the quick start.** The contribution-heavy structure (build, branch
  and channel navigation, how to run tests, how to get changes reviewed) lands *after* a working
  install — a 10-minute-to-first-compile README is a failed README regardless of ambition.
- **Minimal voice may not omit blockers** (env vars, versions, credentials the install genuinely
  needs) — "minimal" is about scope of prose, not accuracy.
- **Engineering voice (the default when the repo gives no stronger signal)** stays neutral and
  direct: active voice, name the thing not the cleverness, repeat a term rather than vary it for
  style — clarity beats elegance in developer docs.

## The restatement technique (write once, cast into any voice)

To show the user options or switch voices on an existing README without re-researching:

1. Extract the **fact core**: bullet list of proven claims (what it is, does, requires, measures).
2. Choose the target register; apply only the five levers above — reorder, re-cut POV/verbs,
   resize sentences, re-select adjectives, re-select sections.
3. Diff the fact cores before and after: a restatement that adds, drops, or softens a fact is a
   rewrite, not a voice change. Never let tone edits smuggle claim edits.

## The one question to ask (before drafting)

"Which README do you want for this project?" — offered as [bracketed] styles with one-line
descriptions, recommendation first, trade-off visible:

- **[Minimal setup]** — get them installed in one screen. Cheapest to maintain; says nothing about
  why to choose this project.
- **[Engineering overview]** — what it is, install, usage, limits. The safe default for libraries.
- **[Deep developer experience]** — the above plus build-from-source, branch/channel navigation,
  contribution and review path. For projects expecting outside contributors or multiple release
  channels.
- **[Marketing showcase]** — the project presented as a product: problem, outcomes, visuals. For
  README-as-landing-page repos (open-source with users to win). *Claims stay evidence-bound.*
- **[Hybrid]** — e.g. showcase front half + deep-DX second half; valid and common — state the
  seam clearly ("Contributors:" heading divides the voices).

Skip the question when the repo already answers (an existing README's register, a docs site
splitting jobs), when the user named the style, or when the ask is a small fix. If positioning is
open and the *choice* would materially change the file, it is exactly one of the intent-dependent
decisions worth asking (SKILL.md §10).
