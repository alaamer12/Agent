#!/usr/bin/env python3
"""win_symbolicate.py - name the frames in a Windows minidump via dbghelp.dll + a symbol server. WINDOWS ONLY.
No WinDbg/cdb/Visual Studio needed. Cleaned-up successor of the throwaway `syms.py` from the DemoApp investigation;
fixes the five bugs that cost that session ~6 runs (see references/symbolication.md):
  1. SymSetOptions precedence bug (`| 0x80000000 & 0`) + DEFERRED_LOADS  -> explicit, verified flags, no deferred loads
  2. symsrv.dll refuses the network without a sibling `symsrv.yes`        -> created automatically
  3. SYMBOL_INFOW.SizeOfStruct computed wrongly (must be 88)              -> constant 88
  4. the app's own exe frames were filtered out as 'noise'                -> nothing is filtered
  5. GetLastError printed after SUCCESSFUL loads (stale 487) misled       -> error shown only when the load returned 0

  python win_symbolicate.py crash.dmp [--threads all|0xTID] [--image-dir DIR] [--symbol-path P] [--loose]
  python win_symbolicate.py --selftest          # any OS: tests the frame-plausibility grading

Prerequisite: the dump was taken on THIS machine (or identical module copies exist), because dbghelp reads each image's
debug directory to find its PDB. Otherwise use WinDbg or fetch PDBs by GUID+age (printed by minidump_report.py).
NOTE: written from the transcript's final working script; only the grading self-test can run on non-Windows.
"""
import argparse
import ctypes
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import grade_frame  # noqa: E402

SYMOPT_UNDNAME = 0x00000002        # demangle C++ names
SYMOPT_LOAD_LINES = 0x00000010     # line info if private PDB
SYMOPT_EXACT_SYMBOLS = 0x00000400  # reject a PDB that does not match (a wrong PDB is WORSE than none)
SYMOPT_NO_PROMPTS = 0x00080000     # never pop UI
DEFAULT_SYMPATH = "srv*{cache}*https://msdl.microsoft.com/download/symbols"


def selftest():
    cases = {"KERNELBASE.dll!RaiseFailFastException+0x152": "ok",
             "Microsoft.UI.Xaml.dll!ctl::ComBase::ReleaseImpl+0x1b2b55": "suspect",
             "ntdll.dll!RtlLargeIntegerToChar+0xffffffffffffffff": "suspect",
             "Microsoft.UI.Xaml.dll!_tls_end+0x2d860": "suspect",
             "Microsoft.UI.Xaml.dll!`string'+0x0": "suspect",
             "MyApp.exe!FinalizerThread::FinalizeAllObjects+0x1a0": "ok",
             "Microsoft.UI.Xaml.dll+0x39cde5": "unsymbolicated"}
    bad = 0
    for text, want in cases.items():
        got, why = grade_frame(text)
        bad += got != want
        print("%s  %-14s %s%s" % ("PASS" if got == want else "FAIL", got, text, ("   <- " + why) if why else ""))
    sys.exit(1 if bad else 0)


