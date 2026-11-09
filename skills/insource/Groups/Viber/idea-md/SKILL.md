---
name: idea-md
description: 'Turns a raw project prompt - any language, any mess - into IDEA.md: the project''s complete idea document, readable by anyone, technical or not. First the idea''s inspiration - a SET of sources: name every product it draws from (Medium, Dev.to…), what each contributes, its relationship (instance of / similar to / a slice of - mixed is normal), what is its own invention, and what it refuses per source. If the prompt never names one, the agent ASKS (''Is this project similar to X?'') instead of guessing. Then plain prose: what it is, its audience and audience types, everything it includes and explicitly does not - written as free-form paragraphs, not fixed bullet sections. Unclear points become idea-level questions only (name, scope boundaries, access rules, editorial stance) - never platform, stack or hosting, which belong to later stages. No system analysis. Triggers: ''write the idea file'', ''turn this into IDEA.md'', a spoken project vision. Feeds the lifecycle''s first phase.'
when_to_use: The user describes a project idea - however rough, in any language - and wants it written as IDEA.md or a project overview, or asks to sharpen/update an existing IDEA.md. Also /idea-md.
argument-hint: "[the project prompt, or the path to update]"
---

# idea-md — the project's standing idea document

IDEA.md is the first standing document of a project, before any spec, architecture, or plan. Its reader is
**any person in the world, technical or not** - a friend, an investor, a new teammate, a future agent - and
after one read they can restate what this project is. That readability bar is the whole skill.

## What IDEA.md is, and is not

| Is | Is not |
|---|---|
| A plain-language overview of the project idea | System analysis of any depth |
| The complete picture of what the project includes, in broad strokes | **Module tables, capability matrices, "in-scope requirements: Module \| In-scope capabilities"** |
| Explicit about what the project does **not** include | Architecture, data models, tech stack |
| The idea's inspiration, stated | Task lists, sprint plans, definitions of done |
| Open questions where the prompt was silent | Filled-in guesses that read as decisions |

The forbidden depth is concrete: if a paragraph starts listing *Accounts: Registration, authentication,
profiles… · Editor: Rich text, headings, links… · Social: Follow, clap…*, that is a requirements matrix, not
an idea - it belongs to `detailsup` (system specification) and `planner` (work breakdown). IDEA.md says
"people can write and publish blog posts and follow writers" and stops there.

## First question: inspiration - no idea comes from thin air

Every project is a descendant of something - and **inspiration is a set, not a single verdict**. A real idea usually has several sources: the publishing model from one product, the community culture from another, the monetization from a third (or from none). Each source contributes something specific, and the *composite* - which pieces from whom, and what refused from each - is the idea's actual identity. Do not force one label onto the whole project.

**If the user's message does not name what the project is similar to, ask - never assume.** One direct question:
*"Is this project similar to <a named product>?"* - or, when no single product fits, *"Is this project similar to
<the kind of thing it resembles>?"* (for example: "Is this project similar to Jira?" or "Is this project
similar to a big-data scraper?"). Wait for the answer; do not proceed on a guess. Only when the prompt names
its inspiration (or answers the question) may the section be written.

For **each** source, one line of the same shape - the three relationship forms below are labels for *one
source*, and mixing them across sources is normal:

| One source's form | Meaning | Telltale in the prompt | What it implies |
|---|---|---|---|
| **instance of** | That product's model applied to a new domain/segment - same mechanics, different world | "«model» for <segment>", "the <product> of <place>" | Its core model carries over almost intact; the new domain's rules are the real work; its extras still need an explicit drop list |
| **similar to** (inspiration) | Borrows that product's concept or feel; the project owns its identity | "similar to X", "inspired by X", "like X but…" | Only the named similarities are owed; everything else is a design choice, not an inheritance |
| **a slice of** | Extracts a subset of that product's capabilities as a standalone product | "X but just the <part>", "just the blog side of X" | The slice's boundary is the product; that product's other features are non-goals from day one |

The composite is written as a short paragraph, not a single tag: *"Inspiration: Medium's publishing core
(instance of), Dev.to's writer culture (similar to), with none of either's monetization or algorithmic
discovery (refused)."* Each clause maps to a source, not to the project as a whole.

