"""Shared helpers for the fatal skill scripts (no third-party dependencies)."""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "assets", "status_codes.json")
_codes = None


def codes():
    global _codes
    if _codes is None:
        with open(DATA, encoding="utf-8") as f:
            _codes = json.load(f)
    return _codes


def parse_number(s):
    """'0xC000027B' | '3221226107' | '-1073741189' | '8000000E' -> unsigned 32-bit int (or None)."""
    s = str(s).strip().lower().rstrip("h")
    if re.fullmatch(r"[0-9a-f]{8}", s):
        return int(s, 16)
    try:
        n = int(s, 16) if s.startswith(("0x", "-0x")) else int(s, 10)
    except ValueError:
        return None
    return n & 0xFFFFFFFF if n < 0 else n


def hx(n, width=8):
    return "0x%0*X" % (width, n)


def ntstatus(n):
    return codes()["ntstatus"].get("%08X" % (n & 0xFFFFFFFF))


def hresult(n):
    return codes()["hresult"].get("%08X" % (n & 0xFFFFFFFF))


def class_name(letter):
    return codes()["classes"].get(letter, "unknown class")


# Raw stack scan + PUBLIC symbols yields plausible-looking but WRONG names. In the DemoApp dump,
# `ReleaseImpl+0x1b2b55`, `RtlLargeIntegerToChar+0xffffffffffffffff`, `_tls_end+0x2d860` and
# `ntdll!sxsisol_SearchActCtxForDllName+0x114` sat beside genuine frames.
_PLACEHOLDER = re.compile(r"(`string'|__ImageBase|_tls_end|_xmm|__PchSym_|_OptionsStorage|c_aTypes|::`vftable'|s_theJitHost|\bg_[A-Za-z]|^_[A-Za-z])")
_FRAME = re.compile(r"^(?:(?P<mod>[^!+\s]+)!)?(?P<sym>.*?)\+0x(?P<off>[0-9a-fA-F]+)$")


def grade_frame(text):
    """-> (grade, reason); grade in {'ok','suspect','unsymbolicated'}. 'ok' = symbol attribution plausible;
    it does NOT prove the frame was on the live call chain."""
    m = _FRAME.match(text.strip())
    if not m or "!" not in text:
        return "unsymbolicated", "module+offset only" if m else "no symbol"
    off = int(m.group("off"), 16)
    if off >= 0x8000000000000000:
        return "suspect", "negative/wrapped offset - symbol is nearest-neighbour noise"
    if off > 0x10000:
        return "suspect", "offset 0x%x is larger than any sane function - name is the nearest public symbol, not the real function" % off
    if _PLACEHOLDER.search(m.group("sym")):
        return "suspect", "data/placeholder symbol, not a function"
    return "ok", ""
