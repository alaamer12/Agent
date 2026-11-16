#!/usr/bin/env python3
"""decode_status.py - turn an exit code / exception code / signal into meaning + next step.

  decode_status.py 0xC000027B 8000000E
  decode_status.py 139 SIGABRT EXC_BREAKPOINT 0x8badf00d
  decode_status.py -- -1073741189          # signed exit codes work too
  decode_status.py --json 0xC0000005 ; decode_status.py --android 6

Ambiguous small numbers (11, 9...) are shown under every plausible reading (exit code / signal number /
shell 128+N) so you choose by evidence, not habit.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import codes, parse_number, hx, ntstatus, hresult, class_name  # noqa: E402

ANDROID = False


def decode(token):
    C = codes()
    out, t = [], token.strip()
    up = t.upper()
    for num, s in C["signals"].items():
        if up in (s["name"], s["name"][3:]):
            out.append(("signal %s (Linux numbering)" % num, s["name"], s["class"], s["meaning"] +
                        ("  [catchable]" if s["catchable"] else "  [NOT catchable]") + ("  [core by default]" if s["core"] else "")))
    if up in C["apple_exceptions"]:
        e = C["apple_exceptions"][up]
        out.append(("Apple exception type", up, e["class"], "%s (signal %s)" % (e["meaning"], e["signal"])))
    for name, d in C["ntstatus"].items():
        if up == d["name"].split(" ")[0]:
            out.append(("NTSTATUS 0x" + name, d["name"], d["class"], d["meaning"] + "\n      next: " + d["next"]))
    if out:
        return out
    n = parse_number(t)
    if n is None:
        return [("?", t, "?", "not a number and not a known name")]
    hexkey = "%08X" % n
    d, h = ntstatus(n), hresult(n)
    if d:
        out.append(("NTSTATUS " + hx(n), d["name"], d["class"], d["meaning"] + "\n      next: " + d["next"]))
    if h:
        out.append(("HRESULT " + hx(n), h["name"], "-", h["meaning"] + "\n      next: " + h["next"]))
    if hexkey in C["apple_termination_codes"]:
        a = C["apple_termination_codes"][hexkey]
        out.append(("Apple termination code", hx(n), a["class"], a["meaning"]))
    if not d and not h and n > 0xFFFF and hexkey not in C["apple_termination_codes"] and hexkey not in C["exit_codes"]:
        sev = {0: "success", 1: "informational", 2: "warning", 3: "error"}[(n >> 30) & 3]
        out.append(("NTSTATUS-shaped " + hx(n), "unknown to this table", "?",
                    "severity=%s. Look it up in ntstatus.h; do not guess." % sev))
    if n <= 255 or t in C["exit_codes"] or hexkey in C["exit_codes"]:
        key = t if t in C["exit_codes"] else (hexkey if hexkey in C["exit_codes"] else str(n))
        if key in C["exit_codes"]:
            e = C["exit_codes"][key]
            out.append(("process exit code " + key, "", e["class"], e["meaning"]))
        if str(n) in C["signals"]:
            s = C["signals"][str(n)]
            out.append(("signal %d (if this is a signal number)" % n, s["name"], s["class"], s["meaning"]))
        if 129 <= n <= 192 and str(n - 128) in C["signals"]:
            s = C["signals"][str(n - 128)]
            out.append(("shell exit status 128+%d (if run via a shell)" % (n - 128), s["name"], s["class"], s["meaning"]))
        if ANDROID and str(n) in C["android_exit_reasons"]:
            out.append(("Android ApplicationExitInfo reason", C["android_exit_reasons"][str(n)], "?", ""))
    return out or [("number %d" % n, hx(n), "?", "no match in the table")]


def main():
    global ANDROID
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("values", nargs="+")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--android", action="store_true", help="also read small numbers as ApplicationExitInfo reasons")
    a = ap.parse_args()
    ANDROID = a.android
    results = {v: decode(v) for v in a.values}
    if a.json:
        print(json.dumps({v: [dict(kind=k, name=n, cls=c, meaning=m) for k, n, c, m in r] for v, r in results.items()}, indent=1))
        return
    for v, rows in results.items():
        print("== %s" % v)
        for kind, name, cls, meaning in rows:
            cl = "  class %s = %s" % (cls, class_name(cls).split(":")[0]) if cls not in ("?", "-") else ""
            print("  - %s: %s%s\n      %s" % (kind, name, cl, meaning))
        print()


if __name__ == "__main__":
    main()
