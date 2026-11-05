---
name: personalize
description: 'Updates the user''s GLOBAL agent instruction file (the personal AGENTS.md every project loads) so settled questions never get re-asked - an agent asking "which package manager?" when the global file answers is the idiot-agent this skill kills. Modes: "/personalize that i like bun and bunx" distills a statement into an enforceable preference line (behavior not transcript, explicit exception boundary); bare /personalize asks what to set, showing existing lines; "/personalize the section X in current AGENTS.md into global" promotes it - personal defaults up, project decisions stay, machine-specific routed out; copy unless told "move". Ladder: current prompt > project AGENTS.md (respects the global; overrides only explicitly) > global preference. Dedupe and refine over append; vague statements sharpened or refused, never written. Triggers: personalize, remember I always prefer, never ask me about X again, set my global default.'
argument-hint: "[preference statement | promotion: the section X in current AGENTS.md into global | empty to be asked]"
---

# Personalize - settle it once, everywhere

The global AGENTS.md is the user's standing instruction file: every project's agent loads it before
the project's own rulebook. Its content is one kind of thing only - **preferences that hold across
projects**. Project files respect it: a project may narrow or override a preference only by writing
the override into its own AGENTS.md with its reason - never by silent contradiction. The measure is simple: **the questions it kills.** A user who has said
"bun and bunx, never npm" once, and gets asked "which package manager?" in the next project, has a
global file that is not doing its job.

## The three laws

1. **Settled questions never re-ask.** If a preference answers a question, asking it again is the
   defect this skill exists to remove. Preference lines are written so an agent can ACT on them
   without deliberation - "prefer modern tooling" answers nothing; "bun/bunx only, never npm/npx"
   kills the question.
2. **The precedence ladder:** `current prompt > project AGENTS.md > this global file`. The user's
   current word wins for that task, silently. A project RESPECTS the global by default and may
   override a preference only **explicitly** - its own AGENTS.md states the override and its
   reason; a project rule quietly contradicting the global with nothing written is silent drift,
   and promotion (Step 2) audits for exactly that. Everywhere unmentioned, the global line governs
   - until edited here.
3. **Behavior, not transcript.** Never store what the user said ("user mentioned they like bun");
   store the rule an agent follows. The global file is policy, like every rulebook - one owner per
   fact, refine over duplicate.

## What belongs here and what does not

| The statement | Where it goes |
|---|---|
| "I always use bun", "no PowerShell", "answer me concisely", "commits in imperative" | global AGENTS.md (this skill) |
| "In this project work lands on `beta`", "docs live in `documentation/`" | the PROJECT's AGENTS.md - that is `agents-md`'s interview, not a personal preference |
| machine-only facts ("my Python is at D:\", "this laptop has no GPU") | `AGENTS.local.md` beside the project, or the user's environment notes - never global (it would lie on another machine) |
| a one-off ("use npm this time") | nowhere - it is not a preference, and silence is correct |

When scope is genuinely unclear and it changes where the line lands, ask the ONE question that
settles it ("every project, or this one?"). Never guess the destination of a rule.

## Step 1 - Find and read the global file

- It is the harness's user-level instruction file (for this CLI: `~/.qoder/agents.md`; another
  harness: its documented equivalent). Do not ask the user for a path the harness already resolves;
  if none can be located, ask once where their global agent instructions live.
- **Read it fully before writing anything** - the current lines decide whether this is an add,
  a refine, or a replacement. Never write against remembered content; re-read.
