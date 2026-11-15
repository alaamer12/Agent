#!/usr/bin/env python3
"""minidump_report.py - first-look report for a Windows (or Breakpad/Crashpad) minidump. No debugger, no packages.

  minidump_report.py crash.dmp                 # exception + faulting thread + thread overview
  minidump_report.py a.dmp b.dmp --compare     # side-by-side signature table
  minidump_report.py crash.dmp --all-threads   # heuristic scan of every thread
  minidump_report.py crash.dmp --json

Answers, in order: (1) exception code and class of death [exact]; (2) which thread died and where each thread's
instruction pointer was [exact, from saved contexts]; (3) what the dump captured - can the heap/stowed exception be
read? [exact]; (4) what the faulting stack seems to contain [HEURISTIC]. Names come from win_symbolicate.py.
"""
import argparse
import json
import os
import signal
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mdparse import MiniDump, DumpError  # noqa: E402
from _common import ntstatus, hresult, hx, class_name, codes  # noqa: E402


def exception_info(d):
    e = d.exception
    if not e:
        return None
    info = ntstatus(e["code"]) or {}
    m, off = d.module_for(e["address"])
    out = dict(code=hx(e["code"]), name=info.get("name", "unknown to table"), cls=info.get("class", "?"),
               meaning=info.get("meaning", ""), next=info.get("next", ""), thread=hx(e["tid"], 4), address=hx(e["address"], 16),
               address_sym=("%s+0x%x" % (m["name"], off)) if m else "(outside any module)", params=[hx(p, 1) for p in e["params"]])
    if e["code"] == 0xC0000409 and e["params"]:
        out["fast_fail_reason"] = codes()["fast_fail"].get(str(e["params"][0])) or "FAST_FAIL code %d (see winnt.h)" % e["params"][0]
    if e["code"] == 0xC0000005 and len(e["params"]) >= 2:
        kind = {0: "READ", 1: "WRITE", 8: "EXECUTE (DEP)"}.get(e["params"][0], "?")
        out["access"] = "%s of 0x%x%s" % (kind, e["params"][1], "  <- below 0x10000: almost certainly a NULL base pointer" if e["params"][1] < 0x10000 else "")
    return out


