---
name: glossary
description: 'Maintains one unambiguous project vocabulary in alphabetical letter blocks. Golden rule for what earns a block: the word as used here carries more than the dictionary sense - redefined or made-concrete ordinary words (''eye'', ''minimal''), project coinages (''Melody'' for a workflow), private-sense abbreviations, transliterations (Basr, بصر), Franco spellings, names/codenames. The project''s own language is the canon, never English; bilingual terms show both forms together; article-led names file under the head noun (''Pit, The'' under P). Each block: term (acronym spelled out), all forms, a 2-5 line meaning, ''Used in:'' refs; keep identities generic - run ''revoke'' before the glossary leaves the project. Lives in AGENTS.md''s `# Glossary`, extracted to GLOSSARY.md when past the section budget. Self-invoke on learning, write the block in the same task; unknown means stay pending - never invent etymology. Also /glossary, ''add this term'', ''what does X mean here''. Owns glossary content; agents-md owns AGENTS.md.'
when_to_use: The agent encounters or uses a project-specific, foreign, transliterated, or redefined term for the first time; the user asks to record or look up a term; or terminology appears mixed across docs and needs one canonical list. Also /glossary.
argument-hint: "[the term(s), or 'audit' to find mixed terminology]"
---

# Glossary - one name per thing, all spellings listed

A project rarely speaks one vocabulary. It mixes English with transliterated words (`Basr` for بصر), Arabic written in Latin letters in chat logs (Franco: `kifak`, `3ando`), plain words given a private meaning ("the eye" = the vision subsystem), and codenames whose meaning is the design. An agent that meets these cold either guesses or asks; a later session meets a *different* spelling of the same word and drifts again. This skill keeps one authoritative list, cheap enough to load every session.

**The invariant: one block per term, filed under its letter - term line (acronym spelled out), every
spelling, a 2-5 line meaning, a `Used in:` reference.** The block answers "what is this word and where is it
used here" - it is not a dictionary and not documentation of the feature.

## The golden rule - what earns a block

Ask one question about any word `X`: **does it mean here exactly what any English/native-language dictionary
says it means, or does the project say more, less, or different?**

- **Different meaning in this project → it belongs in the glossary.** This has nothing to do with the word
  being foreign: plain English words redefined by the project ("eye" = one camera+detector instance, "draft" =
  a specific DB state, "sync" = *the* Basr↔phone protocol) are the most dangerous entries, because every agent
  already believes it understands them. The same for abbreviations that spell out a project-private expansion
  (`TPE` that is not thermal-printer-extension but "the-pipeline-engine").
- **Correct English, but vague - and the project made it concrete → block it too.** The word is neither
  redefined nor foreign; the dictionary is simply not decisive enough. "Minimal" is perfect English, but two
  engineers imagine two different feature sets - the project's *actual commitment* (which surfaces ship in
  core, everything else comes from extensions) must be written or every "keep it minimal" argument talks past
  the next. Same for coined uses: "melody" is a dictionary word, yet when the project means *a user- or
  model-composed sequence of automatable steps*, that is a term, not a metaphor. The test stays the same:
  would a reader who only knows the dictionary act differently from one who knows the project? Then it earns
  a block.
- **Same meaning as the dictionary, used ordinarily → no block.** "User", "button", "timeout" in their normal
  senses add noise and dilute the list.
- **Foreign, transliterated, Franco, codename → almost always a block**, because "same as dictionary" doesn't
  even apply - the dictionary the agent carries is the wrong language.

The test is *project commitment*, not exoticism: a block exists whenever the word, as used here, carries a
decision the project made - a redefinition, a narrowing of something vague, a naming. When unsure, add the
block with a one-line "Used in:" - a cheap extra block beats a confident misunderstanding.

**English is not the canon.** "The dictionary" here means the dictionary of *the project's own language*: a
project that documents and codes in Arabic, German, or Japanese has that language as its reference frame,
and the golden rule is asked in it. Never silently anglophone-ize an entry - the English translation of a
term is not its definition; describe what the word names *in the project*, in the project's language, and
let translations appear only as listed forms or as a clarifying gloss.

