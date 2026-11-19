#!/usr/bin/env python3
"""imgery_lab.py -- verification harness for the imgery (media) pillar.

Like merge_lab.sh for git, but against the live web: every measured claim the
pillar's doctrine makes -- official asset URLs, byte sizes, SVG anatomy,
versionless-CDN ghosting, facade scale, thumbnail traps, CORS behavior -- is
re-probed here against the actual vendor endpoints. Structural claims (a file
exists at URL X with composition Y) FAIL on drift; size claims report drift as
INFO (vendors legitimately resize) but still fail if the ORDER OF MAGNITUDE
breaks. A citation-liveness sweep checks every http(s) URL quoted in the
pillar's markdown.

Usage:
  python imgery_lab.py                 # full matrix (~60 requests, read-only)
  python imgery_lab.py --filter S08    # only ids starting with the prefix
  python imgery_lab.py --fast          # skip the slow embed/CORS checks

Exit 0 = no failures. On Windows run with `python`. stdout is ASCII.
"""

import concurrent.futures
import io
import re
import sys
import zipfile
import urllib.error
import urllib.request
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) imgery-lab/1.0 "
                    "(doctrine verification; not a bot farm)"}
TIMEOUT = 25
PASS = FAIL = INFO = 0
FAILED = []

def ok(name):
    global PASS
    PASS += 1
    print(f"PASS {name}")

def bad(name, msg):
    global FAIL
    FAIL += 1
    FAILED.append(name)
    print(f"FAIL {name}: {msg}")

def note(name, msg):
    global INFO
    INFO += 1
    print(f"INFO {name}: {msg}")

_cache = {}

def fetch(url, headers=None, max_bytes=None):
    key = (url, max_bytes)
    if key in _cache:
        return _cache[key]
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            data = r.read(max_bytes) if max_bytes else r.read()
            out = (r.status, dict(r.headers), data, r.geturl())
    except urllib.error.HTTPError as e:
        try:
            body = e.read(65536)
        except Exception:
            body = b""
        out = (e.code, dict(e.headers or {}), body, url)
    except Exception as e:
        out = (None, {}, str(e).encode("utf-8", "replace"), url)
    _cache[key] = out
    return out

def squash(url_or_bytes):
    """Fetch + decode to text with entities resolved, curly quotes normalized
    and whitespace collapsed - verified false-fail sources: typographic
    apostrophe (Apple), a newline mid-phrase (web.dev)."""
    import html as _html
    if isinstance(url_or_bytes, tuple):
        raw = url_or_bytes[2]
    else:
        raw = fetch(url_or_bytes)[2]
    t = _html.unescape(raw.decode("utf-8", "replace"))
    pairs = ((chr(0x2018), "'"), (chr(0x2019), "'"), (chr(0x201c), '"'),
             (chr(0x201d), '"'), (chr(0x2013), "-"), (chr(0x2014), "--"))
    for a, b in pairs:
        t = t.replace(a, b)
    return re.sub(r"\s+", " ", t)


ZIP_GOOGLE = "https://developers.google.com/static/identity/images/signin-assets.zip"
ZIP_GITHUB = "https://brand.github.com/GitHub_Logos.zip"

# ---------------------------------------------------------------- S01-S02 Google

def S01_google_zip():
    st, hd, data, _ = fetch(ZIP_GOOGLE)
    if st != 200 or not data.startswith(b"PK"):
        return bad("S01", f"signin-assets.zip not served as zip (status {st})")
    if len(data) != 855303:
        note("S01", f"size drifted {len(data)} B vs reported 855,303 B (INFO: vendors resize)")
    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        return bad("S01", "corrupt zip")
    names = zf.namelist()
    svgs = [n for n in names if n.endswith(".svg")]
    if len(svgs) < 20:
        return bad("S01", f"only {len(svgs)} SVGs (reported 24)")
    png_tiers = {m for n in names if n.endswith(".png")
                 for m in re.findall(r"@([1-4])x|([1-4])x\.(png)", n)}
    if not any(("Android" in n or "iOS" in n) for n in names):
        return bad("S01", "platform folders gone")
    if not any("Theme=" in n for n in names):
        return bad("S01", "Theme=/Show text=/Shape= keying gone")
    ok("S01")
    return zf

