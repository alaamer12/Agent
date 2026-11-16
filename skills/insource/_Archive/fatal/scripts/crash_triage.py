#!/usr/bin/env python3
"""crash_triage.py - STEP ZERO of a fatal-crash investigation: what tools and evidence exist on this machine?

  python crash_triage.py                          # last 72 h
  python crash_triage.py --app MyApp --hours 24 --search ~/proj/logs
  python crash_triage.py --json

Why: in the DemoApp session the agent installed dotnet-dump and burned 3 attempts before establishing what the target
runtime supported, and found evidence locations one at a time. This inventories debuggers/symbolizers and lists crash
artifacts for the current OS in one pass (newest first) with the next command per artifact. Read-only.
"""
import argparse
import datetime
import fnmatch
import json
import os
import platform
import shutil
import signal
import subprocess
import sys
import time

TOOLS = {"windows": ["cdb", "windbg", "dotnet-dump", "dotnet", "procdump", "python"],
         "linux": ["gdb", "lldb", "eu-stack", "addr2line", "llvm-symbolizer", "coredumpctl", "readelf", "debuginfod-find", "python3"],
         "darwin": ["lldb", "atos", "symbolicatecrash", "dwarfdump", "log", "python3"],
         "common": ["adb", "ndk-stack", "minidump_stackwalk", "dump_syms", "sentry-cli", "retrace", "node", "java"]}
WIN_TOOL_PATHS = [r"C:\Program Files (x86)\Windows Kits\10\Debuggers\x64\cdb.exe", r"C:\Program Files (x86)\Windows Kits\10\Debuggers\x64\windbg.exe"]
PATTERNS = ["*.dmp", "*.mdmp", "*.hdmp", "core", "core.*", "*.core", "*.crash", "*.ips", "*.diag", "hs_err_pid*.log", "tombstone_*",
            "report.*.json", "Report.wer", "crash*.log", "crash*.json", "watchdog*.log", "heartbeat*.log", "pending-crashes"]
NEXT = {".dmp": "python scripts/minidump_report.py {p}   (then win_symbolicate.py on Windows)", ".mdmp": "python scripts/minidump_report.py {p}",
        ".ips": "read exception type, termination reason, crashed thread; symbolicate with atos + dSYM", ".crash": "read exception type + crashed-thread backtrace; atos/symbolicatecrash + dSYM",
        "core": "gdb -batch -ex 'thread apply all bt' <exe> {p}   (or coredumpctl gdb)", "hs_err": "read header (signal, problematic frame), then Java/native frames",
        "tombstone": "ndk-stack -sym <dir with unstripped .so> < {p}", "Report.wer": "plain text (UTF-16): Sig[], Exception Code, LoadedModule[], IsFatal"}


def hint_for(name):
    for k, v in NEXT.items():
        if k.lower() in name.lower():
            return v
    return "open and read; if it is a log, feed it to scripts/build_timeline.py"


def find_tools():
    key = "windows" if sys.platform == "win32" else ("darwin" if sys.platform == "darwin" else "linux")
    found, missing = {}, []
    for t in TOOLS[key] + TOOLS["common"]:
        p = shutil.which(t)
        (found.__setitem__(t, p) if p else missing.append(t))
    if key == "windows":
        for p in WIN_TOOL_PATHS:
            if os.path.exists(p):
                found[os.path.basename(p)] = p
    try:
        import minidump  # noqa: F401
        found["py:minidump"] = "importable"
    except Exception:
        pass
    return key, found, missing


def candidate_dirs(plat, search, app):
    home = os.path.expanduser("~")
    dirs = list(search)
    if plat == "windows":
        la, pd = os.environ.get("LOCALAPPDATA", os.path.join(home, "AppData", "Local")), os.environ.get("ProgramData", r"C:\ProgramData")
        dirs += [os.path.join(la, "CrashDumps"), os.path.join(pd, "Microsoft", "Windows", "WER", "ReportArchive"), os.path.join(pd, "Microsoft", "Windows", "WER", "ReportQueue"),
                 os.path.join(la, "Microsoft", "Windows", "WER", "ReportArchive"), r"C:\Windows\Minidump"] + ([os.path.join(la, app)] if app else [])
    elif plat == "darwin":
        dirs += [os.path.join(home, "Library", "Logs", "DiagnosticReports"), "/Library/Logs/DiagnosticReports"] + ([os.path.join(home, "Library", "Application Support", app)] if app else [])
    else:
        dirs += ["/var/crash", "/var/lib/systemd/coredump", os.getcwd(), "/tmp"] + ([os.path.join(home, ".local", "share", app)] if app else [])
    return [d for d in dict.fromkeys(dirs) if d and os.path.isdir(d)]


