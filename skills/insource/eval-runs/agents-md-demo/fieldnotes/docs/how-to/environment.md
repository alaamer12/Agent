# How to handle environment and secrets

- **No committed `.env`, and never edit a connection string or the PocketBase URL in source** - those
  are runtime-changeable and belong in SQLite settings tables (section 14 golden rule).
- **Strategy in use:** runtime settings read from the local SQLite `settings` table; the PocketBase
  base URL and sync credentials are user-entered / per-device provisioned, never committed.
- Machine-specific paths go to `AGENTS.local.md`, not into this file.
- **In debug scripts:** read from the settings table or process environment; never hardcode a secret.