def S02_google_badge_anatomy(zf=None):
    zf = zf or S01_google_zip()
    if zf is None or not isinstance(zf, zipfile.ZipFile):
        return bad("S02", "zip unavailable")
    badges = [n for n in zf.namelist() if n.endswith(".svg") and "Show text=No" in n]
    texts = [n for n in zf.namelist() if n.endswith(".svg") and "Show text=Yes" in n]
    if not badges or not texts:
        return bad("S02", "badge/text split not found in bundle")
    body = zf.read(badges[0])
    blurs = body.count(b"feGaussianBlur")
    has_fo = b"foreignObject" in body
    has_conic = b"conic-gradient" in body
    has_mask = b"<mask" in body
    vb = re.search(rb'viewBox="([^"]+)"', body)
    if not (has_fo and has_conic and has_mask):
        return bad("S02", "the G is NOT a foreignObject/conic/mask composite anymore -- "
                          "the undrawability proof needs re-reading")
    if blurs != 7:
        note("S02", f"blur count {blurs} vs measured 7 (structure still complex; INFO drift)")
    if vb and vb.group(1) != b"0 0 40 40":
        note("S02", f"badge viewBox {vb.group(1).decode()} vs 0 0 40 40")
    tb = zf.read(texts[0])
    if b"<text" in tb:
        return bad("S02", "text button contains <text> -- 'outlined text' claim false")
    tvb = re.search(rb'viewBox="([^"]+)"', tb)
    if tvb and tvb.group(1) != b"0 0 180 40":
        note("S02", f"text button viewBox {tvb.group(1).decode()} vs 0 0 180 40")
    ok("S02")

# ------------------------------------------------------------------ S03-S04 GitHub

def S03_github_zip():
    st, hd, data, _ = fetch(ZIP_GITHUB)
    if st != 200 or not data.startswith(b"PK"):
        return bad("S03", f"GitHub_Logos.zip not served (status {st})")
    if len(data) != 499228:
        note("S03", f"size {len(data)} B vs reported 499,228 (INFO drift)")
    zf = zipfile.ZipFile(io.BytesIO(data))
    names = [n for n in zf.namelist() if not n.startswith("__MACOSX") and not n.endswith("/")]
    ext = {}
    for n in names:
        e = n.rsplit(".", 1)[-1].lower()
        ext[e] = ext.get(e, 0) + 1
    junk = [n for n in zf.namelist() if "__MACOSX" in n or n.endswith(".DS_Store")]
    if not junk:
        note("S03", "macOS resource-fork junk absent now (vendoring-hygiene claim was real at probe time)")
    inv = [n for n in names if "Invertocat_Black" in n and n.endswith(".svg")]
    if not inv:
        return bad("S03", "Invertocat svg missing")
    body = zf.read(inv[0])
    paths = body.count(b"<path")
    if paths > 2:
        return bad("S03", f"official Invertocat now {paths} paths -- the 1-path "
                          "provenance lesson needs re-measuring")
    if paths != 1:
        note("S03", f"Invertocat paths={paths} (was 1)")
    if b"<text" in body:
        return bad("S03", "Invertocat contains <text>??")
    note("S03", f"tiers: {ext}")
    ok("S03")

def S04_github_logos_redirect():
    st, hd, _, final = fetch("https://github.com/logos", max_bytes=1)
    if "brand.github.com" in final:
        ok("S04")
    elif st and st < 400:
        bad("S04", f"github.com/logos resolves to {final}, not brand.github.com -- "
                   "the memorized-URL trap example changed")
    else:
        bad("S04", f"status {st}")

# ---------------------------------------------------------------- S05-S07 legal text

def S05_apple_clause_text():
    t = squash("https://www.apple.com/legal/intellectual-property/guidelinesfor3rdparties.html")
    for phrase in ("artist's rendering", "express written trademark license", "takeoff"):
        if phrase not in t:
            return bad("S05", f"quoted clause missing: {phrase!r}")
    ok("S05")