def scan(dirs, hours, app, depth=4):
    cutoff, seen = time.time() - hours * 3600, {}
    for base in dirs:
        bd = base.rstrip(os.sep).count(os.sep)
        for root, subdirs, files in os.walk(base):
            if root.count(os.sep) - bd >= depth:
                subdirs[:] = []
            for n in files + subdirs:
                low = n.lower()
                if not any(fnmatch.fnmatch(low, p.lower()) for p in PATTERNS):
                    continue
                p = os.path.join(root, n)
                if app and app.lower() not in p.lower() and not low.endswith((".dmp", ".ips", ".crash")) and not low.startswith(("core", "hs_err", "tombstone")):
                    continue
                try:
                    st = os.stat(p)
                except OSError:
                    continue
                if st.st_mtime >= cutoff:
                    seen[os.path.realpath(p)] = dict(path=p, name=n, size=st.st_size if os.path.isfile(p) else 0, mtime=st.st_mtime)
    return sorted(seen.values(), key=lambda x: -x["mtime"])


def linux_extras():
    out = {}
    try:
        out["core_pattern"] = open("/proc/sys/kernel/core_pattern").read().strip()
        import resource
        soft, _h = resource.getrlimit(resource.RLIMIT_CORE)
        out["ulimit_core_soft"] = "unlimited" if soft == resource.RLIM_INFINITY else str(soft)
    except Exception:
        pass
    if shutil.which("coredumpctl"):
        try:
            r = subprocess.run(["coredumpctl", "list", "--no-pager", "-q", "--since", "-3days"], capture_output=True, text=True, timeout=10)
            out["coredumpctl"] = "\n".join(r.stdout.strip().splitlines()[-8:]) or "(none)"
        except Exception as ex:
            out["coredumpctl"] = "error: %s" % ex
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--app")
    ap.add_argument("--hours", type=float, default=72)
    ap.add_argument("--search", action="append", default=[])
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    plat, found, missing = find_tools()
    dirs = candidate_dirs(plat, a.search, a.app)
    arts = scan(dirs, a.hours, a.app)
    extras = linux_extras() if plat == "linux" else {}
    if a.json:
        print(json.dumps(dict(platform=plat, tools=found, missing=missing, dirs=dirs, artifacts=arts, extras=extras), indent=1))
        return
    print("# Crash triage - %s, %s, window %.0f h\n\n## Tools present" % (platform.platform(), datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), a.hours))
    for k, v in found.items():
        print("- %s  (%s)" % (k, v))
    print("\n## Tools absent\n- " + (", ".join(missing) or "none"))
    if plat == "windows" and not any(k in found for k in ("cdb", "cdb.exe", "windbg", "windbg.exe")):
        print("- No cdb/WinDbg: use scripts/minidump_report.py + scripts/win_symbolicate.py (pure Python + dbghelp).")
    if "dotnet-dump" in found or "dotnet" in found:
        print("- .NET note: dotnet-dump/SOS cannot read SINGLE-FILE/self-contained bundles without the matching DAC (mscordaccore). "
              "'Failed to request ThreadStore' => stop and pivot to native tools; do not loop.")
    print("\n## Directories scanned")
    for d in dirs:
        print("- " + d)
    if extras:
        print("\n## Linux dump settings")
        for k, v in extras.items():
            print("- %s: %s" % (k, v))
        if "|" not in extras.get("core_pattern", "") and extras.get("ulimit_core_soft") == "0":
            print("- core dumps are DISABLED for this shell (ulimit -c 0): a crash here leaves no core.")
    print("\n## Artifacts, newest first")
    if not arts:
        print("- none found. That is itself evidence: dumps may not be enabled (references/platform-artifacts.md), or the process was "
              "killed without a crash path (class E - external kill).")
    for x in arts[:40]:
        print("- %s  %8.1f KB  %s\n    next: %s" % (datetime.datetime.fromtimestamp(x["mtime"]).strftime("%Y-%m-%d %H:%M:%S"), x["size"] / 1024, x["path"], hint_for(x["name"]).format(p=x["path"])))
    print("\n## Always also check (not files)")
    if plat == "windows":
        print("- Get-WinEvent -FilterHashtable @{LogName='Application'; StartTime=(Get-Date).AddHours(-6)} | ? { $_.Id -in 1000,1001,1026 -or $_.Message -match '<app>' } | fl TimeCreated,Id,Message")
    elif plat == "darwin":
        print("- log show --last 6h --predicate 'process == \"<app>\"' --style compact")
    else:
        print("- journalctl --since '-6h' | grep -iE '<app>|segfault|Out of memory|Killed process|core dumped' ; dmesg -T | grep -iE 'segfault|oom|killed process'")
    print("- Android: adb logcat -b crash -d ; adb shell dumpsys activity exit-info <package>")
    print("- Your own logs: scripts/build_timeline.py -> LAST SIGN OF LIFE vs time of death.")


if __name__ == "__main__":
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    main()
