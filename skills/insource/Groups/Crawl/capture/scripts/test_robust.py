"""Offline robustness tests: fuzzing, pathological inputs, input validation, safety limits.

  python test_robust.py        # exit 0 = all passed

Everything here must finish quickly and never raise or hang, whatever the input.
"""
from __future__ import annotations

import http.server
import os
import random
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _common  # noqa: E402
import _cssparse as css  # noqa: E402
import _htmlpatterns as hp  # noqa: E402
import _tokens  # noqa: E402
import screenshots  # noqa: E402
import website  # noqa: E402

BASE_CSS = """
:root{--bg:#fff;--fg:#111;--accent:rgba(10,20,30,.5);--space-1:4px;--space-2:8px;--space-3:16px;--font:"Inter",system-ui,sans-serif}
@font-face{font-family:"Inter";src:url(inter[wght].woff2) format("woff2");font-weight:100 900}
@media (prefers-color-scheme:dark){:root{--bg:#000;--fg:#eee}}
@media (min-width:768px){.card{display:grid;grid-template-columns:repeat(3,1fr);gap:var(--space-2)}}
@container (min-width:300px){.tile{padding:var(--space-3)}}
@supports (display:grid){.a{display:grid}}
.btn{padding:var(--space-1) var(--space-2);border-radius:8px;background:linear-gradient(#fff,#eee);box-shadow:0 1px 3px rgba(0,0,0,.2);transition:all .2s cubic-bezier(.4,0,.2,1)}
.btn:hover,.btn:focus-visible{color:var(--accent)}.card>.title::after{content:"\\201C";color:tomato}
.md\\:flex{display:flex}.w-\\[calc\\(100\\%-1rem\\)\\]{width:calc(100% - 1rem)}
@keyframes spin{from{transform:rotate(0)}to{transform:rotate(360deg)}}
.nest{color:red;&:hover{color:blue}.child{margin:0 auto}}
@layer base,components;@import url("other.css") layer(base);
"""
BASE_HTML = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>t</title><style>.x{color:red}</style></head><body>'
             '<header class="site-header"><nav><ul><li><a href="/a">A</a></li><li><a href="/b">B</a></li></ul></nav></header>'
             '<main><section class="hero"><h1>Hi</h1><p>text &amp; more</p><button class="btn">Go</button></section>'
             '<ul class="cards"><li class="card"><h3>1</h3></li><li class="card"><h3>2</h3></li><li class="card"><h3>3</h3></li></ul>'
             '<svg viewBox="0 0 10 10"><path d="M0 0"/></svg><my-el data-x="1"></my-el></main><footer>f</footer></body></html>')
CSS_JUNK = ["{", "}", "(", ")", '"', "'", "/*", "*/", "\\", ";", "@media", "@import", "@", "@{", "url(", "--", "[", "]", "\x00", "\n", "var(", ":", "var(--bg)", ","]
HTML_JUNK = ["<", ">", "</div>", "<div>", "<!--", "-->", '"', "<script>", "</script>", "&", "<svg>", "\x00", "<table>", "<li>", "<style>"]


class Timeout(Exception):
    pass


def _alarm(seconds):
    if hasattr(signal, "SIGALRM"):
        signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(Timeout()))
        signal.alarm(seconds)


def _mutate(text, junk, rnd):
    s = list(text)
    for _ in range(rnd.randint(1, 30)):
        pos = rnd.randrange(len(s))
        op = rnd.random()
        if op < 0.4:
            del s[pos:pos + rnd.randint(1, 60)]
        elif op < 0.8:
            s.insert(pos, rnd.choice(junk))
        else:
            s[pos:pos] = list(rnd.choice(junk) * rnd.randint(2, 8))
    return "".join(s)


def cli(*args, timeout=60):
    t0 = time.time()
    r = subprocess.run([sys.executable, os.path.join(HERE, "capture.py"), *args], capture_output=True, text=True, timeout=timeout)
    return r.returncode, (r.stderr + r.stdout), time.time() - t0


