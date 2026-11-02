# Execution rules, environment strategy, debugging

These three sections are where a rulebook earns its keep: they encode the failures that cost hours. Write them
as prohibitions plus the reason plus the permitted route. Never as a command catalogue.

## 6 - Command execution

The recurring hazard is that an agent trained on POSIX habits hits a Windows box, or hits a shell that hangs,
and then repeats the failure with more confidence.

Encode, per project, only what is actually true there:

| Rule type | Example wording | Why it belongs |
|---|---|---|
| Shell preference | "Prefer `cmd` over PowerShell here: PowerShell hangs on long-running commands in this environment." | kills the hang class |
| Chaining | "One command at a time. Avoid `&&`, `||`, and pipes unless unavoidable." | chained failures are unreadable; also `&&` behaves differently across shells, and a swallowed failure looks like success |
| Escaping | "Quote paths with spaces; backslashes eat arguments - use forward slashes where the tool accepts them." | the Windows path class |
| Long jobs | "Run long jobs in the background and poll, rather than blocking on a 2-minute timeout." | avoids the false "it hung" |
| Scratch scripts | "Complex or multi-step logic goes in a script under `scratch/`, run it, delete it when finished." | reproducibility without leaving debris |
| Interactive commands | "Never run a command that waits for input; find the non-interactive flag or hand it to the user." | the deadlock class |
| Verification commands | "The build is `<cmd>`; the test suite is `<cmd>`. Do not run `<heavy command>` unless the user asks." | stops the agent burning minutes the user did not want spent |

Two honesty rules: state the failure being avoided (that is what makes the rule followed instead of negotiated),
and if a restriction is machine-specific rather than project-wide, put it in a local instruction file instead
of the shared one ([`07`](07-harness-and-portability.md)).

**Package manager.** Record exactly one, plus the prohibitions that follow. Infer it from evidence first:

Installs themselves are governed by section 12 (Resourceful): project-local first - the project's own environment, the project's own install, never a global one for a project need.

```bash
ls bun.lockb package-lock.json pnpm-lock.yaml yarn.lock 2>/dev/null
node -e "console.log(require('./package.json').packageManager || 'unset')"
grep -rhoE "(npm|pnpm|yarn|bun)( run| i|x)?" .github/workflows 2>/dev/null | sort | uniq -c | sort -rn | head
```

The wording that works: *"Use `bun` and `bunx`. Do not run `npm install` or `yarn` - they rewrite the lockfile
and produce dependency-resolution changes unrelated to the task."* The reason prevents the agent from treating
it as taste when it is stuck.

For non-JS stacks the same section carries the equivalent: the package/tool manager, the pinned toolchain
version and how to select it, and the restore/build command.

## 7 - Environment and secrets

Ask which strategy the project uses; combinations are normal. Record the route, the paths, and the prohibition.
Never copy the config system's documentation in here.

| Strategy | How it works | What the rulebook must state |
|---|---|---|
| **Type-safe validation** | a schema layer declares and validates the keys the app needs, so missing or invalid values fail fast and in the right place | where the schema lives, where per-app configs live, and that adding a variable means editing the schema rather than poking `process.env` at random |
| **Build-time generation** | a central source (e.g. `config.env`) is read by a generator script that emits each application's env config | the source file, the generator path, the regenerate command, and the rule that generated files are never hand-edited |
| **Runtime secret retrieval** | secrets come from a dedicated provider (e.g. 1Password CLI, a vault, a cloud secret manager) when the process runs | the approved retrieval mechanism, what must never be persisted or logged, and the fallback when the provider is unavailable (stop and report - not "hardcode it temporarily") |

The always-safe prohibitions, which hold in every combination and belong even when the rest is pending:

- **Do not edit `.env` files directly.** Name the permitted route instead; a prohibition without a route just
  stalls the agent.
- **Do not commit secrets, connection strings, or real values.** Scratch debug files read `process.env`; they
  never contain literals.
- **Never print or paste secret values into output, logs, or reports.** Redact, and say what was redacted.
- **If a secret has already been committed, removing it from the file does not un-leak it** - rotation is the
  fix, and that is a user decision.

## 8 - Debugging

Write the *ladder* the project supports, and the permissions, in that order. The generic advice ("read the
error carefully") belongs to nobody and displaces what does.

```md
- Reproduce: <the exact failing state and how to reach it locally>
- Escalate in this order:
  1. <data layer check, e.g. write a debug SQL file in scratch/ and query directly - confirms the data exists>
  2. <service layer check, e.g. call the existing service from a scratch script - isolates backend vs UI>
  3. <presentation/routing>
- Permitted during debugging:
  - inspect local data: yes
  - modify local data: yes, with a written note of what changed
  - inspect or modify staging/production: NO - ask the user
- Visual verification: <how to actually see the app: run+screenshots, device logs, harness tool>
- Cleanup: delete scratch files when finished
- Persistence: if the code looks correct, do not stop at one failed attempt
```

Calibrate to what exists. A CLI tool has no visual verification row; a service with no database has no SQL
step; a project that forbids touching local data gets that prohibition in bold rather than an optimistic
"inspect if needed". Writing a debugging capability the project does not have is worse than omitting it -
the agent will try to fabricate the tool.

**Scaffolding note.** The project may need helper scripts for these steps (a DB inspector, a screenshot
runner). agents-md records the duty and the path; it does not create the helpers. That is another skill's job,
and creating a stub would imply a capability that does not exist yet.
