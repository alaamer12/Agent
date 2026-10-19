"""Loader for the data files in scripts/data/.

Vocabularies that describe the outside world (named colours, tracker domains, UI phrases in many
languages, technology fingerprints) live in data files rather than code, so they can be extended
or overridden without touching the scripts.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"


def _path(name: str) -> Path:
    p = DATA_DIR / name
    if not p.exists():
        raise FileNotFoundError(f"Missing data file {p} (the skill package is incomplete)")
    return p


@lru_cache(maxsize=None)
def load_json(name: str):
    return json.loads(_path(name).read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def load_lines(name: str) -> tuple[str, ...]:
    """Non-empty, non-comment lines of a text data file."""
    lines = (ln.strip() for ln in _path(name).read_text(encoding="utf-8").splitlines())
    return tuple(ln for ln in lines if ln and not ln.startswith("#"))


def host_listed(host: str, domains) -> bool:
    """True if `host` equals or is a subdomain of any listed domain."""
    host = (host or "").lower().rstrip(".")
    return any(host == d or host.endswith("." + d) for d in domains)
