# How to run things

- One package manager per half of the repo: `uv` for Python (`services/api`), `bun` for JS
  (`apps/web`). Never run `pip`, `npm`, or `yarn` here - they rewrite or drift `uv.lock` /
  `bun.lock` and the next install resolves a different tree than CI built.
- One command at a time while investigating; chain with `&&` only when a step truly depends on the
  previous one's success.
- Complex sequences: write a throwaway script under `scratch/`, run it, delete the folder when
  done.
- Verification commands are section 17's gate; this section owns only how things are run.
