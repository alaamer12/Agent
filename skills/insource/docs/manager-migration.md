# manager.py — Behavior Inventory and Migration

This document is the mined inventory of everything the two legacy tools did,
where each behavior lives in `manager.py`, and what changed. It exists so a
future maintainer can verify the consolidation without reading 792 lines of
retired scripts.

Source files: `symlink.py` (677 lines) and `agents_symlink.py` (115 lines).
Both were replaced by `manager.py` and removed; git history keeps them.

## 1. Command surface

| Command | Purpose |
|---|---|
| `skill` (default) | link or hard-copy skills into agent folders or a project |
| `agent` | link or hard-copy `AGENTS.md` into agent instruction files |
| `lint` | validate `SKILL.md` descriptions and sync state |

`python manager.py avatar` and `python manager.py skill avatar` are equivalent:
the parser inserts the default command when the first positional token is not a
command name.

## 2. Skill behaviors from `symlink.py`

| ID | Legacy behavior | New invocation | Implementation | Status |
|---|---|---|---|---|
| S1 | Link named skills into every agent | `manager.py skill avatar` | `cmd_skill` → `deploy_skill` | preserved |
| S2 | Link several names at once | `manager.py skill avatar mine` | `cmd_skill` loop | preserved |
| S3 | `--agents a,b` or `all`, aliases like `claude-code` | `-A/--agents` | `parse_agents` | preserved |
| S4 | `--lock` records installs per agent in `skills-lock.json` | `-l/--lock` | `record_locks` | preserved (see 5.2) |
| S5 | `--refresh` repairs links, restores locked skills, backs up | `-R/--refresh` | `cmd_refresh` | preserved |
| S6 | `--refresh --agents` limits the scope | `-R -A qoder,gemini` | `cmd_refresh` roots | preserved |
| S7 | Backup zip in home before refresh | default on, `-B/--no-backup` to skip | `backup_dirs` | preserved |
| S8 | `--all` links every registry skill | `-a/--all` | `cmd_skill` | preserved |
| S9 | `--force` replaces real directories/files | `-f/--force` | `deploy_skill`, `cmd_refresh` | preserved |
| S10 | `--dry-run` reports without writing | `-d/--dry-run` | all write paths | preserved |
| S11 | `--registry` selects another registry root | `-r/--registry` | `main` | preserved |
| S12 | `--list` prints registry skills | `-L/--list` | `cmd_skill` | preserved (table output) |
| S13 | Nested duplicate entries removed on refresh | `-R` | `clear_entries(places)` | preserved |
| S14 | `qoder`/`gemini` real dirs replaced without `--force` | `-R` | `MIGRATION_AGENTS` | preserved |
| S15 | Resolution: path → cwd → unique match under cwd → registry | any skill name | `resolve_skill` | preserved |
| S16 | Ambiguous local names abort with a listing | any skill name | `resolve_skill` | preserved |
| S17 | Directory symlink with junction fallback on Windows | all link paths | `make_link`, `_make_junction` | preserved |
| S18 | Lockfile keeps unrelated keys (`skills`, `version`) | `-l` | `load_lockfile`/`save_lockfile` | preserved |
| S19 | Backup deduplicates real paths across overlapping roots | `-R` | `backup_dirs` | preserved |
| S20 | Broken locked skills are restored on refresh | `-R` | `cmd_refresh` locked pass | preserved |

## 3. Agent behaviors from `agents_symlink.py`

| ID | Legacy behavior | New invocation | Implementation | Status |
|---|---|---|---|---|
| A1 | Deploy `AGENTS.md` to all agent config files | `manager.py agent` | `cmd_agent` | preserved |
| A2 | `--agents qoder,gemini,claude` selection | `-A/--agents` | `parse_agents` | preserved |
| A3 | `--mode copy` copies instead of linking | `-c/--hard-copy` or `-M copy` | `deploy_agent_file` | preserved |
| A4 | Existing real file backed up once to `.bak` | default on; `-f/--force` skips backup | `deploy_agent_file` | preserved |
| A5 | Symlink failure falls back to a copy | automatic | `deploy_agent_file` | preserved |
| A6 | Missing source `AGENTS.md` is a hard error | automatic | `cmd_agent` | preserved |
| A7 | Unknown agent names were skipped | now a hard error | `parse_agents` | changed (see 5.1) |

## 4. Flag migration

| Legacy flag | New form | Notes |
|---|---|---|
| positional skill names | unchanged, or `skill <names>` | default command is `skill` |
| `--agents` | `-A/--agents` | same syntax and aliases |
| `--refresh` | `-R/--refresh` | also syncs hard copies |
| `--all` | `-a/--all` | same |
| `--lock` | `-l/--lock` | same file and schema |
| `--force` | `-f/--force` | same |
| `--dry-run` | `-d/--dry-run` | same |
| `--no-backup` | `-B/--no-backup` | same |
| `--registry` | `-r/--registry` | same |
| `--list` | `-L/--list` | now a table |
| `--mode symlink|copy` | `-M/--mode` | kept as an alias; `-c/--hard-copy` is preferred |
| — | `-i/--into PATH` | new: install into a project folder |
| — | `-c/--hard-copy` | new: copy plus sync tracking |
| — | `-j/--jobs N` | new: concurrent hashing/linting |
| — | `-q/--quiet` | new |
| — | `-v/--verbose` | new |
| — | `-C/--no-color` | new: ASCII backend |
| — | `-m/--max-description N` | new: lint limit (default 1024) |
| — | `-S/--strict` | new: lint exits 1 on findings |

