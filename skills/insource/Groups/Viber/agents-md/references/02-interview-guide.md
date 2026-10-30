# Interview guide - ask only what the repository cannot answer

`AGENTS.md` records **decisions**. A decision is a question whose answer changes a rule in the file and cannot
be looked up. Everything else is reconnaissance, and reconnaissance is not the user's job.

## The three-question filter

Keep a question only if all three hold:

1. **The answer changes a rule.** "What's the project name?" changes nothing in the file.
2. **The repository does not already say it.** If `bun.lockb` exists, the package manager is Bun; asking
   wastes the user's attention and signals I did not look.
3. **The alternative is a guess I would have to enforce.** If I can leave it `pending` without breaking the
   agent's other duties, asking may still not be worth it - but inventing never is.

## Inferable from the repo - look these up, do not ask

| Fact | Evidence |
|---|---|
| Package manager | `bun.lockb` / `package-lock.json` / `pnpm-lock.yaml` / `yarn.lock`; `packageManager` field in `package.json` |
| Active branch and the branch actually being committed to | `git branch --show-current`, `git log --oneline -20 --all`, merge patterns in history |
| Version format and base | `.csproj` `ApplicationVersion`/`InformationalVersion`, `package.json` version, `Cargo.toml`, `gradle.properties`, changelog headers |
| Commit message convention | 20-40 real subjects; presence of type prefixes correlates with commitlint config |
| Tooling enforcement | `.commitlintrc*`, `.husky/`, `.pre-commit-config.yaml`, `.editorconfig`, lint configs, CI workflow files |
| Docs tree and version dirs | `find` for `docs/`, `.repertoire/`, `steering`, `v1/`, `v2/`, `design/`, `prototype/`, `scratch/` |
| Skill/command roots | `.cursor/skills`, `.claude/skills`, `.qoder/skills`, `skills/`, `.cursor/commands` |
| Env plumbing | `config.env`, `.env.example`, `*.schema.ts` env files, `1password`/`op` references in scripts or CI |
| Test and build commands | CI workflow steps (the safest source), `package.json` scripts, `Makefile`, build docs |
| Data store | connection config keys, migrations folder, ORM config |

If two sources conflict (lockfiles for two managers, CI on three), **that** is a question - with the conflict
named: "There is both `bun.lockb` and `package-lock.json`; history shows both used. Which is authoritative -
the other gets deleted or ignored?"

## Must ask - the decision bank

Ask only for the sections the repo left unresolved. Recommended grouping for one `inquire` page; each row shows
the rule it produces.

| # | Question | Feeds | If unanswered |
|---|---|---|---|
| 1 | Which version is active now, and which must be ignored? | 2 | the file cannot fence scope; highest-cost omission |
| 2 | Which channels exist; do any rules differ per channel? How does the agent detect the channel? | 2, 3 | leave channel out of the table and say so |
| 3 | Where does new work land, and what may never be committed directly? Who approves promotion? | 3 | record the observed branch pattern as *inferred, unconfirmed* |
| 4 | Version format and increment duty; who may change the base version? | 3 | pointer to the file holding it, no invented format |
| 5 | Is there a units index? Where? Reuse-or-extend duty? Who updates it when a subagent adds a unit? | 4 | `pending - no units reference yet` |
| 6 | Where do design/prototype references live, and which are in scope? | 5 | omit section 5 with one line saying the project has none |
| 7 | Which shell must be avoided and why; chaining allowed? Scratch script location and cleanup duty? | 6 | ask; this is environment-specific knowledge only the user has |
| 8 | One package manager, confirmed? | 6 | use the inferred one, marked *inferred from lockfile* |
| 9 | Environment strategy: type-safe schema? build-time generation from a central file? runtime secret store? paths and commands | 7 | `pending` + the prohibition that is always safe: do not edit `.env` directly |
| 10 | Debugging: inspect data permitted? modify permitted, in which environment? how to verify visual/GUI behavior? | 8 | permit read-only inspection locally, require a question for anything mutating |
| 11 | What must happen before the first edit in a session? | 9 | derive from sections 2, 4, 6 as a startup checklist |
| 12 | Subagent naming scheme; report location and filename pattern; is reusing a role name allowed to overwrite? | 10 | propose a default and mark it *proposed* |
| 13 | What may a subagent decide alone vs return undecided? | 10 | default: reversible local edits in scope = decide; anything crossing files/branches/destructive = return undecided |
| 14 | Fan-out: max depths and max total workers; what happens when a leaf fails | 10 | cap at 2 depths and report the cap as a default |
| 15 | Any mandatory-skill rule for this project? | 1, 10 | omit; do not invent an obligation to use skills the project may not have |

## How to hand it to `inquire`

Build one page rather than fifteen pings: group by section, lead with the context the user needs to answer well
("your repo has both lockfiles; here is what each implies"), order options by my recommendation first with the
trade-off visible, and use branching where an answer opens a follow-up (e.g. env strategy → which provider).
Every question must be answerable by someone who has not read this skill's references.

Then, after the answers: **state the decisions back in one short list before drafting.** Silent incorporation
loses the chance to catch a misread answer, and the file is going to enforce it every session.

## Recording answers without smuggling assumptions

| Answer quality | How to write it |
|---|---|
| Decided | the rule, imperative, with the reason in a clause |
| Inferred from repo | the rule + `(inferred from <evidence>; correct me if wrong)` |
| Partially decided | write the decided half; list the rest as pending |
| "Do whatever you think" | pick, then mark **proposed**, and include it in the closing report so the user can veto |
| No answer | `pending - not assumed`, numbered |

The distinction between *decided*, *inferred*, and *proposed* is worth keeping in the file: it tells the next
agent how hard to push back, and it makes the next audit pass short - the pending list is the work queue.
