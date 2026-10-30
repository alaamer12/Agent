"""Helpers shared by the capture commands."""
from __future__ import annotations

import os


def resolve_output(path: str) -> str:
    """Expand a `{n}` placeholder to the next unused integer (app_v{n}.png -> app_v3.png),
    so repeated captures build a numbered history instead of overwriting."""
    if "{n}" not in path:
        return path
    n = 1
    while os.path.exists(path.replace("{n}", str(n))):
        n += 1
    return path.replace("{n}", str(n))


def ensure_parent(path: str) -> None:
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)


def utf8_console() -> None:
    """Make stdout/stderr UTF-8 (errors replaced) so non-ASCII titles/paths never crash on a legacy
    Windows console or a pipe that defaults to an ANSI code page."""
    import sys
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


# Browser-like user agent shared by `design` (curl) and `dom` (Playwright). The Chrome version is never frozen
# in code: it comes from the running browser (dom) or from the installed Playwright's metadata (design); the
# constant below is used only when neither is available. Override per run with --user-agent, or globally with the
# CAPTURE_USER_AGENT environment variable.
_FALLBACK_CHROME_VERSION = "124.0.0.0"


def _playwright_chromium_version():
    """Chromium version bundled with the installed Playwright, read from its metadata (no browser launch)."""
    try:
        import importlib.util
        import json
        from pathlib import Path
        spec = importlib.util.find_spec("playwright")
        if not spec or not spec.origin:
            return None
        meta = Path(spec.origin).parent / "driver" / "package" / "browsers.json"
        for b in json.loads(meta.read_text(encoding="utf-8")).get("browsers", []):
            if b.get("name") == "chromium" and b.get("browserVersion"):
                return b["browserVersion"]
    except Exception:
        return None
    return None


def default_user_agent(browser_version=None) -> str:
    import os
    env = os.environ.get("CAPTURE_USER_AGENT")
    if env:
        return env
    version = browser_version or _playwright_chromium_version() or _FALLBACK_CHROME_VERSION
    major = str(version).split(".")[0]          # real Chrome reports a reduced version: <major>.0.0.0
    return (f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            f"(KHTML, like Gecko) Chrome/{major}.0.0.0 Safari/537.36")