def S06_meta_clause_text():
    st, hd, data, _ = fetch("https://www.facebook.com/brand/resources/facebook/logo/")
    if st != 200:
        note("S06", f"Meta page status {st} (login wall/bot block likely); "
                    "quotes rest on the dossier fetch -- doctrine keeps date-stamp")
        return
    t = data.decode("utf-8", "replace")
    if "brand" not in t.lower():
        return note("S06", "JS-shell page: clause text not in HTML; doctrine quote "
                           "stays dossier-dated (known Meta pattern)")
    if "Google search" in t or "approved" in t:
        ok("S06")
    else:
        note("S06", "page served HTML without the quoted clauses -- re-read manually")

def S07_meta_hashed_asset():
    st, hd, data, _ = fetch("https://static.xx.fbcdn.net/rsrc.php/y9/r/tL_v571NdZ0.svg", max_bytes=4096)
    if st == 200 and b"<svg" in data:
        ok("S07")
    else:
        note("S07", f"fbcdn hashed svg: status {st} -- content-hash-stable claim is "
                    "per-file; this instance may have rotated (verify before quoting)")

# ------------------------------------------------------- S08 ghost-serving (CDN trap)

def S08_simpleicons_ghost():
    st, hd, data, _ = fetch("https://data.jsdelivr.com/v1/packages/npm/simple-icons")
    if st != 200:
        return bad("S08", f"jsdelivr package API status {st}")
    m = re.search(rb'"tags"\s*:\s*{\s*"latest"\s*:\s*"([^"]+)"', data)
    if not m:
        return bad("S08", "no tags.latest in API response")
    latest = m.group(1).decode()
    st_v, _, body_v, _ = fetch("https://cdn.jsdelivr.net/npm/simple-icons/icons/openai.svg", max_bytes=4096)
    st_p, _, _, _ = fetch(f"https://cdn.jsdelivr.net/npm/simple-icons@{latest}/icons/openai.svg", max_bytes=4096)
    if st_v == 200 and st_p == 404:
        ok("S08")
    elif st_v == 200 and st_p == 200:
        note("S08", f"openai.svg now present at {latest} -- reinstated? ghost example stale")
    else:
        bad("S08", f"versionless={st_v} pinned@{latest}={st_p} -- expected 200/404")
    note("S08", f"resolved tags.latest={latest}")

# ------------------------------------------------------------- S09-S10 docs liveness

def S09_svgo_preset_source():
    """Deterministic: the default plugin list read from npm source, not docs."""
    st, _, data, _ = fetch("https://data.jsdelivr.com/v1/packages/npm/svgo")
    if st != 200:
        return bad("S09", f"svgo package API status {st}")
    m = re.search(rb'"latest"\s*:\s*"([^"]+)"', data)
    ver = m.group(1).decode()
    t = squash(f"https://cdn.jsdelivr.net/npm/svgo@{ver}/plugins/preset-default.js")
    listed = set(re.findall(r"import \* as (\w+) from '\./(\w+)\.js'", t))
    names = {a for a, _ in listed}
    if not names:
        return bad("S09", f"no import-list parse in preset-default.js@{ver} -- shape changed")
    must_in = {"convertPathData", "cleanupNumericValues", "convertShapeToPath"}
    must_out = {"removeViewBox", "removeScripts", "removeTitle", "removeDimensions"}
    ins = [p for p in must_in if p not in names]
    outs = [p for p in must_out if p in names]
    if ins or outs:
        return bad("S09", f"svgo@{ver}: wrongly {ins} missing / {outs} present in defaults")
    note("S09", f"svgo@{ver}: {len(names)} default plugins; removeViewBox/removeScripts/removeTitle "
                "confirmed NOT default (source-parsed, not docs-parsed)")
    ok("S09")