Rules that keep the inspiration honest:

- **Name every source explicitly** - product names, not categories ("Medium", "Dev.to", not "blogging
  platforms"). A feature with no identifiable source is the project's own invention - say that too.
- **Per-source, per-contribution.** The relationship can differ between sources *and* between features
  from the same source: a project may take one product's model wholesale and only a single feature from
  another. Record the contribution, not a global classification.
- **Refusals are named per source** - "what we refuse from Medium" and "what we refuse from Dev.to" are
  different lists, and both make the exclude section concrete.
- **"Exactly like X" is rare.** When the user says it, write what will still differ (platform, audience,
  free-vs-paid, geography) - an "exact clone with no differences" is almost always an unexamined claim.
- **Unclear means ask.** Anything about the idea itself that the user's message leaves open - naming,
  scope boundaries, audience, access rules, what "basics" means - gets a question, not a plausible default.

## Procedure

1. **Read the prompt as it was spoken** - any language, any order. Keep the user's own words for the name
   and the idea; do not translate away nuance. (Project names keep their original script next to a Latin
   form on first mention: "وسيط (Wasit)".)
2. **Map the inspiration** (above) - one line per source with its contribution and its relationship; if the
   prompt never named one, ask first. Then state what the composite implies for the include/exclude lists.
3. **Extract the four content pillars**, in plain language:
   - **What it is** - one line, then a short paragraph a non-technical reader understands;
   - **Audience** - who the audience is and what types of audience (readers, writers, both; the segments
     inside them), in their own words - not a persona framework;
   - **What it includes, in total** - every capability the project will have, written as free-form prose
     (normal paragraphs, no bullet scaffolding), grouped the way a reader thinks about the product (write,
     read, follow, be free…), broad strokes only;
   - **What it does not include** - also free-form prose: the exclusions the user stated **and the sources'
     tempting features this project refuses**; the second list is the one users forget and later re-litigate.
4. **Collect the open questions** the prompt genuinely left unanswered - **about the idea itself only**:
   the name/positioning, the boundaries of "basics" vs "deep features", the audience's breadth, who may read
   or write, the editorial stance. Platform, stack, hosting, performance, typography and every other
   how-it-is-built question are **not idea questions** - they belong to `detailsup`/`techstack` and do not
   belong in this document. Number the questions, never fill them with plausible guesses.
5. **Write IDEA.md** in the language the user asked for; when none was named, write English and keep names
   in their original script. Place it at the project root (or where the user says).
6. **Report in chat**: the inspiration line, the file path, and the numbered open questions - nothing else.

## The readability bar

Write for a smart reader who has never seen the prompt. Check the draft yourself:

- a non-technical person reads it once and can restate the idea to someone else;
- no borrowed jargon without a one-clause explanation ("a publication - a shared space where several
  writers post under one name");
- no sentence that only makes sense after reading the source conversation;
- nothing about *how* it will be built - only *what* it is.

## Maintaining it

IDEA.md lives with the project: when a decision changes the idea (a feature moves in or out, the audience
sharpens, the product is renamed), the file is updated in the same change - edits, not appended drift.
The inspiration line is re-checked at that moment too: a project that started "similar to Y" can drift into
"an instance of Y" (or away from it), and the wording should follow.

## Boundaries

| Not this | Go instead |
|---|---|
| System analysis, requirements matrices, module/capability tables | `detailsup` |
| Tech stack or architecture choices | `techstack`, `thebest`, `dtb` |
| Task lists, sequencing, delivery plans | `planner` |
| Persona development, user research | `persona`, `deep-research` |
| AGENTS.md, UNITS.md, glossary | `agents-md`, `units-md`, `glossary-md` - sibling standing documents |
| Polished long-form prose about the idea | `document` |

## Files

| Need | Load |
|---|---|
| The IDEA.md skeleton with section guidance | `assets/templates/IDEA-template.md` |
| The set-of-sources model worked through, plus a complete IDEA.md from a messy spoken prompt | `examples/inspiration-and-worked-file.md` |
