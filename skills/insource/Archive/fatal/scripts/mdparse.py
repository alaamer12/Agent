#!/usr/bin/env python3
"""mdparse - dependency-free reader for Windows user-mode minidumps (MDMP).

Why this exists: in the DemoApp investigation the third-party `minidump` package
returned ExceptionCode as an enum/str, which crashed the first analysis script
(`TypeError: 'str' object cannot be interpreted as an integer`). This reader returns
plain ints everywhere and tells you honestly what the dump does NOT contain.
Breakpad/Crashpad dumps use the same MDMP container on Linux/macOS/Android.

Import:  from mdparse import MiniDump
"""
import bisect
import datetime
import mmap
import struct

ARCH = {0: "x86", 5: "ARM", 9: "AMD64", 12: "ARM64", 6: "IA64"}
TYPE_BITS = {0x1: "WithDataSegs", 0x2: "WithFullMemory", 0x4: "WithHandleData", 0x20: "WithUnloadedModules",
             0x40: "WithIndirectlyReferencedMemory", 0x100: "WithProcessThreadData", 0x800: "WithFullMemoryInfo",
             0x1000: "WithThreadInfo", 0x8000: "WithTokenInformation"}


def _u(fmt, buf, off):
    return struct.unpack_from("<" + fmt, buf, off)


class DumpError(ValueError):
    pass


