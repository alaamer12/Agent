# Worked example - a project that speaks three vocabularies

A vision app named **Basr** (بصر, Arabic for sight/vision). Docs are English, the mobile UI strings are Arabic,
chat logs quote users in Franco, and one team member insists on writing "basr" lowercase, another "Al-Basr". A
new agent session starts on "add an export to the eye list".

## The session that learns a term - self-invoke, add in the same task

The golden rule fires first: `eye` is ordinary English, so the reflex is "not a term". But here "eye" does not
mean the dictionary organ - it names one camera+detector pipeline instance. **Meaning diverges from the
dictionary, so it earns a block**, exactly like a foreign word would.

The agent finds `eye` used three ways: `listEyes()` in code, "the Eye" in a design doc, and `عين` in a UI
string - and the export task needs to know which one it is writing about.

1. It reads enough to decide the referent (one camera + detector pipeline instance) - but *what the word means
   to the team* it does not guess.
2. Adds the block under its letter, meaning marked pending where evidence ends:

```markdown
## E

**eye**
Also: eyes, the Eye, عين

pending - not assumed. Code uses it for one camera+detector pipeline instance (`core/Eyes.ts`); the design
doc may mean the whole vision feature.

Used in: `core/Eyes.ts`, `docs/design.md` §2 ("the Eye")
```

3. Asks the one question the answer changes: *"the design doc says 'the Eye' where the code says pipeline
   instance - same thing, or the doc means the whole vision feature?"* The user's answer completes the block
   in the same task - the pending line replaced by:

```markdown
Same as the code sense: one camera + detector pipeline instance. "The Eye" in design docs is the whole
vision feature (all eyes plus the shared scheduler) - do not use `eye` for the feature, it is not an eye.

Used in: `core/Eyes.ts` (canonical `VisionInstance`), `docs/design.md` §2
```

## The Franco surprise

A support-log analysis quotes a user: `"kifak basir shoo shaghel"`. An agent without the glossary treats it as
noise or machine-translates it badly into the ticket. The blocks record user-facing language as such - and one
of them is the whole argument for this skill existing:

```markdown
## K

**kifak**
Also: كيفك, kifik

"How are you" (Franco spelling of Arabic). Appears only in user chat logs - never project vocabulary; do
not normalize it into identifiers or docs.

Used in: `support/logs/*` (user messages only)


## B

**basir**
Also: بصير, baseer, bshir

"I will see / look" - a Franco verb form of the same root بصر that names this app. **Different word from
`Basr` despite the shared root**: if a user says it, they are talking about looking at something, not the
product.

Not to confuse: Basr (the app).
Used in: `support/logs/*` (user messages only)
```

`basir` and `Basr` collide at first glance, and only listed forms plus one "Not to confuse" line keep an agent
from "helpfully" normalizing a user's word into the product name.

## The audit - one concept, five names

`/glossary audit` over the docs folder finds `Basr`, `basr`, `Al-Basr`, `the app`, `Baser` (a typo in three
files). The merge map shown before any edit:

```text
term          | forms found                       | canonical | action
--------------+-----------------------------------+-----------+----------------------------------
the vision app| Basr, basr, Al-Basr, the app, Baser | Basr      | keep Basr; fix "Baser" typo rows;
              |                                     |           | "the app" stays fine in prose,
              |                                     |           | not as a defined term
```

The result block:

```markdown
## B

**Basr, بصر**
Also: basr, al-basr; "Baser" appears in 3 docs as a typo - fix, do not enshrine

The project: a real-time vision app - camera ingestion, on-device detection, alerts. The name is the Arabic
word for sight/vision, which *is* the app's meaning, so both forms are the canonical name and both are
listed together.

Not to confuse: basir (a Franco verb, "I will see") - user speech, not the product.
Used in: everything; identifier style is `Basr` capitalized.
```

## Filing rules that a fresh agent always forgets

The project has a scratch-data store everyone calls **"the Pit"**, and Arabic UI strings the team quotes
directly. Both rules bite here:

```markdown
## P

**Pit, The**

The scratch area for throwaway analysis artifacts: scripts, dumps, screenshots a task produced and no one
owns. Created freely during debugging, deleted before the task is called done. Filed under P - read "the
Pit"; the article never files the word.

Used in: `scratch/` (gitignored), debugging rules in AGENTS.md §8
```

Two things the block shows: an article-led name filed by its head noun (`Pit, The` under `## P`), and the
definition written in the language the project argues in - here English, because code and docs are English;
the same Pit in an Arabic-speaking project gets an Arabic definition, and English never sneaks in as the
"neutral" voice.

The typo fix is a documentation edit (or the `document` skill's reorganize job if a file needs restructure);
glossary records the alias and flags the typo, it does not sweep the repo.

## Outgrowing the section

After a few months the list is 23 blocks and the `# Glossary` section is past its ~50-line budget. The move:

- full alphabetical list (`## A` … `## Z`) -> `GLOSSARY.md` at the docs location the project already uses;
- AGENTS.md keeps `# Glossary` as obligations + pointer:

```markdown
# Glossary
- Use the canonical form of every defined term in new writing and identifiers.
- Every spelling - native script, transliteration, Franco - is listed; look up before guessing.
- Bilingual names carry both forms on the term line; article-led names file under the head noun (`Pit, The`).
- A term not in the list is either ordinary language or missing: if the task needs it, add it in the same task.
- Read: GLOSSARY.md (alphabetical blocks: term (spelled-out acronym), meaning, Used in)
```

The cheap file stays cheap; the detail is one deliberate `Read` away - and every form still resolves to one
block either way.