class Symbolizer:
    def __init__(self, sympath, workdir, exact=True):
        from ctypes import wintypes
        dd = os.path.join(workdir, "dbg")
        os.makedirs(dd, exist_ok=True)
        cands = [r"C:\Program Files (x86)\Windows Kits\10\Debuggers\x64", r"C:\Program Files (x86)\Windows Kits\10\Debuggers\x86",
                 os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32")]
        vs = r"C:\Program Files\Microsoft Visual Studio"
        if os.path.isdir(vs):
            for root, _d, files in os.walk(vs):
                if "symsrv.dll" in (f.lower() for f in files) and "x64" in root and "Remote Debugger" in root:
                    cands.insert(0, root)
                    break
        find = lambda n: next((os.path.join(c, n) for c in cands if os.path.exists(os.path.join(c, n))), None)
        src_dbg, src_sym = find("dbghelp.dll"), find("symsrv.dll")
        if not src_dbg:
            raise SystemExit("dbghelp.dll not found")
        if not src_sym:
            print("!! symsrv.dll not found: no symbol-server downloads. Install Debugging Tools for Windows or use a local cache.", file=sys.stderr)
        for s in (src_dbg, src_sym):
            if s:
                shutil.copy(s, os.path.join(dd, os.path.basename(s)))
        open(os.path.join(dd, "symsrv.yes"), "w").close()                     # bug 2
        os.add_dll_directory(dd)
        self.dbg = ctypes.WinDLL(os.path.join(dd, "dbghelp.dll"), use_last_error=True)
        self.h = wintypes.HANDLE(0x1234)
        opts = SYMOPT_UNDNAME | SYMOPT_LOAD_LINES | SYMOPT_NO_PROMPTS | (SYMOPT_EXACT_SYMBOLS if exact else 0)   # bug 1
        self.dbg.SymSetOptions(opts)
        self.dbg.SymInitializeW.argtypes = [wintypes.HANDLE, wintypes.LPCWSTR, wintypes.BOOL]
        if not self.dbg.SymInitializeW(self.h, sympath, False):
            raise SystemExit("SymInitializeW failed: %d" % ctypes.get_last_error())
        self.dbg.SymLoadModuleExW.restype = ctypes.c_uint64
        self.dbg.SymLoadModuleExW.argtypes = [wintypes.HANDLE, wintypes.HANDLE, wintypes.LPCWSTR, wintypes.LPCWSTR,
                                              ctypes.c_uint64, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD]
        self.dbg.SymFromAddrW.argtypes = [wintypes.HANDLE, ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64), ctypes.c_void_p]
        self.loaded = set()

        class SYMBOL_INFOW(ctypes.Structure):
            _fields_ = [("SizeOfStruct", wintypes.ULONG), ("TypeIndex", wintypes.ULONG), ("Reserved", ctypes.c_uint64 * 2),
                        ("Index", wintypes.ULONG), ("Size", wintypes.ULONG), ("ModBase", ctypes.c_uint64), ("Flags", wintypes.ULONG),
                        ("Value", ctypes.c_uint64), ("Address", ctypes.c_uint64), ("Register", wintypes.ULONG), ("Scope", wintypes.ULONG),
                        ("Tag", wintypes.ULONG), ("NameLen", wintypes.ULONG), ("MaxNameLen", wintypes.ULONG), ("Name", wintypes.WCHAR * 1024)]
        self.SYM = SYMBOL_INFOW

    def load(self, m, image_dirs):
        path = m["path"] if os.path.exists(m["path"]) else next((os.path.join(d, m["name"]) for d in image_dirs if os.path.exists(os.path.join(d, m["name"]))), None)
        if not path:
            return "image not found on this machine"
        base = self.dbg.SymLoadModuleExW(self.h, None, path, None, m["base"], m["size"], None, 0)
        if base == 0 and ctypes.get_last_error() != 0:                        # bug 5
            return "SymLoadModuleExW failed, error %d" % ctypes.get_last_error()
        self.loaded.add(m["name"])
        return None

    def name(self, d, addr):
        m, off = d.module_for(addr)
        if m is None:
            return None
        if m["name"] not in self.loaded:
            return "%s+0x%x" % (m["name"], off)
        si = self.SYM()
        si.SizeOfStruct = 88                                                    # bug 3
        si.MaxNameLen = 1024
        disp = ctypes.c_uint64()
        if self.dbg.SymFromAddrW(self.h, addr, ctypes.byref(disp), ctypes.byref(si)):
            return "%s!%s+0x%x" % (m["name"], si.Name, disp.value)
        return "%s+0x%x" % (m["name"], off)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dump", nargs="?")
    ap.add_argument("--threads", default="fault", help="fault | all | 0xTID")
    ap.add_argument("--image-dir", action="append", default=[], help="extra folder holding the app's own modules")
    ap.add_argument("--symbol-path", default=os.environ.get("_NT_SYMBOL_PATH"))
    ap.add_argument("--loose", action="store_true", help="accept mismatched PDBs (NOT recommended)")
    ap.add_argument("--max-frames", type=int, default=60)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    if sys.platform != "win32":
        raise SystemExit("win_symbolicate.py needs Windows (dbghelp.dll). Use --selftest here, or gdb/lldb/ndk-stack/atos (references/platform-artifacts.md).")
    if not a.dump:
        ap.error("dump required")
    from mdparse import MiniDump
    d = MiniDump(a.dump)
    work = os.path.join(tempfile.gettempdir(), "fatal-symbolicate")
    os.makedirs(work, exist_ok=True)
    sympath = a.symbol_path or DEFAULT_SYMPATH.format(cache=os.path.join(work, "symcache"))
    s = Symbolizer(sympath, work, exact=not a.loose)
    dirs = [os.path.expandvars(x) for x in a.image_dir]
    print("symbol path: %s\n" % sympath)
    missing = {m["name"]: w for m in d.modules for w in [s.load(m, dirs)] if w}          # bug 4: load everything
    if missing:
        print("modules without symbols (frames show module+offset only):")
        for k, v in sorted(missing.items()):
            print("  - %s: %s" % (k, v))
        print()
    tids = [t["tid"] for t in d.threads] if a.threads == "all" else ([d.exception["tid"]] if a.threads == "fault" and d.exception else [] if a.threads == "fault" else [int(a.threads, 0)])
    for tid in tids:
        print("=== thread 0x%x%s ===  (heuristic scan)" % (tid, "  FAULTING" if d.exception and d.exception["tid"] == tid else ""))
        for f in d.scan_stack(tid)[: a.max_frames]:
            text = s.name(d, f["addr"])
            grade, why = grade_frame(text)
            print("  %s %s%s" % ({"ok": "   ", "suspect": "(?)", "unsymbolicated": " . "}[grade], text, ("      <- " + why) if why else ""))
        print()
    print("legend: '(?)' = implausible attribution; '.' = no symbol. Even 'ok' frames come from a SCAN, not an unwind: "
          "treat as hypothesis, then corroborate (references/evidence-and-reasoning.md).")


if __name__ == "__main__":
    main()