class MiniDump:
    def __init__(self, path):
        self.path = path
        self._f = open(path, "rb")
        try:
            self.buf = mmap.mmap(self._f.fileno(), 0, access=mmap.ACCESS_READ)
        except ValueError:
            raise DumpError("file is empty")
        self.size = len(self.buf)
        self._parse_header()
        self._parse_system()
        self._parse_modules()
        self._parse_memory()
        self._parse_threads()
        self._parse_exception()

    def _parse_header(self):
        if self.size < 32:
            raise DumpError("too small to be a minidump")
        sig = bytes(self.buf[:4])
        if sig != b"MDMP":
            if bytes(self.buf[:8]) in (b"PAGEDU64", b"PAGEDUMP"):
                raise DumpError("this is a Windows KERNEL/complete memory dump (PAGEDU64), not a user-mode minidump - use WinDbg/kd")
            if sig == b"\x7fELF":
                raise DumpError("this is an ELF core file - use gdb/lldb/eu-stack (see references/platform-artifacts.md)")
            raise DumpError("not an MDMP file (signature %r)" % sig)
        self.version, self.nstreams, self.dir_rva, self.checksum, self.timestamp, self.flags = _u("IIIIIQ", self.buf, 4)
        self.version &= 0xFFFF
        self.streams = {}
        for i in range(self.nstreams):
            t, sz, rva = _u("III", self.buf, self.dir_rva + 12 * i)
            self.streams.setdefault(t, []).append((sz, rva))

    @property
    def time_utc(self):
        try:
            return datetime.datetime.fromtimestamp(self.timestamp, datetime.timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None

    @property
    def flag_names(self):
        return [n for b, n in TYPE_BITS.items() if self.flags & b]

    def _stream(self, t):
        v = self.streams.get(t)
        return v[0] if v else None

    def _parse_system(self):
        self.arch = self.os = None
        self.ptr = 8
        s = self._stream(7)
        if not s:
            return
        arch, _l, _r, ncpu, _pt, major, minor, build = _u("HHHBBIII", self.buf, s[1])
        self.arch = ARCH.get(arch, "arch#%d" % arch)
        self.os = "%d.%d build %d" % (major, minor, build)
        self.ptr = 4 if arch in (0, 5) else 8

    def _wstr(self, rva):
        (n,) = _u("I", self.buf, rva)
        return bytes(self.buf[rva + 4: rva + 4 + n]).decode("utf-16-le", "replace")

    def _parse_modules(self):
        self.modules = []
        s = self._stream(4)
        if s:
            rva = s[1]
            (n,) = _u("I", self.buf, rva)
            for i in range(n):
                o = rva + 4 + 108 * i
                base, size, _cs, ts, name_rva = _u("QIIII", self.buf, o)
                sig, _sv, ms, ls = _u("IIII", self.buf, o + 24)
                ver = "%d.%d.%d.%d" % (ms >> 16, ms & 0xFFFF, ls >> 16, ls & 0xFFFF) if sig == 0xFEEF04BD else None
                cv_size, cv_rva = _u("II", self.buf, o + 76)
                guid = age = pdb = None
                if cv_size >= 24 and bytes(self.buf[cv_rva:cv_rva + 4]) == b"RSDS":
                    d1, d2, d3 = _u("IHH", self.buf, cv_rva + 4)
                    d4 = bytes(self.buf[cv_rva + 12: cv_rva + 20])
                    (age,) = _u("I", self.buf, cv_rva + 20)
                    guid = "%08X%04X%04X%s" % (d1, d2, d3, d4.hex().upper())
                    pdb = bytes(self.buf[cv_rva + 24: cv_rva + cv_size]).split(b"\0")[0].decode("utf-8", "replace")
                path = self._wstr(name_rva)
                self.modules.append(dict(base=base, size=size, timestamp=ts, version=ver, path=path, pdb=pdb, guid=guid, age=age,
                                         name=path.replace("/", "\\").split("\\")[-1]))
        self.modules.sort(key=lambda m: m["base"])
        self._mod_bases = [m["base"] for m in self.modules]

    def module_for(self, addr):
        i = bisect.bisect_right(self._mod_bases, addr) - 1
        if i >= 0:
            m = self.modules[i]
            if m["base"] <= addr < m["base"] + m["size"]:
                return m, addr - m["base"]
        return None, None

    def sym(self, addr):
        m, off = self.module_for(addr)
        return "%s+0x%x" % (m["name"], off) if m else None

    def _parse_memory(self):
        ranges = []
        s = self._stream(5)
        if s:
            (n,) = _u("I", self.buf, s[1])
            for i in range(n):
                start, dsz, drva = _u("QII", self.buf, s[1] + 4 + 16 * i)
                ranges.append((start, dsz, drva))
        s = self._stream(9)
        self.has_memory64 = bool(s)
        if s:
            n, base_rva = _u("QQ", self.buf, s[1])
            cur = base_rva
            for i in range(n):
                start, dsz = _u("QQ", self.buf, s[1] + 16 + 16 * i)
                ranges.append((start, dsz, cur))
                cur += dsz
        ranges.sort()
        self.mem = ranges
        self._mem_starts = [r[0] for r in ranges]
        self.captured_bytes = sum(r[1] for r in ranges)

    def read(self, addr, n):
        """Bytes of target memory, or None if not captured in this dump."""
        i = bisect.bisect_right(self._mem_starts, addr) - 1
        if i < 0:
            return None
        start, size, off = self.mem[i]
        if addr + n > start + size:
            return None
        return bytes(self.buf[off + (addr - start): off + (addr - start) + n])

    def _parse_threads(self):
        self.threads = []
        s = self._stream(3)
        if not s:
            return
        (n,) = _u("I", self.buf, s[1])
        for i in range(n):
            tid, susp, _pc, _pr, teb, sstart, ssz, srva, csz, crva = _u("IIIIQQIIII", self.buf, s[1] + 4 + 48 * i)
            sp, ip = self._ctx_sp_ip(crva, csz)
            self.threads.append(dict(tid=tid, suspend=susp, teb=teb, stack_start=sstart, stack_size=ssz,
                                     stack_rva=srva, ctx_size=csz, ctx_rva=crva, sp=sp, ip=ip))

    def _ctx_sp_ip(self, rva, size):
        try:
            if self.arch == "AMD64" and size >= 0x100:
                return _u("Q", self.buf, rva + 0x98)[0], _u("Q", self.buf, rva + 0xF8)[0]
            if self.arch == "ARM64" and size >= 0x110:
                return _u("Q", self.buf, rva + 0x100)[0], _u("Q", self.buf, rva + 0x108)[0]
        except struct.error:
            pass
        return None, None

    def thread(self, tid):
        return next((t for t in self.threads if t["tid"] == tid), None)

    def _parse_exception(self):
        self.exception = None
        s = self._stream(6)
        if not s:
            return
        rva = s[1]
        tid, _al = _u("II", self.buf, rva)
        code, flags, _nested, addr, nparams, _al2 = _u("IIQQII", self.buf, rva + 8)
        params = list(_u("15Q", self.buf, rva + 8 + 32))[: min(nparams, 15)]
        csz, crva = _u("II", self.buf, rva + 8 + 152)
        sp, ip = self._ctx_sp_ip(crva, csz)
        self.exception = dict(tid=tid, code=code, flags=flags, address=addr, params=params, sp=sp, ip=ip)

    def dump_kind(self):
        if self.has_memory64 or (self.flags & 0x2):
            return "full-memory (heap included)"
        return "mini-style (stacks + selected memory regions; heap usually NOT included)"

    def read_stowed(self):
        """Decode STOWED_EXCEPTION_INFORMATION (code 0xC000027B): list of dicts, or a str explaining why not."""
        e = self.exception
        if not e or e["code"] != 0xC000027B:
            return None
        if len(e["params"]) < 2:
            return "exception record has no parameters"
        arr, count = e["params"][0], e["params"][1]
        if not (0 < count <= 16):
            return "implausible stowed count %d" % count
        out = []
        for i in range(count):
            pp = self.read(arr + self.ptr * i, self.ptr)
            if pp is None:
                return ("stowed-exception array at 0x%x is not in this dump (mini dumps omit heap). "
                        "Re-capture with DumpType=2 - see scripts/enable_crash_dumps.ps1" % arr)
            p = int.from_bytes(pp, "little")
            hdr = self.read(p, 0x28)
            if hdr is None:
                return "stowed record at 0x%x is not in this dump (heap not captured)" % p
            _size, sig = struct.unpack_from("<I4s", hdr, 0)
            rc, bits = struct.unpack_from("<iI", hdr, 8)
            rec = dict(signature=sig.decode("ascii", "replace"), hresult=rc & 0xFFFFFFFF, form=bits & 3,
                       thread_id=bits >> 2, frames=[])
            if rec["form"] == 1:
                exaddr, wsz, words, stptr = struct.unpack_from("<QIIQ", hdr, 16)
                rec["exception_address"] = exaddr
                data = self.read(stptr, words * 8) if (stptr and wsz == 8 and 0 < words <= 256) else None
                if data:
                    rec["frames"] = [struct.unpack_from("<Q", data, 8 * j)[0] for j in range(words)]
            out.append(rec)
        return out

    def scan_stack(self, tid, max_words=20000):
        """HEURISTIC scan: every stack word pointing into a loaded module. NOT an unwound call stack -
        contains stale slots and data pointers; order is approximate."""
        t = self.thread(tid)
        if not t:
            return []
        data = self.read(t["stack_start"], t["stack_size"]) if t["stack_size"] else None
        if data is None:
            data = bytes(self.buf[t["stack_rva"]: t["stack_rva"] + t["stack_size"]])
        start_off, step = 0, self.ptr
        if t["sp"] and t["stack_start"] <= t["sp"] < t["stack_start"] + len(data):
            start_off = (t["sp"] - t["stack_start"]) & ~(step - 1)
        out, last = [], None
        for k in range(start_off, min(len(data) - step, start_off + max_words * step) + 1, step):
            a = int.from_bytes(data[k:k + step], "little")
            m, off = self.module_for(a)
            if m is None or (m["name"], off) == last:
                continue
            last = (m["name"], off)
            out.append(dict(stack_addr=t["stack_start"] + k, addr=a, module=m["name"], offset=off))
        return out
