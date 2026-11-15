#!/usr/bin/env python3
"""Build a tiny FAKE-but-structurally-valid x64 Windows minidump to test the skill's scripts without a real crash.
It mimics the shape of the DemoApp crash: a fail-fast (0xC000027B) raised on a *finalizer* thread while the UI
thread sits idle. All names/addresses are invented.   Usage: make_synthetic_minidump.py OUT.dmp [--mini]
--mini omits the heap region (stowed exception unreadable, like the real dump).
"""
import struct
import sys

out = sys.argv[1] if len(sys.argv) > 1 else "synthetic_failfast.dmp"
with_heap = "--mini" not in sys.argv
APP, NTDLL, KBASE, XAML = 0x7FF600000000, 0x7FFED9E90000, 0x7FFED7640000, 0x7FFE4C850000
mods = [(APP, 0x300000, 0x6A3ED1EB, r"C:\demo\Demo.exe", (1, 0, 4, 0), None),
        (XAML, 0xE00000, 0x810B4CF6, r"C:\demo\bundle\Microsoft.UI.Xaml.dll", (3, 1, 7, 0), ("Microsoft.ui.xaml.pdb", 1)),
        (KBASE, 0x350000, 0x5E000000, r"C:\Windows\System32\KERNELBASE.dll", (10, 0, 19041, 1), None),
        (NTDLL, 0x1F0000, 0x5E000001, r"C:\Windows\System32\ntdll.dll", (10, 0, 19041, 1), None)]
UI_TID, FIN_TID = 0x4700, 0x38FC
UI_STACK, FIN_STACK, HEAP = 0xA0F0000000, 0xA0F1000000, 0x2DB48814000
buf = bytearray()


def alloc(data, align=8):
    while len(buf) % align:
        buf.append(0)
    rva = len(buf)
    buf.extend(data)
    return rva


def wstr(s):
    b = s.encode("utf-16-le")
    return struct.pack("<I", len(b)) + b + b"\0\0"


nstreams = 5
buf.extend(b"\0" * (32 + 12 * nstreams))
sysinfo = struct.pack("<HHHBBIIII", 9, 6, 0, 8, 1, 10, 0, 19045, 2) + b"\0" * 32
sys_rva = alloc(sysinfo)
mblob = struct.pack("<I", len(mods))
for base, size, ts, path, ver, pdb in mods:
    name_rva = alloc(wstr(path), 4)
    cv_size = cv_rva = 0
    if pdb:
        cv = b"RSDS" + struct.pack("<IHH", 0x11223344, 0x5566, 0x7788) + bytes.fromhex("99AABBCCDDEEFF00") + struct.pack("<I", pdb[1]) + pdb[0].encode() + b"\0"
        cv_rva, cv_size = alloc(cv, 4), len(cv)
    fv = struct.pack("<IIII", 0xFEEF04BD, 0x10000, (ver[0] << 16) | ver[1], (ver[2] << 16) | ver[3]) + b"\0" * 36
    mblob += struct.pack("<QIIII", base, size, 0, ts, name_rva) + fv + struct.pack("<II", cv_size, cv_rva) + b"\0" * 24
assert len(mblob) == 4 + 108 * len(mods)
mod_rva = alloc(mblob)


def stack_bytes(words, size):
    b = b"".join(struct.pack("<Q", w) for w in words)
    return b + b"\0" * (size - len(b))


fin_words = [1, 0xDEADBEEF, XAML + 0x39CDE5, KBASE + 0x12C012, 0x123456789, APP + 0x1A2B3C, XAML + 0x39D309,
             NTDLL + 0x1C3C8, XAML + 0x39CDE5, APP + 0x1A2B80, APP + 0x1A2B80, KBASE + 0x6098D]
ui_words = [0, 0, NTDLL + 0x4CC91, KBASE + 0x1234, APP + 0x5000, XAML + 0xB23688]
SZ = 0x1000
fin_rva, ui_rva = alloc(stack_bytes(fin_words, SZ)), alloc(stack_bytes(ui_words, SZ))


def ctx(rsp, rip):
    c = bytearray(0x4D0)
    struct.pack_into("<I", c, 0x30, 0x10000B)
    struct.pack_into("<Q", c, 0x98, rsp)
    struct.pack_into("<Q", c, 0xF8, rip)
    return bytes(c)


fin_ctx, ui_ctx = alloc(ctx(FIN_STACK, XAML + 0x39CDE5)), alloc(ctx(UI_STACK, NTDLL + 0x4CC91))
tblob = struct.pack("<I", 2)
for tid, st, srva, crva in ((UI_TID, UI_STACK, ui_rva, ui_ctx), (FIN_TID, FIN_STACK, fin_rva, fin_ctx)):
    tblob += struct.pack("<IIIIQQIIII", tid, 0, 0, 0, 0, st, SZ, srva, 0x4D0, crva)
thr_rva = alloc(tblob)
excp = struct.pack("<II", FIN_TID, 0) + struct.pack("<IIQQII", 0xC000027B, 1, 0, XAML + 0x39CDE5, 2, 0) + \
    struct.pack("<15Q", HEAP + 0xC80, 1, *([0] * 13)) + struct.pack("<II", 0x4D0, fin_ctx)
exc_rva = alloc(excp)
ranges = [(UI_STACK, SZ, ui_rva), (FIN_STACK, SZ, fin_rva)]
if with_heap:
    heap = bytearray(0x1000)
    struct.pack_into("<Q", heap, 0xC80, HEAP + 0xD00)
    hdr = struct.pack("<I4siI", 0x30, b"SE02", 0x8000000E - (1 << 32), 1 | (FIN_TID << 2)) + struct.pack("<QIIQ", XAML + 0x39CDE5, 8, 3, HEAP + 0xE00)
    heap[0xD00:0xD00 + len(hdr)] = hdr
    struct.pack_into("<3Q", heap, 0xE00, XAML + 0x1000, APP + 0x2000, KBASE + 0x3000)
    ranges.append((HEAP, 0x1000, alloc(bytes(heap))))
mem = struct.pack("<I", len(ranges)) + b"".join(struct.pack("<QII", a, s, r) for a, s, r in ranges)
mem_rva = alloc(mem)
dirents = [(7, len(sysinfo), sys_rva), (4, len(mblob), mod_rva), (3, len(tblob), thr_rva), (6, len(excp), exc_rva), (5, len(mem), mem_rva)]
buf[0:32] = struct.pack("<4sIIIIIQ", b"MDMP", 0xA793, nstreams, 32, 0, 1792496000, 0)
for i, (t, sz, rva) in enumerate(dirents):
    struct.pack_into("<III", buf, 32 + 12 * i, t, sz, rva)
open(out, "wb").write(buf)
print("wrote", out, len(buf), "bytes", "(with heap)" if with_heap else "(mini: no heap)")
