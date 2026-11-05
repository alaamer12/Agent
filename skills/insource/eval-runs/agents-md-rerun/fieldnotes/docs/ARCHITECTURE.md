# Tidepool Architecture

- `apps/web` (SvelteKit) calls `services/api` (FastAPI); persistence is SQLite via SQLAlchemy 2.0
  (`Mapped[]` style - see AGENTS.md section 21).
- Money is integer cents behind the `Money` value type; float columns do not exist on any model.
- Config is one typed schema: `AppSettings` in `services/api/settings.py`; startup fails on a
  missing or unknown key, and an import-linter gate blocks direct `os.environ` reads in CI.
- Pipelines: every push to `main` publishes to PyPI + the web host; nightly `beta` builds deploy
  to `beta.tidepool.dev`.

Local binary tooling (not tracked, `tools/` is private): `tools/sqlitebook.exe`, a portable SQLite
browser for DB inspection per AGENTS.md section 8. Install need: download the vendor's portable
`.exe` into `tools/` on each machine; never commit the file itself.
