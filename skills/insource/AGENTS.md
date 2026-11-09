# Global Agent Instructions

Standing preferences for AI agents in every project; your current prompt wins over any line here.

## Working preferences

- **Do not run typecheck by default** (`tsc --noEmit`, `bun run typecheck`, turbo typecheck/build). The user runs these at the end of a session. Run them only when the user explicitly asks in the current session.
- **Other agents may be editing the same working tree concurrently.** If a file changes underneath you, or an edit you expected to make is already present: do not panic, do not "restore" anything, and do not fight the other agent. Re-read the file for current state, adapt (keep your own changes additive), or wait briefly until that agent finishes with the file. Never revert or overwrite edits you did not make.
- **Chat language mirroring with English code/docs**: Mirror the user's conversational language (English, Modern Standard Arabic, Egyptian Arabic) in interactive chat responses; author all code, comments, commit messages, and project documentation strictly in English - unless ordered otherwise in the session.
- **Chat brevity vs. file detail**: Deliver concise, direct, filler-free answers in chat; make written files (documentation, READMEs, architecture notes) comprehensive, detailed, and context-rich for future readers - unless the user asks for an in-depth chat explanation.
- **Autonomy & escalation boundary**: Make reversible technical decisions autonomously and proceed; stop to ask only on costly, irreversible, or cross-cutting structural forks - unless invoked under full-autonomy skills (e.g. `iwts`) where the agent proceeds without interruption to the end.
- **Calibrated verification**: Execute real verification commands (tests, builds, runs) for non-trivial logic, refactoring, and multi-file changes; skip verification burns on simple, trivial file edits - unless the user requests explicit validation.
- **Root-cause fixing**: Diagnose and resolve underlying defects rather than applying superficial bandaids; record architectural rationale in docs - unless instructed to perform an isolated quick patch.
- **Safe cleanup**: Remove dead code and unused imports within touched files; ask for user confirmation before deleting standalone files or directories - unless the file was created in the current ephemeral session.
- **Minimal diffs & style preservation**: Restrict edits to the exact lines being changed and preserve incumbent formatting/whitespace; avoid full-file auto-reformatting - unless the repository enforces a pre-commit formatter or the user requests it.
- **Secrets & environment security**: Never write, log, expose, or commit secret keys or live `.env` files; document required variables in `.env.example` - unless mock placeholders are explicitly requested.

## Tooling & Dependencies

- **Package manager**: `bun`/`bunx` for JS/TS tasks; never use `npm`/`npx`/`yarn`/`pnpm` - unless existing repository lockfile/config strictly dictates another manager or the user explicitly specifies it.
- **Dependency discipline**: Prefer standard libraries and already-installed packages before adding new dependencies; avoid adding external libraries for small utilities that can be written natively - unless approved or required by project specifications.
- **Cross-platform shell execution**: Prefer platform-agnostic commands and tools (Node, Python, Bun) over OS-specific shell scripts and syntax; avoid assumptions about Unix-only utilities when running on Windows - unless explicitly running inside a targeted WSL/Linux environment.

## Git Discipline

- **Commit style**: Use Conventional Commits in imperative mood in English (e.g., `feat: add user service`, `fix: handle race condition`); never write vague, unstructured commit summaries - unless the repository already enforces a different documented standard.
