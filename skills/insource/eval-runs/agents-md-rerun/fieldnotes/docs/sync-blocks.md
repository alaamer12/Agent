# Sync Blocks - Tidepool

The tables section 24 governs: every writable meaning with more than one home, one named block per
meaning, its own table. The law and the same-change duty live in `AGENTS.md` section 24; this file
is the body. An edit that changes a block's meaning updates EVERY row of its table in the same
change, phrased per home; a moved anchor gets re-anchored in that same change.

## Block: version-declaration-sites

| Location | Line anchor | Carries |
|---|---|---|
| `pyproject.toml` | `project.version` field | the external base - PyPI's release identity |
| `package.json` | `"version"` key | the same base, web bundle metadata |
| `services/api/build.py` | `BUILD` constant | the internal track - strictly increasing, CI/logs/telemetry only |

The About page is deliberately NOT a row: it READS the runtime value (section 18) - a reader is not
a writable home.
