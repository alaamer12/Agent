"""Regression tests for `design` (parser, charset, naming, local files). Offline; needs curl for the last two.

  python test_design.py        # exit 0 = all passed
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _cssparse as css  # noqa: E402
import _htmlpatterns as hp  # noqa: E402
import design  # noqa: E402


def main() -> int:
    failures = []

    def check(name, cond):
        print(("ok   " if cond else "FAIL ") + name)
        if not cond:
            failures.append(name)

    # charset decoding
    ar = "مرحبا بالعالم"
    text, enc = design.decode_body(f'<meta charset="windows-1256">{ar}'.encode("cp1256"), "text/html")
    check("charset: <meta charset> windows-1256", ar in text and enc == "cp1256")
    text, enc = design.decode_body(ar.encode("cp1256"), "text/html; charset=windows-1256")
    check("charset: Content-Type header wins", ar in text)
    check("charset: UTF-8 BOM stripped", design.decode_body(b"\xef\xbb\xbfhello", "")[0] == "hello")
    check("charset: UTF-8 default", design.decode_body(ar.encode("utf-8"), "")[0] == ar)
    check("charset: @charset in CSS", "\u00e9" in design.decode_body('@charset "iso-8859-1"; a{content:"\u00e9"}'.encode("latin-1"), "text/css")[0])
    check("charset: unknown name falls back, never crashes", isinstance(design.decode_body(b"abc", "text/html; charset=bogus-xyz")[0], str))

    # escaped (Tailwind-style) selectors
    sheet = css.parse_css(r""".md\:flex{display:flex}.hover\:bg-\[\#0f0\]:hover{background:#0f0}.w-\[calc\(100\%-1rem\)\]{width:1px}.a\(b{color:red}.after{color:blue}
@media (min-width:768px){.md\:flex{display:flex}}""")
    check("parser: escaped selectors don't swallow later rules", len(sheet.rules) == 6 and any(r["sel"] == ".after" for r in sheet.rules))
    idx = hp.CssIndex(sheet.rules)
    check("class index: escaped CSS names match HTML class names", "md:flex" in idx.by_class and "hover:bg-[#0f0]" in idx.by_class)
    html = '<ul><li class="md:flex a"><b class="x">1</b></li><li class="md:flex a"><b class="x">2</b></li><li class="md:flex a"><b class="x">3</b></li></ul>'
    pat = hp.analyze_patterns(html, sheet.rules)
    check("patterns: Tailwind-style class finds its CSS rules", any("md:flex" in c["css"] for c in pat["components"]))

    # output naming
    check("name: root URL -> host", design.out_name("http://127.0.0.1:9300/") == "127.0.0.1_9300")
    check("name: different pages differ", design.out_name("https://x.com/a") != design.out_name("https://x.com/b"))
    check("name: query adds a stable hash", design.out_name("https://x.com/a?p=1") != design.out_name("https://x.com/a?p=2")
          and design.out_name("https://x.com/a?p=1") == design.out_name("https://x.com/a?p=1"))

    # end to end on local files through curl (file://)
    if shutil.which("curl") or shutil.which("curl.exe"):
        tmp = tempfile.mkdtemp(prefix="design-test-")
        with open(os.path.join(tmp, "index.html"), "wb") as f:
            f.write(f'<!doctype html><meta charset="windows-1256"><title>{ar}</title><link rel="stylesheet" href="s.css"><h1 class="t">{ar}</h1>'.encode("cp1256"))
        with open(os.path.join(tmp, "s.css"), "w", encoding="utf-8") as f:
            f.write(".t{color:#abcdef;font-size:2rem}")
        out = os.path.join(tmp, "out")
        r = subprocess.run([sys.executable, os.path.join(HERE, "capture.py"), "design", "both", os.path.join(tmp, "index.html"), "--out", out],
                           capture_output=True, text=True)
        have = lambda n: os.path.exists(os.path.join(out, n))
        check("local file: design runs and writes all outputs", r.returncode == 0 and all(have(n) for n in ("html.dump", "css.dump", "design-system.md", "design-patterns.md")))
        if have("html.dump"):
            h = open(os.path.join(out, "html.dump"), encoding="utf-8").read()
            check("local file: Arabic cp1256 page decoded correctly in html.dump", ar in h and "\ufffd" not in h and "encoding=cp1256" in h)
        if have("css.dump"):
            check("local file: relative stylesheet fetched into css.dump", "#abcdef" in open(os.path.join(out, "css.dump"), encoding="utf-8").read())
        r = subprocess.run([sys.executable, os.path.join(HERE, "capture.py"), "design", "tokens", os.path.join(tmp, "missing.html")], capture_output=True, text=True)
        check("local file: missing path gives a clear error", r.returncode != 0 and "No such file" in (r.stderr + r.stdout))
        shutil.rmtree(tmp, ignore_errors=True)
    else:
        print("SKIP end-to-end local-file tests (curl not found)")

    print(f"\n{'FAILED: ' + ', '.join(failures) if failures else 'all design tests passed'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