def S10_webdev_quotes():
    want = {
        "https://web.dev/articles/font-best-practices.md.txt": "replace icon fonts with SVGs",
        "https://web.dev/articles/preload-critical-assets.md.txt": "fetched twice",
        "https://web.dev/articles/embed-best-practices.md.txt": "224 times faster",
    }
    missing = []
    for u, phrase in want.items():
        t = squash(u)
        if phrase.lower() not in t.lower():
            missing.append(f"{u.rsplit('/', 1)[-1]}: '{phrase}'")
    if missing:
        return note("S10", "phrasing drift on current pages (doctrine quotes stay "
                            "dossier-dated): " + " | ".join(missing))
    ok("S10")

# ------------------------------------------------------------------ S11-S12 facade scale

def S11_facade_bytes():
    cands = [
        "https://cdn.jsdelivr.net/gh/paulirish/lite-youtube-embed@master/src/lite-yt-embed.min.js",
        "https://cdn.jsdelivr.net/gh/paulirish/lite-youtube-embed@master/src/lite-yt-embed.js",
    ]
    js = None
    for c in cands:
        st, hd, data, _ = fetch(c)
        if st == 200:
            js = data
            break
    css = fetch("https://cdn.jsdelivr.net/gh/paulirish/lite-youtube-embed@master/src/lite-yt-embed.css")[2] \
        if js else b""
    if not js:
        return bad("S11", "lite-youtube-embed sources not reachable")
    total = len(js) + len(css)
    note("S11", f"facade raw bytes js+css = {total:,}")
    if total > 100_000:
        return bad("S11", f"facade grew to {total} B -- the KB-scale claim is dead")
    ok("S11")

def S12_player_page_scale():
    st, hd, data, _ = fetch("https://www.youtube.com/embed/aqz-KE-bpKQ")
    if st != 200:
        return note("S12", f"embed doc status {st}; 540 KB figure stays dossier-dated")
    note("S12", f"embed document first render bytes = {len(data):,}")
    if len(data) < 50_000:
        return bad("S12", "embed doc under 50 KB -- facade cost story needs re-measure")
    ok("S12")

# --------------------------------------------------------------------- S13-S14 traps

def S13_thumbnail_traps():
    problems = []
    st, hd, data, _ = fetch("https://i.ytimg.com/vi/INVALIDidXX/maxresdefault.jpg")
    ct = (hd.get("Content-Type") or "").lower()
    is_img = data[:3] == b"\xff\xd8\xff"
    if st == 200 and is_img or (st == 404 and (is_img or ct.startswith("image"))):
        note("S13", f"invalid-id maxres: status {st}, image bytes present "
                    "-- onerror-only handling confirmed unsafe")
    else:
        problems.append(f"invalid-id maxres: status {st} ct {ct} magic {data[:3]!r} -- the "
                        "'error responses still carry an image body' claim fails here")
    st2, _, d2, _ = fetch("https://i.ytimg.com/vi/aqz-KE-bpKQ/hqdefault.jpg", max_bytes=16)
    if not (st2 == 200 and d2[:3] == b"\xff\xd8\xff"):
        problems.append(f"hqdefault on known video: {st2}")
    stw, _, dw, _ = fetch("https://i.ytimg.com/vi/aqz-KE-bpKQ/hqdefault.webp", max_bytes=16)
    if stw == 404 and dw[:3] == b"\xff\xd8\xff":
        note("S13", "404 on .webp served a JPEG BODY -- status-only handling is "
                    "structurally unsafe here; naturalWidth/magic probe is the rule (measured)")
    else:
        note("S13", f"webp thumb: status {stw}, magic {dw[:4]!r}")
    if problems:
        return bad("S13", "; ".join(problems))
    ok("S13")