def main() -> int:
    failures = []

    def check(name, cond):
        print(("ok   " if cond else "FAIL ") + name)
        if not cond:
            failures.append(name)

    # ---- fuzzing: never raise, never hang ----
    rnd = random.Random(2024)
    bad = slow = 0
    for _ in range(300):
        txt = _mutate(BASE_CSS, CSS_JUNK, rnd)
        t0 = time.time()
        _alarm(5)
        try:
            _tokens.analyze_tokens(css.parse_css(txt))
        except Exception:
            bad += 1
        finally:
            if hasattr(signal, "SIGALRM"):
                signal.alarm(0)
        slow += time.time() - t0 > 3
    check("CSS fuzz: 300 corrupted stylesheets, no exception", bad == 0)
    check("CSS fuzz: none slower than 3s", slow == 0)
    bad = slow = 0
    for _ in range(150):
        txt = _mutate(BASE_HTML, HTML_JUNK, rnd)
        t0 = time.time()
        _alarm(10)
        try:
            hp.analyze_patterns(txt, css.parse_css(BASE_CSS).rules)
        except Exception:
            bad += 1
        finally:
            if hasattr(signal, "SIGALRM"):
                signal.alarm(0)
        slow += time.time() - t0 > 5
    check("HTML fuzz: 150 corrupted pages, no exception", bad == 0)
    check("HTML fuzz: none slower than 5s", slow == 0)

    # ---- pathological structures ----
    check("nameless at-rule '@{...}' is ignored, later rules survive", [r["sel"] for r in css.parse_css("@{a:b} .x{c:d}").rules] == [".x"])
    check("unbalanced braces/strings/comments terminate", len(css.parse_css('.a{color:red} .b{"unterminated /* never closed {{{').rules) >= 1)
    cyc = (":root{--a:var(--b);--b:var(--c);--c:var(--a);--x:var(--x);--big:" + " ".join(f"var(--v{i})" for i in range(300)) + ";"
           + "".join(f"--v{i}:var(--big);" for i in range(300)) + "}.k{color:var(--a);background:var(--big)}")
    t0 = time.time()
    res = _tokens.Resolver(css.parse_css(cyc).rules)
    out = res.resolve("var(--big)")
    check("cyclic + exploding variable graph resolves fast and is size-capped", time.time() - t0 < 2 and len(out) <= _tokens.MAX_RESOLVED_CHARS)
    check("a cycle stays symbolic instead of looping", "var(" in res.resolve("var(--x)"))
    deep = "<html><body>" + "<div>" * 6000 + "t" + "</div>" * 6000 + "</body></html>"
    try:
        r_ = hp.analyze_patterns(deep, [])
        check("6000-level nesting does not hit the recursion limit", True)
        check("tree depth is capped like a browser", r_["document"]["max_depth"] <= hp.MAX_TREE_DEPTH)
    except RecursionError:
        check("6000-level nesting does not hit the recursion limit", False)
    t0 = time.time()
    hp.analyze_patterns("<b><i><div>" * 4000, [])
    check("a flood of unclosed tags finishes quickly", time.time() - t0 < 10)
    check("empty / whitespace input is handled", hp.analyze_patterns("", [])["document"]["elements"] == 0 and _tokens.analyze_tokens(css.parse_css(""))["stats"]["rules"] == 0)

    # ---- structural state classes ----
    pat = hp.analyze_patterns('<div class="menu"><a class="item">x</a></div>', css.parse_css(".menu.is-open{a:b}.menu.mystery{c:d}.menu .item.active{e:f}.menu{g:h}").rules)
    sc = pat["classes"]["state_classes"]
    check("state classes found structurally (any name, absent from served HTML)", {"is-open", "mystery", "active"} <= set(sc) and "menu" not in sc and "item" not in sc)

    # ---- names and paths ----
    long_url = "http://127.0.0.1:9/" + "segment/" * 60 + "page.html"
    check("folder names are capped", len(screenshots.folder_name(long_url)) <= screenshots.MAX_NAME_CHARS)
    check("capped names stay unique", screenshots.folder_name(long_url) != screenshots.folder_name(long_url + "x"))
    check("Windows reserved names are avoided", screenshots.folder_name("http://nul/") == "_nul" and screenshots.folder_name("file:///x/CON.html") == "_CON")
    from pathlib import Path
    root = Path(tempfile.mkdtemp(prefix="robust-"))
    for u in ("http://x.com/../../etc/passwd", "http://x.com/%2e%2e/%2e%2e/etc/passwd", "http://x.com/C:/Windows/x.js", "http://x.com/a\\b.js"):
        p = website.local_path(root, u, "text/javascript", True)
        check(f"website path stays inside the output folder: {u[-22:]}", str(p.resolve()).startswith(str(root.resolve())))
    p = website.local_path(root, "http://x.com/" + "b" * 400 + ".js", "text/javascript", True)
    check("website shortens an over-long segment but keeps its extension", len(p.name) <= website.MAX_SEGMENT_CHARS and p.name.endswith(".js"))
    shutil.rmtree(root, ignore_errors=True)

    # ---- user agent ----
    os.environ["CAPTURE_USER_AGENT"] = "custom/1"
    check("UA: environment override wins", _common.default_user_agent("130.1.2.3") == "custom/1")
    del os.environ["CAPTURE_USER_AGENT"]
    check("UA: built from the given browser version (reduced form)", "Chrome/130.0.0.0" in _common.default_user_agent("130.1.2.3"))

    # ---- input validation: fast, offline, no browser ----
    for args, needle in ((["--width", "0"], "--width"), (["--height", "-5"], "--height"), (["--zoom", "1"], "Zoom must be"), (["--scale", "99"], "--scale"),
                         (["--scroll", "--overlap", "900"], "--overlap"), (["--slices", "0"], "--slices"), (["--device", "iPhone 13", "--zoom", "50"], "--zoom cannot"),
                         (["--max-shots", "0"], "--max-shots")):
        code, text, secs = cli("screenshots", "http://127.0.0.1:9/x", *args, "--output-dir", tempfile.gettempdir())
        check(f"screenshots rejects {' '.join(args)} instantly", code != 0 and needle in text and secs < 8)
    code, text, _ = cli("screenshots")
    check("screenshots without a target says what to do", code != 0 and "at least one target" in text)

    # ---- design guards ----
    class H(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            body, ctype = ((b'{"a": 1}', "application/json") if self.path == "/data.json" else (b"<!doctype html><title>x</title><p>hello</p>", "text/html"))
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    tmp = tempfile.mkdtemp(prefix="robust-design-")
    if shutil.which("curl") or shutil.which("curl.exe"):
        code, text, _ = cli("design", "tokens", base + "/data.json", "--out", os.path.join(tmp, "j"))
        check("design: a JSON endpoint is rejected as not-HTML", code != 0 and "not an HTML page" in text)
        code, text, _ = cli("design", "tokens", base + "/", "--out", os.path.join(tmp, "m"), "--max-bytes", "10")
        check("design: --max-bytes stops oversized resources", code != 0)
        code, text, _ = cli("design", "tokens", base + "/" + "x" * 300 + ".html", "--out", os.path.join(tmp, "long"))
        check("design: very long URL path does not crash (name capped)", code == 0 or "File name too long" not in text)
        bin_file = os.path.join(tmp, "blob.html")
        open(bin_file, "wb").write(b"\x00\x01\x02 not markup at all")
        code, text, _ = cli("design", "tokens", bin_file, "--out", os.path.join(tmp, "b"))
        check("design: a local file with no tags is rejected", code != 0 and "does not look like HTML" in text)
    else:
        print("SKIP design guard tests (curl not found)")
    srv.shutdown()

    # ---- configurable designs folder names ----
    d = os.path.join(tmp, "proj", "ui-kit")
    os.makedirs(d)
    open(os.path.join(d, "home.html"), "w").write("<p>x</p>")
    r = subprocess.run([sys.executable, os.path.join(HERE, "capture.py"), "designs", "--list", "--folder-names", "ui-kit"], cwd=os.path.join(tmp, "proj"), capture_output=True, text=True)
    check("designs: --folder-names finds an unconventional folder", r.returncode == 0 and "home.html" in r.stdout)
    r = subprocess.run([sys.executable, os.path.join(HERE, "capture.py"), "designs", "--list"], cwd=os.path.join(tmp, "proj"), capture_output=True, text=True)
    check("designs: default names do not find it (so the option matters)", r.returncode != 0)
    shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n{'FAILED: ' + ', '.join(failures) if failures else 'all robustness tests passed'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
