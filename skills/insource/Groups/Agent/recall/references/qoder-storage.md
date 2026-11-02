# This harness's session storage (verified)

**Verification: every path and recipe below was run against live session
data on 2026-10-23 (Qoder CLI, Windows, Git Bash).** Re-verify after
harness updates — storage layouts move. On any *other* environment, do not
assume these paths exist; run the discovery procedure from [`recovery.md`](recovery.md) §Step 1
and record findings here (or per-environment) with verification labels.

## Where sessions live

```
~/.qoder/projects/<project-slug>/<session-uuid>.jsonl     # the conversation
~/.qoder/logs/sessions/<project-slug>/<session-uuid>/     # per-session logs
~/.qoder/plans/  ~/.qoder/file-history/  ~/.qoder/state.json
```

- `<project-slug>` = the project's absolute path, drive colon and separators
  folded (e.g. `F--Projects-Agent-skills-insource`). The **current** project
  is almost always the right directory; list its `.jsonl` files by mtime for
  recent sessions.
- Other projects' sessions are readable the same way when the user names an
  unrelated past conversation.
- Files are live-append: the *current* session can itself be grepped (proven
  — its first messages were extracted while it ran).

## Record schema (observed)

Newline-delimited JSON. Each record's `type` field discriminates:

| type | is a conversation message? | notes |
|---|---|---|
| `user` | yes | `message.content` = string or list of parts |
| `assistant` | yes | parts include `thinking`, `text`, `tool_use` |
| `system` | partly | system-level records |
| `attachment` | content | files/refs attached to turns |
| `ai-title` | no | `aiTitle` — human-readable session title(s), latest wins |
| `active-leaf` | no | tree/branch state (`leafUuid`, `explicit`) |
| `runtime-config`, `workspace-directories`, `worktree-state`, `file-history-snapshot`, `last-prompt` | no | harness bookkeeping — skip when reconstructing |

Message-bearing records also carry: `sessionId`, `timestamp`, `uuid` +
`parentUuid` (ordering/relationships), `cwd`, `gitBranch`, `version`,
`isSidechain`. Tool calls appear as assistant parts (`type: tool_use`,
with `name`/`input`); results as user-message parts (`type: tool_result`).
**A turn spans multiple records — never assume one record = one message,
and never trust record order alone without checking `timestamp`/uuid links.**

## Verified recipes

**1. List recent sessions with titles (locating, recovery.md §Step 2):**

```python
import json, glob, os, datetime
proj = os.path.expanduser("~/.qoder/projects/<project-slug>")
rows = []
for f in glob.glob(proj + "/*.jsonl"):
    title = ""
    for line in open(f, encoding="utf-8", errors="ignore"):
        if '"ai-title"' in line:
            try: title = json.loads(line).get("aiTitle", title)
            except Exception: pass
    rows.append((os.path.getmtime(f), os.path.basename(f), title,
                 round(os.path.getsize(f) / 1e6, 2)))
for mt, f, t, mb in sorted(rows, reverse=True):
    print(datetime.datetime.fromtimestamp(mt).strftime("%Y-%m-%d %H:%M"),
          f[:8], f"{mb}MB", t)
```

**2. Surface-level digest of a range — user text + assistant `text` parts
(skips thinking/tool noise), line-index preserved for chunk tracking:**

```python
import json, sys
n = 0
for i, line in enumerate(open(sys.argv[1], encoding="utf-8", errors="ignore")):
    if n >= 4: break                      # chunk budget
    try: r = json.loads(line)
    except Exception: continue
    if r.get("type") not in ("user", "assistant"): continue
    c = r.get("message", {}).get("content")
    if isinstance(c, str) and c.strip() and not c.startswith("{"):
        print(f"[{i}] {r['type']}: {c[:90]}"); n += 1
    elif isinstance(c, list):
        for p in c:
            if isinstance(p, dict) and p.get("type") == "text" and p.get("text","").strip():
                print(f"[{i}] {r['type']}: {p['text'][:90]}"); n += 1; break
```

**3. Full-fidelity pass** — same iteration, but keep *every* part: `thinking`
(flag as internal), `tool_use` (emit `name` + `input`), `tool_result` (emit
paired by `tool_use_id`), `attachment`; emit `timestamp` per record; count
records consumed per range so chunk boundaries are provable (no skip/dup).

**4. Find a session by distinctive content** (when title/date don't
identify it):

```bash
grep -l "distinctive phrase" ~/.qoder/projects/*/*.jsonl
```

grep the raw files *first*, then parse only hits — cheap, and the match
line's index is the natural chunk anchor to start reading from.

## Limits observed

- Titles update as a session evolves; an old session's `aiTitle` may describe
  its *first* topic — verify by content, not title alone.
- Compaction summaries live in the *new* session's context, not as records
  in the old `.jsonl` — the old file stays the original; prefer it.
- Very large `tool_result` payloads dominate file size (a 3 MB file was
  ~2.7 MB of tool data) — for surface-level depth, drop them by part type
  before loading ranges into context; for full fidelity, chunk smaller.
