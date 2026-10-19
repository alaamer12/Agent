#!/usr/bin/env python3
"""Check that non-image media a decide page references exists and is the right kind of file.

Usage: python check_media.py page.html [--hosted] [--browser] [--timeout 15]

Covers audio (mp3 wav ogg opus flac m4a aac), video (mp4 m4v mov webm mkv ogv), documents (pdf),
3D models (glb gltf) and fonts (woff woff2 ttf otf). Images have their own script, check_images.py.
For any other medium, write a new checker (see references/media.md, "When no script exists").

References are found in src/href/data/poster attributes and in string literals inside the page's
script (full http(s) URLs with a media extension, and data: URIs). Keep full URLs as plain strings.

Each reference is OK, WARN (could not fully verify) or PROBLEM (verified bad):
  - must exist and be fetchable, must not be an HTML error page, must not be empty
  - file signature must match the extension
  - audio/video are also probed with ffprobe when installed (duration, readable streams)
--hosted   for hosted viewers that block remote and local media: every reference must be a data: URI
--browser  also load the page in headless Chromium and try each <audio>/<video>. Headless
           Chromium may lack H.264/AAC, so failures on mp4/m4a/aac/mov are only WARN.
Exit code 1 if any PROBLEM is found.
"""
import re, sys, os, base64, shutil, subprocess, tempfile, urllib.request, urllib.error, urllib.parse
from concurrent.futures import ThreadPoolExecutor

# Tunable limits. Adjust them for the environment or the page.
WARN_MB = 8            # larger items are flagged (hosted viewers may cap total page size)
MAX_FETCH = 40_000_000 # stop downloading a remote file after this many bytes

KINDS = {"audio": "mp3 wav ogg oga opus flac m4a aac", "video": "mp4 m4v mov webm mkv ogv",
         "document": "pdf", "3d": "glb gltf", "font": "woff woff2 ttf otf"}
EXT2KIND = {e: k for k, v in KINDS.items() for e in v.split()}
EXTRE = "|".join(sorted(EXT2KIND, key=len, reverse=True))
MIME2EXT = {"audio/mpeg": "mp3", "audio/wav": "wav", "audio/x-wav": "wav", "audio/ogg": "ogg", "audio/flac": "flac",
            "audio/mp4": "m4a", "audio/aac": "aac", "video/mp4": "mp4", "video/webm": "webm", "video/ogg": "ogv",
            "video/quicktime": "mov", "application/pdf": "pdf", "model/gltf-binary": "glb", "font/woff": "woff",
            "font/woff2": "woff2", "font/ttf": "ttf", "font/otf": "otf"}

def ext_of(url):
    if url.startswith("data:"):
        return MIME2EXT.get(url[5:].split(";")[0].split(",")[0].lower(), "")
    return os.path.splitext(urllib.parse.urlparse(url).path)[1][1:].lower()

def is_media(u):
    return ext_of(u) in EXT2KIND

def magic_ok(raw, ext):
    h = raw[:16]
    if ext == "mp3": return h[:3] == b"ID3" or (len(h) > 1 and h[0] == 0xFF and (h[1] & 0xE0) == 0xE0)
    if ext == "wav": return h[:4] == b"RIFF" and raw[8:12] == b"WAVE"
    if ext in ("ogg", "oga", "opus", "ogv"): return h[:4] == b"OggS"
    if ext == "flac": return h[:4] == b"fLaC"
    if ext in ("m4a", "mp4", "m4v", "mov"): return raw[4:8] in (b"ftyp", b"moov", b"mdat", b"wide", b"free")
    if ext == "aac": return h[:2] in (b"\xff\xf1", b"\xff\xf9") or h[:3] == b"ID3"
    if ext in ("webm", "mkv"): return h[:4] == b"\x1a\x45\xdf\xa3"
    if ext == "pdf": return raw[:1024].find(b"%PDF-") >= 0
    if ext == "glb": return h[:4] == b"glTF"
    if ext == "gltf": return b'"asset"' in raw[:4096]
    if ext == "woff": return h[:4] == b"wOFF"
    if ext == "woff2": return h[:4] == b"wOF2"
    if ext == "ttf": return h[:4] in (b"\x00\x01\x00\x00", b"true")
    if ext == "otf": return h[:4] == b"OTTO"
    return True

def verify(raw, ext, label):
    if not raw: return "PROBLEM", f"{label}: empty file"
    if raw[:300].lstrip().lower().startswith((b"<!doctype html", b"<html")):
        return "PROBLEM", f"{label}: returned an HTML page, not a .{ext} file"
    if not magic_ok(raw, ext): return "PROBLEM", f"{label}: content does not look like a .{ext} file"
    mb = len(raw) / 1048576; msg = f"{label}: .{ext}, {mb:.2f} MB"
    kind = EXT2KIND.get(ext)
    if kind in ("audio", "video"):
        if shutil.which("ffprobe"):
            with tempfile.NamedTemporaryFile(suffix="." + ext, delete=False) as f: f.write(raw); tmp = f.name
            r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", tmp], capture_output=True, text=True)
            os.unlink(tmp)
            try: dur = float(r.stdout.strip())
            except ValueError: return "PROBLEM", f"{msg}; ffprobe cannot read it ({r.stderr.strip()[:60]})"
            if dur <= 0: return "PROBLEM", f"{msg}; zero duration"
            msg += f", {dur:.1f}s"
        else:
            msg += ", header checked only (ffprobe not installed)"
    if mb > WARN_MB: return "WARN", msg + "; large (hosted viewers may cap total page size)"
    return "OK", msg

