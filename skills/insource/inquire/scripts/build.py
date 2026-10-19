#!/usr/bin/env python3
"""Build an Inquire page: splice a content JSON file into assets/template.html.

usage: build.py content.json --out page.html [--mode verbose|concise] [--lang en] [--dir ltr|rtl]
"""
import argparse, html, json, pathlib, sys

RTL = {"ar", "he", "fa", "ur", "ps", "sd", "yi"}
TEMPLATE = pathlib.Path(__file__).resolve().parent.parent / "assets" / "template.html"


def embed(data):
    """JSON that is safe inside an inline <script> block."""
    t = json.dumps(data, ensure_ascii=False)
    return (t.replace("</", "<\\/").replace("<!--", "<\\u0021--")
             .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("content")
    ap.add_argument("--out", required=True)
    ap.add_argument("--mode", choices=["verbose", "concise"])
    ap.add_argument("--lang")
    ap.add_argument("--dir", choices=["ltr", "rtl"])
    a = ap.parse_args()

    d = json.loads(pathlib.Path(a.content).read_text(encoding="utf-8"))
    d["mode"] = a.mode or d.get("mode") or "verbose"      # verbose is the default
    lang = a.lang or d.get("lang") or "en"
    direction = a.dir or ("rtl" if lang.split("-")[0].lower() in RTL else "ltr")

    page = TEMPLATE.read_text(encoding="utf-8")
    for marker in ("__INQUIRE_DATA__", "__TITLE__", "__LANG__", "__DIR__"):
        if page.count(marker) != 1:
            sys.exit(f"template is broken: {marker} appears {page.count(marker)} times")
    page = (page.replace("__INQUIRE_DATA__", embed(d))
                .replace("__TITLE__", html.escape(d.get("title", "Inquire")))
                .replace("__LANG__", html.escape(lang)).replace("__DIR__", direction))
    pathlib.Path(a.out).write_text(page, encoding="utf-8")
    print(f"built {a.out} ({len(page)//1024} KB, mode={d['mode']}, lang={lang}, dir={direction})")


if __name__ == "__main__":
    main()
