#!/usr/bin/env python3
"""Fetch an ArtCraft app's documentation from GitHub (Windows/Linux/macOS).

Usage: python fetch_docs.py <app> [out_dir] [branch]
  e.g. python fetch_docs.py myapp            -> throwaway/docs/myapp/
       python fetch_docs.py myapp docs main

Downloads every known docs file from github.com/storytold/<app>/<branch>/docs/
that exists (cli.md, mcp.md, plugins.md, server.md, control-protocol.md, ...).
"""
import os, sys, urllib.request

FILES = ["cli.md", "mcp.md", "plugins.md", "server.md", "control-protocol.md",
         "file-format-parity.md", "introduction.md", "design-notes.md"]

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    app = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join("throwaway", "docs", app)
    branch = sys.argv[3] if len(sys.argv) > 3 else "main"
    base = f"https://raw.githubusercontent.com/storytold/{app}/{branch}/docs/"
    os.makedirs(out, exist_ok=True)
    got = 0
    for f in FILES:
        try:
            with urllib.request.urlopen(base + f, timeout=20) as r:
                data = r.read()
            if data:
                open(os.path.join(out, f), "wb").write(data)
                got += 1
                print(f"got  {f} ({len(data)} bytes)")
        except Exception:
            pass
    print(f"{got}/{len(FILES)} docs saved to {out}")
    if not got:
        print(f"WARN: nothing fetched — check the repo github.com/storytold/{app} and branch {branch}")
        sys.exit(1)

if __name__ == "__main__":
    main()
