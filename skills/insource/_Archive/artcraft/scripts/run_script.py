#!/usr/bin/env python3
"""Run an ArtCraft CLI `run` script and report failures cleanly (no JSON dumps).

Usage: python run_script.py <cli-exe> <script.json> [--out file] [--in file] [--ids NAME1,NAME2]

Prints one line per failure (step, command, error) or the "wrote ..." line on success.
With --ids, also prints "id <n> = <name>" for created layers whose step names match
(works for any create command: names are read back from the script's own params).
Exits non-zero when the run failed.
"""
import json, subprocess, sys

def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print(__doc__); sys.exit(2)
    cli, script = args[0], args[1]
    rest = args[2:]
    cmd = [cli, "run", script]
    want_ids = []
    i = 0
    while i < len(rest):
        if rest[i] in ("--out", "--in"):
            cmd += [rest[i], rest[i + 1]]; i += 2
        elif rest[i] == "--ids":
            want_ids = rest[i + 1].split(","); i += 2
        else:
            cmd.append(rest[i]); i += 1
    # map step index -> created layer name from the script's own params (frame.create
    # results carry only the id; node.create results carry the node)
    step_names = {}
    try:
        raw = json.load(open(script, encoding="utf-8"))
        steps = raw.get("commands", raw) if isinstance(raw, dict) else raw
        for n, s in enumerate(steps):
            p = s.get("params") or {}
            if isinstance(p, dict) and isinstance(p.get("name"), str):
                step_names[n] = p["name"]
    except Exception:
        pass
    p = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    fails = 0
    for line in p.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if isinstance(d, dict) and d.get("ok") is False:
            fails += 1
            print(f"FAIL step {d.get('step')} {d.get('command')}: {str(d.get('error'))[:400]}")
        elif isinstance(d, dict):
            res = d.get("result") or {}
            name = step_names.get(d.get("step")) or (
                res.get("node", {}).get("name") if isinstance(res.get("node"), dict) else res.get("name"))
            if name in want_ids and res.get("id") is not None:
                print(f"id {res['id']} = {name}")
    for e in (p.stderr or "").strip().splitlines():
        if e.strip() and "wrote" not in e:
            print("stderr:", e[:300])
    if fails or p.returncode != 0:
        print(f"RUN FAILED ({fails} bad steps) - rolled back; fix and rerun")
        sys.exit(1)
    wrote = next((l.strip() for l in ((p.stdout or "") + (p.stderr or "")).splitlines()
                  if "wrote" in l), "OK")
    print(wrote)

if __name__ == "__main__":
    main()
