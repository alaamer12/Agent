#!/usr/bin/env python3
"""
display-to-user prototype server.
Zero third-party dependencies (stdlib only) so it runs in any project
regardless of language/ecosystem.

Serves:
  GET /              -> index.html (the viewer UI)
  GET /api/tree       -> JSON: {cwd, branch, is_git, tree: [...], changed: [...]}
"""
import argparse
import http.server
import json
import os
import subprocess
import sys
import urllib.parse
from pathlib import Path

MAX_FILE_BYTES = 2 * 1024 * 1024  # 2MB cap for preview/highlight requests


def parse_args():
    parser = argparse.ArgumentParser(
        description="display-to-user: serve a browsable file tree + git status for a project."
    )
    parser.add_argument(
        "--port", "-p", type=int, default=8420,
        help="port to listen on (default: 8420)",
    )
    parser.add_argument(
        "--root", "-r", type=str, default=os.getcwd(),
        help="project directory to serve (default: current working directory)",
    )
    return parser.parse_args()


ARGS = parse_args()
ROOT = Path(ARGS.root).resolve()
PORT = ARGS.port

# Directories we never want to walk into (huge / irrelevant / binary noise)
IGNORE_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    "dist", "build", ".next", ".turbo", "target", ".cache",
}


def run_git(args):
    """Run a git command. Returns (stdout, error_reason) tuple.
    error_reason is None on success, 'not_installed' if git binary missing,
    'not_repo' if the directory is not a git repository, or 'error' for other failures."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            stderr = result.stderr.lower()
            if "not a git repository" in stderr:
                return None, "not_repo"
            return None, "error"
        return result.stdout, None
    except FileNotFoundError:
        return None, "not_installed"
    except subprocess.TimeoutExpired:
        return None, "error"


def get_git_info():
    """Returns (is_git, branch, changed, status_map, git_error).
    git_error is None if git works, 'not_installed' if git binary is missing,
    or 'not_repo' if the directory is not a git repository."""
    branch_out, err = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    is_git = branch_out is not None
    branch = branch_out.strip() if branch_out else None
    git_error = err if not is_git else None

    changed = []
    status_map = {}
    if is_git:
        # --uall ensures individual files inside untracked dirs are listed,
        # not just the directory name (e.g. "Solidjs-tutorial/" as a single entry)
        status_out, _ = run_git(["status", "--porcelain", "-uall"])
        if status_out is not None:
            for line in status_out.splitlines():
                if not line.strip():
                    continue
                code = line[:2].strip()
                path_part = line[3:]
                if " -> " in path_part:
                    path_part = path_part.split(" -> ")[-1]
                path_part = path_part.strip('"')
                if path_part.endswith("/"):
                    path_part = path_part[:-1]
                st = "U" if code == "??" else "M"
                changed.append(path_part)
                status_map[path_part] = st
    return is_git, branch, changed, status_map, git_error


def is_visible_path(rel_posix: str, staged_paths: set = None) -> bool:
    """Returns True if this path would be shown in the file tree.
    A path is hidden if any of its components are in IGNORE_DIRS or start
    with '.' (except '.github') — UNLESS the path is explicitly staged,
    in which case we always show it."""
    # Always hide __pycache__ and other IGNORE_DIRS regardless of staging
    parts = rel_posix.split("/")
    for part in parts:
        if part in IGNORE_DIRS:
            return False
    # If path is explicitly staged/tracked by git, show it even if it's a dotfile
    if staged_paths and rel_posix in staged_paths:
        return True
    # Otherwise hide dot-prefixed files/dirs (except .github)
    for part in parts:
        if part.startswith(".") and part not in (".github",):
            return False
    return True


def get_status_for_path(rel_path: str, status_map: dict) -> str | None:
    """Returns 'M' or 'U' if rel_path matches a changed entry or lives inside an untracked dir."""
    for c, st in status_map.items():
        if rel_path == c or rel_path.startswith(c + "/"):
            return st
    return None


def build_tree(base: Path, status_map: dict):
    """Recursively build a nested tree structure, skipping ignored dirs.
    Marks each node `changed: bool` and `status: 'M'|'U'|None`.
    Dotfiles/dotdirs that are explicitly in status_map are shown."""
    staged_paths = set(status_map.keys())

    def is_explicitly_changed(name: str, rel: str) -> bool:
        """True if this name or any sub-path of rel is in status_map."""
        if rel in status_map:
            return True
        prefix = rel + "/"
        return any(p.startswith(prefix) for p in status_map)

    def walk(dir_path: Path):
        entries = []
        try:
            children = sorted(
                dir_path.iterdir(),
                key=lambda p: (p.is_file(), p.name.lower()),
            )
        except PermissionError:
            return entries

        for child in children:
            if child.name in IGNORE_DIRS:
                continue
            rel = child.relative_to(base).as_posix()
            # Skip dotfiles/dotdirs unless they are explicitly staged/changed
            if child.name.startswith(".") and child.name not in (".github",):
                if not is_explicitly_changed(child.name, rel):
                    continue
            if child.is_dir():
                sub = walk(child)
                dir_st = "M" if any(n.get("status") == "M" for n in sub) else ("U" if any(n.get("status") == "U" for n in sub) else None)
                node = {
                    "name": child.name,
                    "path": rel,
                    "type": "dir",
                    "children": sub,
                    "changed": any(n["changed"] for n in sub),
                    "status": dir_st,
                }
            else:
                st = get_status_for_path(rel, status_map)
                node = {
                    "name": child.name,
                    "path": rel,
                    "type": "file",
                    "changed": st is not None,
                    "status": st,
                }
            entries.append(node)
        return entries

    return walk(base)


def safe_resolve(rel_path: str) -> Path:
    """Resolve a client-supplied relative path against ROOT, refusing any
    path that would escape ROOT (via '..', symlinks, or absolute paths).
    Raises ValueError if the path is unsafe."""
    if rel_path.startswith("/") or rel_path.startswith("\\"):
        raise ValueError("absolute paths not allowed")
    candidate = (ROOT / rel_path).resolve()
    try:
        candidate.relative_to(ROOT.resolve())
    except ValueError:
        raise ValueError("path escapes project root")
    return candidate


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # keep stdout quiet

    def _send_json(self, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path, content_type: str):
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        try:
            parsed = urllib.parse.urlsplit(self.path)
            qs = urllib.parse.parse_qs(parsed.query)

            if parsed.path == "/api/tree":
                is_git, branch, changed, status_map, git_error = get_git_info()
                tree = build_tree(ROOT, status_map)
                # Filter changed to only paths actually visible in the tree
                # (excludes IGNORE_DIRS but allows staged dotfiles)
                staged_paths = set(status_map.keys())
                visible_changed = [p for p in changed if is_visible_path(p, staged_paths)]
                self._send_json({
                    "cwd": str(ROOT),
                    "is_git": is_git,
                    "git_error": git_error,  # None | 'not_installed' | 'not_repo' | 'error'
                    "branch": branch,
                    "changed": visible_changed,
                    "tree": tree,
                })
                return

            if parsed.path == "/api/file":
                rel = qs.get("path", [None])[0]
                if not rel:
                    self._send_json_error(400, "missing 'path' query param")
                    return
                try:
                    target = safe_resolve(rel)
                except ValueError as e:
                    self._send_json_error(403, str(e))
                    return
                if not target.is_file():
                    self._send_json_error(404, "not a file")
                    return
                # cap file size we'll ever try to render/highlight
                size = target.stat().st_size
                if size > MAX_FILE_BYTES:
                    self._send_json_error(413, f"file too large ({size} bytes)")
                    return
                try:
                    content = target.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    self._send_json_error(415, "binary file, cannot display as text")
                    return
                self._send_json({
                    "path": rel,
                    "size": size,
                    "content": content,
                })
                return

            # everything else -> index.html (single page app)
            index_path = Path(__file__).parent / "index.html"
            self._send_file(index_path, "text/html; charset=utf-8")
        except FileNotFoundError as e:
            self._send_json_error(404, f"Path not found: {e}")
        except Exception as e:  # last-resort guard so the server never 500s silently
            self._send_json_error(500, f"{type(e).__name__}: {e}")

    def _send_json_error(self, code: int, message: str):
        body = json.dumps({"error": message}).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    if not ROOT.is_dir():
        print(f"[display-to-user] ERROR: {ROOT} is not a directory", file=sys.stderr)
        sys.exit(1)

    print(f"[display-to-user] serving {ROOT} on http://0.0.0.0:{PORT}")
    server = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