Every flag above has both a short and a long form.

## 5. Intentional behavior changes

### 5.1 Unknown agent names are now always an error

`symlink.py` errored, `agents_symlink.py` skipped with a notice. A silent skip
hides a typo; the unified tool errors for both commands and lists the valid
names.

### 5.2 Lock entries are recorded only for real installs

The old linker treated `skipped` as success and locked it. A skipped install
would then be "restored" on refresh into a path the user had explicitly
protected. `cmd_skill` records only statuses other than `skipped`/`failed`.

### 5.3 Refresh verifies links by resolution, not file-set equality

A symlink's contents *are* the source by definition, so comparing file sets
added cost without information. Refresh now checks that the link exists and
resolves to the source. Hard copies get the stronger fingerprint comparison
(section 7).

### 5.4 `agent --force` now means "do not keep a `.bak`"

Previously the `.bak` was unconditional. The default still backs up; `--force`
is the explicit opt-out so repeated deploys do not accumulate backups.

## 6. New capabilities

### 6.1 `--into` project installs

`-i/--into PATH` replaces the agent roots with one folder. The path is created
if missing and must be a directory if it exists. A skill lands at
`PATH/<skill-name>`. `--agents` is rejected with `--into` because the
destination is already singular.

### 6.2 Hard copies with synchronization

`-c/--hard-copy` copies the skill tree instead of linking. Every copy is
recorded in `manager-copies.json` at the registry root:

```json
{
  "version": 1,
  "copies": {
    "<normcase absolute target>": {
      "skill": "beta",
      "source": "<absolute source>",
      "target": "<absolute target>",
      "kind": "dir",
      "fingerprint": "<sha256 of the source tree>",
      "target_fingerprint": "<sha256 of the copy>",
      "files": 12,
      "copied_at": "2026-11-13T10:00:00"
    }
  }
}
```

`kind` is `dir` for skills and `file` for agent instruction files. The
fingerprint joins sorted `relative/path:sha256` entries, skipping `.git`,
`__pycache__`, `node_modules`, virtualenvs and link directories.

Re-running `-c` on an unchanged copy reports `unchanged`. If the source moved
on, the copy is updated. If the copy was edited locally, the update is refused
unless `-f/--force` is passed. `-R/--refresh` runs the same logic for every
managed copy under the selected roots.

### 6.3 Automatic sync audit

Every command except `--list` calls `audit_all()` before doing its work and
prints a warning banner if anything is missing or stale:

- hard-copy states: `missing-source`, `missing-target`, `target-replaced`,
  `source-changed`, `target-modified`, `both-changed`, `source-unreadable`,
  `target-unreadable`;
- link states: `broken-link`, `wrong-target`, `missing-locked`.

The audit hashes recorded copies concurrently (`-j/--jobs`).

### 6.4 Lint

`manager.py lint` discovers every `SKILL.md` under the registry, every existing
agent skills folder, every recorded hard-copy target, and any `-i/--into` root;
deduplicates by real path; reads frontmatter concurrently; and warns when the
description exceeds `-m/--max-description` (default 1024). Missing frontmatter
or a missing description is also a warning. Summary counts: roots, files
checked, hard copies tracked, description warnings, sync issues. `-S/--strict`
turns findings into exit code 1.

### 6.5 Display and reporting

Rich tables/panels when available, deterministic ASCII otherwise; command and
flag echo; a warning banner that survives `--quiet`. Full specification in
`docs/display-architecture.md`.

## 7. Data formats

| File | Owner | Format | Notes |
|---|---|---|---|
| `skills-lock.json` | `-l/--lock`, `-R/--refresh` | existing schema | unrelated keys preserved |
| `manager-copies.json` | hard-copy writes | version 1, `copies` map | machine-local; ignored by git |
| backup zip | `-R/--refresh` | `skill-sync-backup-YYYYmmdd-HHMMSS.zip` in home | deduplicates real paths |

## 8. File map

| Path | Role |
|---|---|
| `manager.py` | CLI, display layer, deploy/refresh/lint, audit, manifest |
| `docs/display-architecture.md` | output layer specification |
| `docs/manager-migration.md` | this inventory |
| `AGENTS.md` | source deployed by `manager.py agent` |
| `skills-lock.json` | lock records consumed by refresh/audit |

## 9. Verification performed

Sandbox run with `MANAGER_HOME` redirected to a temporary home and a temporary
registry:

1. default command links a skill; destination is a link/junction;
2. `-A qoder` writes only qoder's folder;
3. `-c` produces a real directory and a manifest record with source and both
   fingerprints;
4. changing the source makes `lint` report `source-changed`;
5. `-R` recopies the changed source; a second lint is clean;
6. `-i` creates a missing destination root and links into it;
7. `-i -c` creates a real copy and is discovered by `lint --into`;
8. `agent` deploys a link, then `agent -c` a tracked copy;
9. `--list` enumerates the registry;
10. `-d` mutates nothing and says `would ...`;
11. a locally edited copy blocks refresh until `-f`;
12. `-S` returns 1 only when findings exist;
13. folded, literal, single- and double-quoted frontmatter all parse;
14. rich output and `--jobs 1` both run clean.