## Write it immediately - the rule, with its test

**A term learned is a term written, in the same task, before the task is called done.** Not "I'll add it
later", not a note in the report, not a mental bookmark for the next session - the next session is exactly
the agent that will meet the word cold. The completion test: when finishing any task, if you used or
learned a term that fails the golden rule, the glossary block exists *now*; a task that ends with an
un-written new term is not finished. This covers all learning routes: reading code or docs, the user
saying it in chat, a log file, your own coinage while naming something. (The one exception: a term whose
meaning you had to ask about and the answer never came - that block is written as `pending - not assumed`,
still in this task.)

## When it runs

- **Self-invoke on learning:** the first time the agent meets (or coins) a term that fails the golden rule -
  its use here carries more than the plain dictionary sense, whether because it is foreign, transliterated,
  Franco, a redefined or made-concrete common word, a private-sense abbreviation, or a meaningful
  project/codename - it adds or updates the block in the same task, not as follow-up.
- **User asks:** "add this term to the glossary", "what does X mean here", "these docs use three names for one thing".
- **Audit mode:** the user asks to find mixed terminology, or the agent notices two spellings/names for one concept while working.

## Where it lives

| Situation | Placement |
|---|---|
| Default | `# Glossary` section near the top of `AGENTS.md` (inside its ~50-line section budget) |
| Terms outgrow the section, or the project already has a docs/ convention | full list moves to `GLOSSARY.md` (or the project's docs location); AGENTS.md keeps the section as obligations + pointer: canonical-form rule + `Read: GLOSSARY.md` |
| No AGENTS.md exists yet | do not create it - that is `agents-md`'s job; produce the ready `# Glossary` block and hand it over |

The extraction trigger is the same as agents-md's: a section past ~50 lines becomes a doc with a pointer. Glossary content moves; the obligations stay ("use canonical terms; every alias is listed; unknown means are pending").

## Entry format - alphabetical blocks

The list is organized, not appended: letter headings (`## A`, `## B`, …), one block per term. A block has four
parts - term line, optional `Also:` line, the meaning (2-5 lines), and a `Used in:` reference. The shape, filled:

```markdown
## M

**Minimal IDE**

The project's philosophy of shipping only an essential core (editor, file tree, syntax highlighting,
settings, terminal, extension host) while everything else arrives through community extensions - so
"minimal" here is a specific ship-list commitment, not a general feeling of "small". Two consequences that
are part of the term: fast startup, and customization that is infinite because the core stays out of the way.

Not to confuse: "minimal core" used loosely in chat may mean just the editor - the full set is what ships.
Used in: `docs/architecture.md` §1, the core-vs-extension boundary in `src/`

## W

**workflow (also: Melody in this project)**
Also: Melody, melodies

A user-created or auto-generated sequence of steps that automates a development task - a visual, composable
arrangement of extensions. Two ways it comes to be: composed by hand, or generated by the assistant model
from a prompt the user gives in chat. The project names this "Melody", so `Melody`, `workflow`, and `routine`
in the docs all mean this one concept.

Used in: `src/workflows/`, `docs/concepts.md`
```

Both are ordinary English - `minimal` and `workflow` are correctly spelled and grammatical. They are here
because the project loaded them with a specific meaning a fresh reader would not supply. The `Melody` block
is the reverse case too: the project *renamed* an ordinary concept with a proper noun, and the glossary maps
the coinage back to the plain word so neither spelling strands the other.

Rules:

- **Term line: `**Canonical (Spelled Out)**`** - an acronym or abbreviation always carries its full form in
  parentheses the first time; a plain or foreign word is just the bold canonical. Letters decide the block's
  home: by the canonical form's first letter.
- **Bilingual terms are written as one combined canonical** - the project's Latin form and its native script
  together on the term line: `**Basr, بصر**`. Both are the name; neither is an annotation. Other
  transliterations (basr, al-basr, Franco spellings) go on the `Also:` line. If the project's primary
  language is not English, the whole glossary speaks that language - headings, meanings, and the combined
  form in the project's own order (`**بصر, Basr**`) - English never becomes the default voice.
- **Leading articles do not file the word.** A name like "The Pit" is listed by its head noun, inverted
  comma-style: `**Pit, The**` under `## P`, read as "The Pit" everywhere it is cited. Same for any lead-in
  the project treats as inseparable (`A-Frame` stays under A; `el-Basr` files under the noun it attaches to).
  The lookup a future agent performs is for the distinguishing word, not the grammar in front of it.
- **`Also:` line whenever variants exist** - remaining transliterations, Franco spellings, plural and
  variant spellings, retired aliases (the native script of a bilingual term is on the term line, not here).
  An agent meeting `بصر` must land on the `Basr, بصر` block; alias terms get no block of their own, only
  the `Also:` line.
- **Meaning in 2-5 lines**: plain-language sense and what it names *in this project*, with the confusion guard
  as its own "Not to confuse:" line when a look-alike exists. Needs more than 5 lines → it is documentation:
  write it in the feature's doc and point there from `Used in:`.
- **`Used in:` names where the term actually lives** - the module, config key, or doc section. This is the
  lookup an agent most often wants: it met the word in code and wants the definition, or read the definition
  and wants the code.
- **Write the meaning generically, keep identity out of it.** A block explains what the term *is*, not whose
  contract it is: partner and customer names, internal endpoints, ticket ids, unreleased versions belong in
  the definition only when the term genuinely *is* that thing - and even then name the role ("a vetted
  partner", "the enterprise tier"), not the identity. A glossary is one of the most-shared artifacts in a
  repo; before a glossary leaves the project - to a public doc, another team, or an issue - run `revoke`
  over it. Inside the project the real names may stay where the code already shows them.
- **Never invent an etymology or a meaning.** Unknown term still gets its block immediately, meaning withheld:

  ```markdown
  ## F

  **farasa, فرسة**
  Also: faraasa

  pending - not assumed. UI string label; not defined anywhere in code or docs.
  Used in: `app/UI_strings.ar.xml`
  ```

  Ask the user when the conversation allows; the block then gets its meaning in the same task.
- **Two senses, split.** A term meaning two things here gets one block with an "As X: / As Y:" line pair if
  both are core, or a pointer block plus a real block under the other word's letter if one is dominant.
- **Language honesty**: keep the term's own script visible in the `Also:` line, because the agent must match
  it later in logs, UI strings and chat.
- New entries are inserted under their letter, in alphabetical order within it - never tacked onto the end.

## Audit mode - finding mixed terminology

Look for one concept under several names, then propose the merge map (show it before editing):

1. Grep variants of a term across docs, code, chat-facing strings - including script and transliteration spellings; also grep the *other* language: English docs may reference a word an Arabic UI string already defined.
2. For each collision: pick the canonical (dominant in code), move the rest onto its `Also:` line, and fix or flag the occurrences that used a non-canonical spelling in a place a future agent will read as new vocabulary.
3. Anything whose meaning the docs disagree on is surfaced to the user, not decided silently.

## Boundaries

| Not this | Go instead |
|---|---|
| Creating or restructuring AGENTS.md | `agents-md` (glossary fills/updates the `# Glossary` section only) |
| The reusable-units index | `units-md` - units are code parts; terms are vocabulary |
| Explaining how a system works | `document` (write) - the glossary block is a few lines |
| Translating content between languages | not this skill - matching forms is not translating |
| Taking a glossary outside the project (public docs, another team, an issue) | `revoke` - strip identities, keep the meanings |

## Reference

`examples/worked-entries.md` - a project that speaks three vocabularies, showing the golden rule doing its
job: a redefined English word (`eye`), the Franco collision that proves the point (`basir` vs `Basr` - same
letters, different words), an audit merge map, and the section outgrowing its budget into `GLOSSARY.md`.
Read it once before the first real entry if the "does it differ from the dictionary?" test feels unclear.
