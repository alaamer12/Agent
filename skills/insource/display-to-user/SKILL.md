---
name: display-to-user
description: Use this skill whenever you (Claude) are running as a remote coding agent and the user asks you to "show", "display", "let me see", or "give me a link to see" what you've done to their project — the current state of files, or just the changes so far. Also trigger this if the user asks for a way to visually browse the project tree, preview a README or HTML file you produced, or share a live view of the repo with someone else. This spins up a local web viewer (file tree + git status + file preview) and tunnels it with ngrok so the user gets a real clickable URL back, rather than you pasting file contents into chat.
---

# display-to-user

Give the user (or someone they forward the link to) a live, browsable view
of the project you're working in: a file tree, git change highlighting, and
rendered previews of Markdown/HTML files — reachable from a public URL via
ngrok, since you're running remotely and the user can't just open
`localhost` themselves.

## When to use this

Trigger on requests like:
- "show me what you've done"
- "let me see the project"
- "can I get a link to browse the files"
- "display the changes so far"
- "I want to preview that README you wrote"

Don't use this for a request to see the content of ONE specific file in
chat ("show me what's in `config.py`") — just read and paste that inline.
This skill is for browsing/previewing, not single-file dumps.

## Prerequisites

- Python 3 on the machine actually running the server (this is usually you,
  the agent, if you're running in the user's environment — not the user's
  separate local machine, unless they've asked you to hand them files to
  run themselves).
- `git` installed, if the project is a git repo (optional — the viewer
  degrades gracefully to "no git status" otherwise).
- `ngrok` installed and authenticated on the machine that will run the
  tunnel command. This is almost always the same machine as the server
  — if you can run `server.py` yourself, you can very likely run `ngrok`
  yourself too, since they need to reach the same `localhost` port.

## Critical invariant: never tunnel a port with nothing listening on it

ngrok does not verify the target is alive — `ngrok http <port>` will open a
public tunnel to that port whether or not anything answers there, and the
user will just get connection errors through a URL that looks like it
should work. **The server must be confirmed up and answering on the target
port before ngrok is started, every time**, with no exceptions for "it
should be fine" or "I just started it." `scripts/launch.py` (below)
enforces this automatically — use it rather than starting the server and
ngrok as two independent, unordered steps.

## Recommended: one command via `scripts/launch.py`

```bash
python3 <skill_dir>/scripts/launch.py --root /path/to/the/actual/project --port 8420
```

This does all of the following, in order, and refuses to proceed to the
next step if the previous one failed:
1. Starts `templates/server.py` in the background against `--root`.
2. Polls `http://127.0.0.1:<port>/` until it answers `200` (up to ~10s) —
   **this is the liveness check** that guarantees ngrok never tunnels to a
   dead port. If the server never comes up, it exits with an error and
   never touches ngrok at all.
3. Runs the ngrok `check` (install + auth) — see the failure handling
   below.
4. Starts the ngrok tunnel and prints the public HTTPS URL as its last
   line of stdout on success.

`--root` defaults to the current directory if omitted, matching
`server.py`'s own default. Omit `--port` to use the default `8420`.

If ngrok isn't ready, `launch.py` prints which check failed
(`NOT_INSTALLED` or `NOT_AUTHED`) and confirms the viewer server is still
running locally so nothing is wasted — read `references/ngrok-setup.md`
and relay the exact remediation steps to the user; don't guess or paraphrase
vaguely. **Always use ngrok's default random URL** (e.g.
`https://a1b2c3.ngrok-free.app`) — do not pass `--subdomain` unless the
user explicitly asked for a specific custom one by name (it requires a paid
plan and will make the command fail on free accounts).

Once you have the URL, report it back to the user directly — this is the
actual deliverable of the whole skill, don't bury it in a longer message:

> Here's a live view of the project: **https://a1b2c3.ngrok-free.app**
> It shows the file tree, highlights what's changed, and you can
> right-click any Markdown or HTML file to preview it.

### Cleanup

```bash
python3 <skill_dir>/scripts/ngrok_tunnel.py stop
```
This stops the ngrok agent process. `launch.py` intentionally leaves both
the viewer server and the tunnel running afterward (the user may still be
looking at the link) — kill the server process yourself (its pid is
printed by `launch.py`) once the user is done, or leave it running if they
want continued access.

## Manual path (only if you need finer control)

If you need to run the server and tunnel as separate steps — e.g. to
restart just the tunnel without restarting the server, or to run the server
somewhere other than where `launch.py` lives — do it in this exact order
and verify each step before moving to the next:

1. Copy `templates/server.py` and `templates/index.html` together into a
   writable location (they must stay in the same folder as each other).
2. Start it: `python3 server.py --root /path/to/project --port 8420`
3. **Verify it's actually listening before going anywhere near ngrok:**
   ```bash
   curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8420/
   ```
   Expect `200`. If you don't get it, stop and debug the server — do not
   proceed to start a tunnel.
4. Only now run `python3 <skill_dir>/scripts/ngrok_tunnel.py check`, then
   `start --port 8420` if `check` reports `OK`.

See `references/server-architecture.md` for the full CLI flag and API
reference.

## Troubleshooting

- **The tree only shows a couple of files, not the whole project** — this
  is not a bug in `server.py`; it means `--root` is pointing somewhere
  other than the project the user actually meant (e.g. an empty or nearly
  empty folder). Copying `templates/server.py` and `templates/index.html`
  directly into the target project and running from there is a completely
  normal, supported way to use this tool — do NOT add logic that treats
  the tool's own files being present in the served folder as an error;
  that IS the expected setup for most users. If the tree looks wrong,
  check `--root` is actually the project path, not that the two tool
  files happen to be sitting inside it.
- **The ngrok URL loads but shows connection errors / "site can't be
  reached"** — this is the exact failure this skill's ordering exists to
  prevent. It means the server process died or was never actually
  listening on the port ngrok was pointed at (wrong `--port` value between
  the two commands is the most common cause). Re-run `launch.py` from
  scratch rather than trying to patch a half-working setup.
- **Server starts but `/api/tree` errors** — check `--root` actually points
  at a real directory the server process can read; see
  `references/server-architecture.md`.
- **ngrok `start` never returns a URL** — check
  `/tmp/display-to-user-ngrok.log` (ngrok's own output) for the actual
  failure, e.g. the free-plan limit of one online agent session at a time —
  an old tunnel from a previous run may still be registered.
- **Icons look wrong / tree looks broken** — this almost always means a
  stale copy of `index.html` is being served (e.g. one without the
  embedded icon manifest). Recopy `templates/index.html` fresh rather than
  debugging in place.

## Reference files

- `references/ngrok-setup.md` — install/auth instructions per OS, and the
  custom-subdomain caveat.
- `references/server-architecture.md` — full API surface, CLI flags, and
  the design decisions behind the server/frontend (read this before making
  any code changes to `templates/server.py` or `templates/index.html`).
