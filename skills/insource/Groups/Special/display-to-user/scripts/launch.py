#!/usr/bin/env python3
"""
launch.py — one-command wrapper that starts the display-to-user viewer
server against a project directory and tunnels it with ngrok, printing the
public URL. Designed to be run from anywhere — it does NOT require copying
server.py/index.html into the target project; they stay wherever this skill
is installed and are pointed at the project via --root.

Usage (from anywhere):
    python3 launch.py --root /path/to/project [--port 8420]

Usage (from inside the project you want to show):
    cd /path/to/project
    python3 /path/to/skill/scripts/launch.py

If --root is omitted, defaults to the current working directory — same
default as server.py itself.

This script:
  1. Starts templates/server.py against --root in the background.
  2. Waits for it to answer on --port.
  3. Runs ngrok_tunnel.py check; if not OK, prints remediation and exits
     without starting a tunnel.
  4. Runs ngrok_tunnel.py start and prints the resulting public URL.

It intentionally does NOT stop either process on exit — both the viewer
server and the ngrok tunnel are meant to keep running until the user is
done. Use scripts/ngrok_tunnel.py stop (and kill the server pid printed
below) to tear down.
"""
import argparse
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(SKILL_DIR, "templates")
SERVER_PY = os.path.join(TEMPLATES_DIR, "server.py")
NGROK_HELPER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ngrok_tunnel.py")


def wait_for_server(port, retries=20, delay=0.5):
    url = f"http://127.0.0.1:{port}/"
    for _ in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status == 200:
                    return True
        except (urllib.error.URLError, ConnectionRefusedError):
            pass
        time.sleep(delay)
    return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=str, default=os.getcwd(),
                         help="project directory to serve (default: current directory)")
    parser.add_argument("--port", type=int, default=8420)
    parser.add_argument("--region", type=str, default=None)
    parser.add_argument("--subdomain", type=str, default=None,
                         help="only pass this if the user explicitly asked for a specific "
                              "custom subdomain; requires a paid ngrok plan")
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"ERROR: {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    log_path = "/tmp/display-to-user-server.log"
    with open(log_path, "w") as log_file:
        server_proc = subprocess.Popen(
            [sys.executable, SERVER_PY, "--root", root, "--port", str(args.port)],
            stdout=log_file, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
            start_new_session=True,
        )

    print(f"Started viewer server (pid {server_proc.pid}) for {root} on port {args.port}")

    if not wait_for_server(args.port):
        print(f"ERROR: server did not respond in time. Check {log_path}", file=sys.stderr)
        sys.exit(2)

    check = subprocess.run([sys.executable, NGROK_HELPER, "check"], capture_output=True, text=True)
    status = check.stdout.strip()
    if status != "OK":
        print(f"ngrok is not ready ({status}). See references/ngrok-setup.md for setup steps.", file=sys.stderr)
        print(f"The viewer server is still running locally on port {args.port} if you want to fix ngrok and tunnel it separately.", file=sys.stderr)
        sys.exit(check.returncode or 1)

    start_cmd = [sys.executable, NGROK_HELPER, "start", "--port", str(args.port)]
    if args.region:
        start_cmd += ["--region", args.region]
    if args.subdomain:
        start_cmd += ["--subdomain", args.subdomain]

    start = subprocess.run(start_cmd, capture_output=True, text=True)
    if start.returncode != 0:
        print("ERROR starting ngrok tunnel:", start.stderr.strip(), file=sys.stderr)
        sys.exit(start.returncode)

    public_url = start.stdout.strip().splitlines()[-1]
    print(public_url)


if __name__ == "__main__":
    main()
