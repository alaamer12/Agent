#!/usr/bin/env python3
"""
ngrok_tunnel.py — start an ngrok HTTP tunnel to a local port and report
back its public URL, using ngrok's local inspection API rather than
screen-scraping stdout.

Usage:
    python3 ngrok_tunnel.py check
        Verifies ngrok is installed and has a configured authtoken.
        Exits 0 if both are true, prints a specific remediation message
        and exits 1/2 otherwise.

    python3 ngrok_tunnel.py start --port 8420
        Starts `ngrok http <port>` in the background, polls the local
        API (http://127.0.0.1:4040/api/tunnels) until the tunnel is up,
        and prints the public HTTPS URL to stdout as the last line.
        The ngrok process is left running; the caller is responsible
        for stopping it (see `stop`).

    python3 ngrok_tunnel.py stop
        Stops any ngrok agent process this script started (best-effort:
        looks for a pidfile written by `start`).
"""
import argparse
import json
import subprocess
import sys
import time
import urllib.request
import urllib.error

NGROK_API = "http://127.0.0.1:4040/api/tunnels"
PIDFILE = "/tmp/display-to-user-ngrok.pid"


def ngrok_installed():
    try:
        subprocess.run(
            ["ngrok", "version"],
            capture_output=True, text=True, timeout=5,
        )
        return True
    except FileNotFoundError:
        return False
    except subprocess.TimeoutExpired:
        return True  # binary exists, just slow


def ngrok_authed():
    """ngrok config check exits 0 only if the config file is valid AND
    (as of v3) an authtoken has been added — a fresh install with no
    authtoken fails this check."""
    try:
        result = subprocess.run(
            ["ngrok", "config", "check"],
            capture_output=True, text=True, timeout=5,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False
    except subprocess.TimeoutExpired:
        return False


def cmd_check():
    if not ngrok_installed():
        print("NOT_INSTALLED")
        return 2
    if not ngrok_authed():
        print("NOT_AUTHED")
        return 1
    print("OK")
    return 0


def fetch_public_url(retries=20, delay=0.5):
    """Poll ngrok's local API until a tunnel appears, return its https
    public_url. Prefers https over http if both are listed."""
    for _ in range(retries):
        try:
            with urllib.request.urlopen(NGROK_API, timeout=2) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            tunnels = data.get("tunnels", [])
            if tunnels:
                https_tunnels = [t for t in tunnels if t.get("public_url", "").startswith("https://")]
                chosen = https_tunnels[0] if https_tunnels else tunnels[0]
                return chosen["public_url"]
        except (urllib.error.URLError, ConnectionRefusedError, json.JSONDecodeError):
            pass
        time.sleep(delay)
    return None


def cmd_start(port, region=None, subdomain=None, extra_args=None):
    if not ngrok_installed():
        print("ERROR: ngrok is not installed.", file=sys.stderr)
        return 2
    if not ngrok_authed():
        print("ERROR: ngrok has no authtoken configured.", file=sys.stderr)
        return 1

    cmd = ["ngrok", "http", str(port), "--log=stdout"]
    if region:
        cmd += ["--region", region]
    if subdomain:
        # only works on paid ngrok plans; caller should only pass this
        # if the user explicitly asked for a custom subdomain
        cmd += ["--subdomain", subdomain]
    if extra_args:
        cmd += extra_args

    log_path = "/tmp/display-to-user-ngrok.log"
    with open(log_path, "w") as log_file:
        proc = subprocess.Popen(
            cmd,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )

    with open(PIDFILE, "w") as f:
        f.write(str(proc.pid))

    url = fetch_public_url()
    if url is None:
        print(f"ERROR: ngrok did not come up in time. Check {log_path}", file=sys.stderr)
        return 3

    print(url)
    return 0


def cmd_stop():
    try:
        with open(PIDFILE) as f:
            pid = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        print("No tracked ngrok process found.")
        return 0
    try:
        import os
        import signal
        os.kill(pid, signal.SIGTERM)
        print(f"Stopped ngrok (pid {pid}).")
    except ProcessLookupError:
        print("ngrok process already gone.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)

    sub.add_parser("check")

    start_p = sub.add_parser("start")
    start_p.add_argument("--port", type=int, required=True)
    start_p.add_argument("--region", type=str, default=None)
    start_p.add_argument("--subdomain", type=str, default=None)

    sub.add_parser("stop")

    args = parser.parse_args()

    if args.action == "check":
        sys.exit(cmd_check())
    elif args.action == "start":
        sys.exit(cmd_start(args.port, region=args.region, subdomain=args.subdomain))
    elif args.action == "stop":
        sys.exit(cmd_stop())


if __name__ == "__main__":
    main()
