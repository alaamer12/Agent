#!/usr/bin/env python3
"""Run a capture matrix into a directory and record a manifest.

Pair with palette_diff.py: capture the same config before and after the migration, then diff
the two output directories. The config is the only stack-specific part; the runner is not.

Config (JSON)
{
  "output_file": "shot.png",
  "cwd": ".",
  "setup":   ["npm run build", {"command": "python -m http.server 3000", "background": true}],
  "teardown": [],
  "states": [
    {"name": "home-light",
     "command": "npx playwright screenshot --viewport-size=1280,800 http://127.0.0.1:3000 {out}",
     "env": {"FORCE_THEME": "light"}},
    {"name": "home-dark", "command": "... {out}", "env": {"FORCE_THEME": "dark"}}
  ]
}

Placeholders in commands: {out} (absolute output image path), {name} / {state} (state name).
Commands intentionally run through the platform shell (pipes, env, npx, emulator CLIs) and the
config is executable input: only run trusted configs. State names are restricted to
[A-Za-z0-9._-]; {out} is inserted raw, so quote it in the command if your paths may contain spaces.

Output
  <out>/<state>/<output_file>   one capture per state
  <out>/manifest.json           git commit, timestamp, config hash, commands, image sha256

Usage
  python capture_matrix.py --config capture.json --out .parity/before
  python capture_matrix.py --config capture.json --out .parity/after --only home-light,home-dark
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time

SAFE_NAME = re.compile(r"^[A-Za-z0-9._-]+$")


def sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_commit(cwd: str) -> str | None:
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=cwd,
                             capture_output=True, text=True, check=True)
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def run_entry(entry, cwd: str, env: dict) -> subprocess.Popen | None:
    """Run one setup/teardown entry. Returns a process for background entries."""
    if isinstance(entry, str):
        entry = {"command": entry}
    if entry.get("background"):
        return subprocess.Popen(entry["command"], cwd=cwd, shell=True,
                                env={**env, **(entry.get("env") or {})})
    subprocess.run(entry["command"], cwd=cwd, shell=True, check=True,
                   env={**env, **(entry.get("env") or {})})
    return None


def stop_process(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                       capture_output=True, text=True)
    else:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a styleup capture matrix with a manifest.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--only", default=None, help="comma-separated state names")
    args = parser.parse_args()

    with open(args.config, encoding="utf-8") as fh:
        raw = fh.read()
    config = json.loads(raw)
    output_file = config.get("output_file") or "shot.png"
    cwd = config.get("cwd") or os.getcwd()
    states = config.get("states") or []
    if args.only:
        wanted = [name.strip() for name in args.only.split(",") if name.strip()]
        known = {state["name"] for state in states}
        unknown = [name for name in wanted if name not in known]
        if unknown:
            print(f"Unknown state(s): {', '.join(unknown)}")
            return 2
        states = [state for state in states if state["name"] in wanted]

    out_dir = os.path.abspath(args.out)
    unsafe = [state["name"] for state in states if not SAFE_NAME.match(str(state["name"]))]
    if unsafe:
        print(f"Unsafe state name(s) (use A-Za-z0-9._- only): {', '.join(map(str, unsafe))}")
        return 2

    os.makedirs(out_dir, exist_ok=True)
    env = dict(os.environ)
    background: list[subprocess.Popen] = []
    manifest_states = []

    try:
        for entry in config.get("setup") or []:
            proc = run_entry(entry, cwd, env)
            if proc is not None:
                background.append(proc)
        for state in states:
            name = state["name"]
            state_dir = os.path.join(out_dir, name)
            os.makedirs(state_dir, exist_ok=True)
            target = os.path.join(state_dir, output_file)
            command = (state["command"]
                       .replace("{out}", target)
                       .replace("{name}", name)
                       .replace("{state}", name))
            state_env = {**env, **(state.get("env") or {})}
            print(f"== {name} ==", flush=True)
            time_started = time.time()
            subprocess.run(command, cwd=cwd, shell=True, check=True, env=state_env)
            if not os.path.exists(target):
                print(f"  ERROR: command finished but wrote no image at {target}")
                return 1
            manifest_states.append({
                "name": name,
                "command": command,
                "duration_s": round(time.time() - time_started, 2),
                "image": os.path.join(name, output_file).replace(os.sep, "/"),
                "sha256": sha256_file(target),
                "bytes": os.path.getsize(target),
            })
            print(f"  captured ({manifest_states[-1]['duration_s']}s)")
    finally:
        for entry in config.get("teardown") or []:
            try:
                run_entry(entry, cwd, env)
            except Exception as exc:  # teardown must never hide the real failure
                print(f"  teardown warning: {exc}")
        for proc in background:
            stop_process(proc)

    manifest = {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "git_commit": git_commit(cwd),
        "config": os.path.abspath(args.config),
        "config_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "output_file": output_file,
        "states": manifest_states,
    }
    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
    print(f"captured {len(manifest_states)} state(s) -> {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