def check(ref, base, hosted, timeout):
    url, line = ref; ext = ext_of(url); short = url if len(url) < 70 else url[:67] + "..."
    if url.startswith("data:"):
        try: raw = base64.b64decode(url.split(",", 1)[1])
        except Exception: return "PROBLEM", f"line {line}: data URI cannot be decoded"
        s, m = verify(raw, ext, "data URI"); return s, f"line {line}: {m}"
    if hosted: return "PROBLEM", f"line {line}: {short} is not a data: URI. Hosted pages block remote and local media, so embed it or link out"
    p = urllib.parse.urlparse(url)
    if p.scheme in ("http", "https"):
        pre = f"line {line}: {short}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (decide media check)"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r: raw = r.read(MAX_FETCH + 1)
        except urllib.error.HTTPError as e:
            if e.headers.get("x-deny-reason"): return "WARN", f"{pre}: blocked by this environment's network policy ({e.headers.get('x-deny-reason')}); could not verify"
            return "PROBLEM", f"{pre}: HTTP {e.code}"
        except Exception as e:
            return "WARN", f"{pre}: could not connect ({str(e)[:70]}); bad host or network limit"
        s, m = verify(raw, ext, "file"); return s, f"{pre}: {m}"
    path = os.path.join(base, urllib.parse.unquote(url))
    if not os.path.isfile(path): return "PROBLEM", f"line {line}: {short} not found next to the page"
    s, m = verify(open(path, "rb").read(), ext, "file"); return s, f"line {line}: {short}: {m}"

def collect(html):
    refs, seen, page = [], set(), []
    def add(u, idx):
        u = u.strip()
        if u and u not in seen: seen.add(u); refs.append((u, html.count("\n", 0, idx) + 1))
    for m in re.finditer(r"\b(?:src|href|data|poster)\s*=\s*\"([^\"]+)\"", html, re.I):
        if is_media(m.group(1)): add(m.group(1), m.start())
    for m in re.finditer(r"[\"'`](https?://[^\"'`\s<>]+?\.(?:" + EXTRE + r")(?:\?[^\"'`\s<>]*)?)[\"'`]", html, re.I): add(m.group(1), m.start())
    for m in re.finditer(r"[\"'`](data:(?:audio|video|application/pdf|model|font)/[^;,\"'`]+;base64,[A-Za-z0-9+/=]+)[\"'`]", html, re.I):
        if is_media(m.group(1)): add(m.group(1), m.start())
    for m in re.finditer(r"<(video|audio)\b([^>]*)>", html, re.I):
        tag, a = m.group(1).lower(), m.group(2); ln = html.count("\n", 0, m.start()) + 1
        if "controls" not in a.lower(): page.append(("WARN", f"line {ln}: <{tag}> without controls"))
        if "autoplay" in a.lower() and "muted" not in a.lower(): page.append(("WARN", f"line {ln}: <{tag}> autoplays with sound; browsers block it and it annoys users"))
        if tag == "video" and "<track" not in html.lower(): page.append(("WARN", f"line {ln}: <video> has no <track> captions; add captions or a transcript if it has speech"))
    return refs, page

def browser_check(path):
    from playwright.sync_api import sync_playwright
    out = []
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page()
        pg.goto("file://" + os.path.abspath(path), wait_until="load")
        pg.evaluate("window.dispatchEvent(new Event('beforeprint'))")
        pg.evaluate("document.querySelectorAll('audio,video').forEach(m=>{m.preload='auto';m.load()})")
        pg.wait_for_timeout(3000)
        for r in pg.evaluate("[...document.querySelectorAll('audio,video')].map(m=>({s:(m.currentSrc||m.src||'').slice(0,80),ok:!m.error&&m.readyState>=1}))"):
            weak = ext_of(r["s"]) in ("mp4", "m4v", "m4a", "aac", "mov")
            out.append(("OK" if r["ok"] else ("WARN" if weak else "PROBLEM"), f"browser: {r['s']} " + ("loads" if r["ok"] else "did not load" + (" (headless Chromium may lack H.264/AAC)" if weak else ""))))
        b.close()
    return out

def main():
    if len(sys.argv) < 2: print(__doc__); sys.exit(2)
    path = sys.argv[1]; hosted = "--hosted" in sys.argv
    timeout = float(sys.argv[sys.argv.index("--timeout") + 1]) if "--timeout" in sys.argv else 15
    html = open(path, encoding="utf-8").read(); base = os.path.dirname(os.path.abspath(path))
    refs, results = collect(html)
    with ThreadPoolExecutor(6) as ex: results += list(ex.map(lambda r: check(r, base, hosted, timeout), refs))
    if "--browser" in sys.argv and re.search(r"<(audio|video)\b", html, re.I):
        try: results += browser_check(path)
        except Exception as e: results.append(("WARN", f"browser check skipped: {e}"))
    if not refs and not results: print("note: no media referenced"); sys.exit(0)
    for lvl in ("PROBLEM", "WARN", "OK"):
        for s, m in results:
            if s == lvl: print(f"{s:7} {m}")
    bad = sum(s == "PROBLEM" for s, _ in results); warn = sum(s == "WARN" for s, _ in results)
    print(f"\n{len(refs)} reference(s): {bad} problem(s), {warn} warning(s). Warnings mean the check could not confirm; open the page and play each item.")
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
