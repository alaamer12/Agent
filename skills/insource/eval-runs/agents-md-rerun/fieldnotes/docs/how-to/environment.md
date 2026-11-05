# How to handle environment and secrets

- Every config value is declared in the typed `AppSettings` schema (`services/api/settings.py`) -
  the rule itself is section 14; this section owns the files: `.env` is a runtime materialization
  of that schema, nothing more.
- Never edit `.env` files ad hoc: change the schema, mirror the key in `.env.example`, let startup
  validation propagate. There is no other route.
- Runtime secret store: none decided yet - `pending - not assumed`; do not wire one in speculatively.
- Machine-specific paths go in `AGENTS.local.md`, not this file.
