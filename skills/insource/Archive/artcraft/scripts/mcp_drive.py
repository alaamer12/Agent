#!/usr/bin/env python3
"""Drive a running ArtCraft app over MCP (<app>-cli mcp --attach <port>).

Usage: python mcp_drive.py <cli-exe> <port> <steps.json> [--timeout 15]

steps.json is a list of steps, each:
  {"tool": "open_file", "args": {...}}                      call an MCP tool
  {"tool": "screenshot", "args": {...}, "save": "f.png"}    save image result
  {"tool": "run_command", "args": {"command": ..., "params": ...}}
  {"wait": 0.5}                                             sleep seconds

The app must run with:  <app> [--control <port>]   (the GUI's control-port flag).
Prints one summary line per step; screenshots saved next to cwd.
"""
import json, subprocess, sys, threading, time, base64

def main():
    if len(sys.argv) < 4:
        print(__doc__); sys.exit(2)
    cli, port, steps_file = sys.argv[1], sys.argv[2], sys.argv[3]
    timeout = 15
    if "--timeout" in sys.argv:
        timeout = float(sys.argv[sys.argv.index("--timeout") + 1])
    steps = json.load(open(steps_file, encoding="utf-8"))
    p = subprocess.Popen([cli, "mcp", "--attach", port],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace")
    out = {}
    def reader():
        for line in p.stdout:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if "id" in d:
                out[d["id"]] = d
    threading.Thread(target=reader, daemon=True).start()

    def send(obj):
        p.stdin.write(json.dumps(obj) + "\n"); p.stdin.flush()

    def call(rid):
        t0 = time.time()
        while rid not in out and time.time() - t0 < timeout:
            time.sleep(0.05)
        return out.pop(rid, None)

    send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2025-06-18", "capabilities": {},
        "clientInfo": {"name": "mcp_drive", "version": "1"}}})
    if not call(1):
        print("FAIL: no initialize reply — is the app running with --control " + port + "?")
        sys.exit(1)
    send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    rid = 1
    for i, s in enumerate(steps):
        if "wait" in s:
            time.sleep(s["wait"]); continue
        rid += 1
        send({"jsonrpc": "2.0", "id": rid, "method": "tools/call",
              "params": {"name": s["tool"], "arguments": s.get("args", {})}})
        r = call(rid)
        if r is None:
            print(f"step {i} {s['tool']}: TIMEOUT"); continue
        res = r.get("result", {})
        saved = False
        if s.get("save"):
            for c in res.get("content", []):
                if c.get("type") == "image":
                    open(s["save"], "wb").write(base64.b64decode(c["data"]))
                    print(f"step {i} {s['tool']}: saved {s['save']}"); saved = True
        if not saved:
            err = r.get("error") or res.get("isError")
            text = ""
            for c in res.get("content", []):
                if c.get("type") == "text":
                    text = c["text"][:160]; break
            print(f"step {i} {s['tool']}: {'ERR ' + str(err)[:160] if err else 'ok ' + text}")
    p.terminate()

if __name__ == "__main__":
    main()