def build(d, all_threads=False, max_frames=40):
    threads = []
    for t in d.threads:
        m, off = d.module_for(t["ip"]) if t["ip"] else (None, None)
        threads.append(dict(tid=hx(t["tid"], 4), ip=("%s+0x%x" % (m["name"], off)) if m else ("0x%x" % t["ip"] if t["ip"] else "?"),
                            stack_kb=t["stack_size"] // 1024, is_faulting=bool(d.exception and d.exception["tid"] == t["tid"])))
    r = dict(file=os.path.basename(d.path), size_mb=round(d.size / 1e6, 2), time_utc=str(d.time_utc), arch=d.arch, os=d.os,
             kind=d.dump_kind(), header_flags=d.flag_names or [hex(d.flags)], captured_mb=round(d.captured_bytes / 1e6, 2),
             exception=exception_info(d), threads=threads, scans={})
    st = d.read_stowed()
    if isinstance(st, list):
        for s in st:
            h = hresult(s["hresult"]) or {}
            s["hresult_hex"], s["hresult_name"] = hx(s["hresult"]), h.get("name", "?")
            s["frames_sym"] = [d.sym(a) or "0x%x" % a for a in s.pop("frames")]
            s["exception_address_sym"] = d.sym(s["exception_address"]) if s.get("exception_address") else None
    r["stowed"] = st
    tids = [t["tid"] for t in d.threads] if all_threads else ([d.exception["tid"]] if d.exception else [])
    for tid in tids:
        r["scans"][hx(tid, 4)] = ["%s+0x%x" % (f["module"], f["offset"]) for f in d.scan_stack(tid)][:max_frames]
    r["modules"] = [dict(name=m["name"], version=m["version"], timestamp=hx(m["timestamp"]), pdb=m["pdb"],
                         guid_age=("%s%X" % (m["guid"], m["age"])) if m["guid"] else None) for m in d.modules]
    return r


def print_md(r, app=None):
    p = print
    p("# Minidump report: %s" % r["file"])
    p("- size %.2f MB, captured memory %.2f MB, header time (UTC) %s" % (r["size_mb"], r["captured_mb"], r["time_utc"]))
    p("- %s, Windows %s" % (r["arch"], r["os"]))
    p("- **dump kind: %s**   header flags: %s" % (r["kind"], ", ".join(r["header_flags"])))
    e = r["exception"]
    p("\n## Exception  *(exact - read from the exception record)*")
    if not e:
        p("No exception stream (manual/on-demand dump, not a crash dump). Read thread IPs instead.")
    else:
        p("- code **%s** = %s" % (e["code"], e["name"]))
        if e["cls"] != "?":
            p("- termination class **%s**: %s" % (e["cls"], class_name(e["cls"])))
        if e["meaning"]:
            p("- meaning: %s" % e["meaning"])
        p("- raised on thread **%s** at %s (%s)" % (e["thread"], e["address"], e["address_sym"]))
        p("- parameters: %s" % (", ".join(e["params"]) or "none"))
        for k in ("fast_fail_reason", "access"):
            if k in e:
                p("- %s: %s" % (k.replace("_", " "), e[k]))
        if e["next"]:
            p("- next step: %s" % e["next"])
    st = r["stowed"]
    if st is not None:
        p("\n## Stowed exception(s)  *(exact if readable)*")
        if isinstance(st, str):
            p("- NOT READABLE: %s" % st)
        else:
            for s in st:
                p("- %s inner HRESULT **%s** = %s; form=%d; recorded thread id %s" % (s["signature"], s["hresult_hex"], s["hresult_name"], s["form"], hx(s["thread_id"], 4)))
                if s.get("exception_address_sym"):
                    p("  raised at %s" % s["exception_address_sym"])
                for f in s["frames_sym"]:
                    p("    - %s" % f)
    p("\n## Threads  *(instruction pointers are exact: from each thread's saved context)*")
    p("| thread | instruction pointer | stack KB | |\n|---|---|---|---|")
    for t in r["threads"]:
        p("| %s | %s | %d | %s |" % (t["tid"], t["ip"], t["stack_kb"], "**FAULTING**" if t["is_faulting"] else ""))
    for tid, frames in r["scans"].items():
        p("\n## Heuristic stack scan, thread %s" % tid)
        p("> NOT an unwound call stack: stale slots and data pointers are included and order is approximate. Use it to pick "
          "modules to symbolicate; never quote it as 'the call stack'.")
        for f in frames:
            p("    %s" % f)
    p("\n## Modules" + (" (filtered by '%s')" % app if app else ""))
    p("| module | version | build timestamp | pdb / guid+age |\n|---|---|---|---|")
    for m in r["modules"]:
        if app and app.lower() not in m["name"].lower():
            continue
        p("| %s | %s | %s | %s |" % (m["name"], m["version"] or "", m["timestamp"], (m["pdb"] or "") + (" " + m["guid_age"] if m["guid_age"] else "")))
    p("\n## What this report can and cannot tell you")
    p("- Exact: exception code/address/thread, thread IPs, module list, dump kind.")
    p("- Heuristic: the stack scan. Unknown: function names (win_symbolicate.py) and managed frames (need DAC/SOS or logs).")
    if isinstance(r["stowed"], str):
        p("- The dump lacks the heap, so inner exception details are missing. Enable full dumps for the next crash.")


def compare(reports):
    print("| dump | time (UTC) | code | thread | fault site | kind |\n|---|---|---|---|---|---|")
    for r in reports:
        e = r["exception"] or {}
        print("| %s | %s | %s | %s | %s | %s |" % (r["file"], r["time_utc"][:19], e.get("code", "-"), e.get("thread", "-"), e.get("address_sym", "-"), r["kind"].split(" ")[0]))
    print("\nVerdict rule: call two dumps the **same** failure only if code, fault module AND the role of the faulting thread "
          "(finalizer / UI / worker) match; otherwise write **related** or **different** and say why.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dumps", nargs="+")
    ap.add_argument("--all-threads", action="store_true")
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--app", help="only list modules whose name contains this text")
    ap.add_argument("--max-frames", type=int, default=40)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    reports = []
    for path in a.dumps:
        try:
            reports.append(build(MiniDump(path), a.all_threads, a.max_frames))
        except (DumpError, OSError) as ex:
            print("!! %s: %s" % (path, ex), file=sys.stderr)
    if a.json:
        print(json.dumps(reports, indent=1, default=str))
    elif a.compare:
        compare(reports)
    else:
        for r in reports:
            print_md(r, a.app)
            print()
    sys.exit(0 if reports else 2)


if __name__ == "__main__":
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    main()