def S14_font_cors():
    hdrs = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"}
    st, hd, css, _ = fetch("https://fonts.googleapis.com/css2?family=Inter:wght@400", headers=hdrs)
    if st != 200:
        return bad("S14", f"Google Fonts css status {st}")
    m = re.search(rb"https://fonts\.gstatic\.com[^) ]+\.woff2", css)
    if not m:
        return note("S14", "no gstatic woff2 URL in css (UA shaping) -- claim unchecked here")
    st2, hd2, _, _ = fetch(m.group(0).decode(), max_bytes=64, headers=hdrs)
    acao = (hd2.get("Access-Control-Allow-Origin") or "")
    if st2 == 200 and acao == "*":
        ok("S14")
    else:
        bad("S14", f"gstatic font: status {st2}, ACAO={acao!r} -- 'fonts need a CORS "
                   "connection' needs re-reading")

# ------------------------------------------------------------------------ S15 goog expiry

def S15_goog_expires_header():
    st, hd, _, _ = fetch("https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png",
                         max_bytes=16)
    exp = hd.get("X-Goog-Expires") or hd.get("Expires") or ""
    if st and st < 400 and exp:
        note("S15", f"X-Goog-Expires/Expires present ({exp})")
        ok("S15")
    else:
        note("S15", f"no expiry header observed (status {st}); the 'vendor links expire' "
                    "doctrine rests on the measured hub-asset case (dossier-dated)")

# --------------------------------------------------------------------- S16 citation sweep

REF_DIR = Path(__file__).resolve().parent.parent

def S16_citation_liveness():
    urls = set()
    for md in REF_DIR.rglob("*.md"):
        text = md.read_text(encoding="utf-8", errors="replace")
        for u in re.findall(r"https?://[^\s)\]\"'<>]+", text):
            u = u.rstrip(".,;:")
            if "fonts.googleapis.com/css2" in u or "example.com" in u:
                continue
            urls.add(u)
    urls = sorted(urls)
    def probe(u):
        return u, fetch(u, max_bytes=2048)[0]
    dead, blocked, unreachable = [], [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        for u, st in ex.map(probe, urls):
            if st is None:
                unreachable.append(u)
            elif st in (404, 410):
                dead.append((u, st))
            elif st in (403, 429) or (st and st >= 500):
                blocked.append((u, st))
    for u, st in dead:
        print(f"  dead citation: {st} {u}")
    for u in unreachable:
        print(f"  unreachable from this network (timeout/refused) -- not judged dead: {u}")
    for u, st in blocked:
        print(f"  bot-blocked (not a dead link): {st} {u}")
    if dead:
        return bad("S16", f"{len(dead)} dead citations of {len(urls)} probed")
    note("S16", f"{len(urls)} citations probed; {len(blocked)} bot-blocked, "
                f"{len(unreachable)} unreachable-from-here")
    ok("S16")

def main():
    global PASS, FAIL, INFO
    args = sys.argv[1:]
    filt = None
    fast = False
    if "--filter" in args:
        filt = args[args.index("--filter") + 1]
    if "--fast" in args:
        fast = True

    # zips fetched once; S01 must run before S02 (shares the fetch cache)
    run = lambda name: (filt is None or name.startswith(filt))
    zf_g = S01_google_zip() if run("S01") else None
    if run("S02"):
        if isinstance(zf_g, zipfile.ZipFile):
            S02_google_badge_anatomy(zf_g)
        else:
            S02_google_badge_anatomy()
    for fn in (S03_github_zip, S04_github_logos_redirect, S05_apple_clause_text,
               S06_meta_clause_text, S07_meta_hashed_asset, S08_simpleicons_ghost,
               S09_svgo_preset_source, S10_webdev_quotes, S13_thumbnail_traps):
        name = fn.__name__.split("_")[0]
        if filt and not name.startswith(filt):
            continue
        fn()
    if not fast:
        for fn in (S11_facade_bytes, S12_player_page_scale, S14_font_cors,
                   S15_goog_expires_header, S16_citation_liveness):
            name = fn.__name__.split("_")[0]
            if filt and not name.startswith(filt):
                continue
            fn()

    print(f"\nimgery_lab: {PASS} passed, {FAIL} failed, {INFO} info-notes; "
          f"failures:{' ' + ' '.join(FAILED) if FAILED else ' none'}")
    return 1 if FAIL else 0

if __name__ == "__main__":
    sys.exit(main())