- No file yet: create it with the minimal shape - H1 title (`# Global Agent Instructions`), one
  lead line ("Standing preferences for AI agents in every project; your current prompt wins over
  any line here."), and a `## Working preferences` section.

## Step 2 - Get the statement

- **With arguments** (`/personalize that i like bun and bunx`): the statement is given - go
  distill. Do not re-ask what was already said.
- **Bare** (`/personalize`): ask ONE question - "what do you want to personalize?" - optionally
  with the existing lines listed under it so the user can amend instead of add. No interview wall,
  no guessing at what they "probably" want.
- **Vague statement** ("I like clean code", "be faster"): it cannot kill any question yet - ask
  what it changes in practice ("which behavior - naming? formatting? answer length?"). Sharpen it
  or refuse to write it; a vague line is a transcript in rule clothing.
- **Promotion** (`/personalize the section X in current AGENTS.md into global`): a project section
  can be one person's settled preference wearing project clothes. Read the named section and sort
  EVERY line: personal default → distilled into a global line; project decision → stays (said so
  in the report, line by line); machine-specific → routes to `AGENTS.local.md`. **Copy is the
  default** - the project file is touched only when the user said "move", and then the promoted
  lines are deleted there in the same change so one owner per fact remains. A candidate line that
  contradicts an existing global line STOPS and asks which one the user actually lives by -
  promotion never silently wins a fight between two files.

## Step 3 - Distill into a preference line

Every line carries, in order:

```text
[where it applies] : [the required behavior] ; [what is forbidden or avoided] - [exception boundary]
```

- `bun/bunx for JS work; never npm/npx - unless the repo's config forces it or the user orders
  otherwise in the current session.`
- The **exception boundary is mandatory**: the repo-evidence escape and the current-prompt escape.
  A rule without a boundary is a cage the first legitimate exception will break.
- One behavior per line. Two behaviors make two lines.
- Group under a matching section (`## Working preferences`, `## Tooling`, ...); create a new
  section only when none fits, and keep the file's existing wording and structure intact.

## Step 4 - Dedupe, refine, conflict

- **Same meaning already covered** → say so and change nothing. The user stating a preference
  twice is emphasis, not a second rule.
- **Related line exists, stated more weakly or too broadly** → REFINE it in place (merge the new
  precision into it). Never append a near-copy: two copies agree today and disagree after the
  first edit.
- **Contradicts an existing line** → the user's current word wins: replace the old line and
  state in the report what it retired ("replaced: 'npm preferred'"). Silent swaps are how an
  old preference keeps getting enforced by an agent reading a line nobody remembers.

## Step 5 - Write minimally, report

- Edit the affected lines only - never rewrite the whole file, never re-flow sections the change
  does not touch.
- Report in one block: the exact line added/refined/replaced (quoted), its section, and one
  precedence reminder ("your current prompt still overrides it").

## Anti-patterns

| Failure | Why it is the opposite of the purpose |
|---|---|
| Storing the quote ("user said they like bun") | a transcript kills no questions; agents cannot act on reported speech |
| Writing vague lines ("prefer modern tools") | answers nothing; the question survives being answered |
| Appending a second line beside the first | two owners of one fact - the drift maintenance cannot see |
| Smuggling a project decision into global | every other project inherits a rule chosen for one |
| Silent promotion win (project line promoted while its global contradiction goes unmentioned) | two files now disagree and no agent knows which one the user lives by |
| Deleting from the project after a COPY (or copying then leaving both owners) | "move" is a stated order, not an assumption; one owner per fact either way |
| "Always/never" with no exception boundary | breaks on the first legitimate exception, then gets ignored wholesale |
| Rewriting the file to "tidy" it | destroys wording the user chose; only the affected line is yours |

## Boundaries

- **Writable targets:** the global instruction file (its creation included) - and, ONLY on a
  stated "move", the deletion of the promoted lines from the project's AGENTS.md. Everything else
  routes out with a pointer to the right owner (`agents-md` for project rulebooks,
  `AGENTS.local.md` for machine facts).
- **No invented preferences:** only what the user stated or answered this session. Never "helpfully"
  add preferences guessed from observed behavior - a guessed default is an idiot-agent with
  paperwork.
- **Deleting/retiring a line happens only on a stated contradiction** (Step 4); the file is the
  user's, this skill is its editor, not its landlord.

## Resources

- `references/01-line-shape.md` - worked good/bad preference lines across domains, and the
  exception-boundary patterns.
- `examples/session-walkthrough.md` - both entry modes, one worked session each.
