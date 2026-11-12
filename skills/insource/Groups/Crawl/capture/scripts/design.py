"""Capture a site's design: tokens (colors, typography, spacing...) and/or HTML patterns for cloning.

Uses curl (curl.exe on Windows) to fetch the page and EVERY stylesheet it references, then dumps:
  html.dump   the page HTML as served, decoded with its declared charset and saved as UTF-8
              (first line is a provenance comment that records the original encoding)
  css.dump    all CSS concatenated: linked sheets, @import chains, <style> blocks, style="" attributes
and analyses the dumps into:
  tokens   -> design-system.md + design-tokens.json   (colors, variables, typography, spacing, radius,
                                                        shadows, motion, breakpoints, layout, theming)
  patterns -> design-patterns.md + design-patterns.json (skeleton, sections, repeated components with
                                                        exemplar HTML + their CSS, naming conventions,
                                                        layout recipes, custom elements, clone checklist)

Usage:
  python design.py tokens   https://example.com
  python design.py patterns https://example.com --keep-text
  python design.py both     http://localhost:8000 --output-dir .capture/design/local
  python design.py patterns https://spa.example.com --html-file .capture/dom/spa.example.com.html
  python design.py tokens   https://example.com --reuse        # re-analyse existing dumps, no network

Plain curl sees server-delivered HTML/CSS. For JS-rendered pages, run `dom` first and pass its output
with --html-file (CSS is still fetched with curl).
"""
from __future__ import annotations

import argparse
import codecs
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli import add_json_args, add_output_args, begin, emit  # noqa: E402
from _common import default_user_agent, ensure_parent  # noqa: E402
from _cssparse import Sheet, parse_css  # noqa: E402
from _htmlpatterns import analyze_patterns, extract_inline_css, parse_html, render_patterns_md  # noqa: E402
from _techdetect import css_banner_list, last_header_block, parse_header_block, redact_headers  # noqa: E402
from _tokens import analyze_tokens, render_tokens_md  # noqa: E402
from screenshots import folder_name, normalize_url  # noqa: E402

MODES = {"tokens": "tokens", "token": "tokens", "system": "tokens", "colors": "tokens", "color": "tokens",
         "typography": "tokens", "patterns": "patterns", "pattern": "patterns", "clone": "patterns",
         "html": "patterns", "both": "both", "all": "both"}
HEADER = re.compile(r"/\* ===== SOURCE: (.*?) \| (.*?) ===== \*/\n(.*?)\n/\* ===== END ===== \*/", re.S)


# ---------- curl ----------
def curl_bin() -> str:
    for name in (("curl.exe", "curl") if os.name == "nt" else ("curl", "curl.exe")):
        if shutil.which(name):
            return name
    sys.exit("curl not found. Install curl (Windows 10+ ships curl.exe; macOS/Linux: your package manager).")


DEFAULT_MAX_BYTES = 20_000_000      # per fetched resource (curl --max-filesize; applies when the server states the size)


def decode_body(raw: bytes, content_type: str = "") -> tuple[str, str]:
    """Decode a fetched body using, in order: BOM, Content-Type charset, <meta charset> / @charset,
    then UTF-8. Returns (text, encoding name). Dumps are always saved as UTF-8."""
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw[3:].decode("utf-8", "replace"), "utf-8"
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return raw.decode("utf-16", "replace"), "utf-16"
    cs = None
    m = re.search(r"charset\s*=\s*[\"']?([\w.:-]+)", content_type or "", re.I)
    if m:
        cs = m.group(1)
    if not cs:
        head = raw[:4096].decode("ascii", "ignore")
        m = (re.search(r"<meta[^>]+charset\s*=\s*[\"']?([\w.:-]+)", head, re.I)
             or re.search(r"^\s*@charset\s+[\"']([\w.:-]+)[\"']", head, re.I))
        if m:
            cs = m.group(1)
    if cs:
        try:
            return raw.decode(cs, "replace"), codecs.lookup(cs).name
        except LookupError:
            pass
    try:
        return raw.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        return raw.decode("utf-8", "replace"), "utf-8 (lossy)"


def curl_fetch(url: str, a, accept: str = "*/*", want_headers: bool = False) -> dict:
    cmd = [curl_bin(), "-sS", "-g", "-L", "--compressed", "--max-redirs", "8", "--max-time", str(a.timeout),
           "--max-filesize", str(a.max_bytes),
           "-A", a.user_agent, "-H", f"Accept: {accept}"]
    for h in a.header or []:
        cmd += ["-H", h]
    if a.insecure:
        cmd.append("-k")
    hdr_path = None
    if want_headers and not url.startswith("file://"):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".hdr")
        tmp.close()
        hdr_path = tmp.name
        cmd += ["-D", hdr_path]
    cmd += ["-w", "\n%{http_code}\t%{content_type}\t%{url_effective}", url]
    p = subprocess.run(cmd, capture_output=True)
    raw_headers = ""
    if hdr_path:
        try:
            raw_headers = redact_headers(last_header_block(Path(hdr_path).read_text(encoding="utf-8", errors="replace")))
        finally:
            Path(hdr_path).unlink(missing_ok=True)
    if p.returncode != 0:
        return {"url": url, "ok": False, "status": 0, "error": p.stderr.decode("utf-8", "replace").strip() or f"curl exit {p.returncode}", "body": "", "encoding": ""}
    body, _, tail = p.stdout.rpartition(b"\n")
    parts = tail.decode("utf-8", "replace").split("\t", 2)
    status = int(parts[0]) if parts and parts[0].isdigit() else 0
    ctype, eff = (parts + ["", ""])[1:3] if len(parts) >= 2 else ("", url)
    is_file = url.startswith("file://")
    ok = is_file or 200 <= status < 300
    text, enc = decode_body(body, ctype)
    return {"url": url, "final_url": eff or url, "ok": ok, "status": status, "content_type": ctype,
            "body": text, "encoding": enc, "raw_headers": raw_headers, "error": "" if ok else f"HTTP {status}"}


# ---------- dumps ----------
def source_block(label: str, info: str, text: str) -> str:
    return f"/* ===== SOURCE: {label} | {info} ===== */\n{text.rstrip()}\n/* ===== END ===== */\n\n"


def read_css_dump(path: Path) -> list[tuple[str, str, str]]:
    return HEADER.findall(path.read_text(encoding="utf-8"))


def fetch_all(url: str, a, out: Path) -> dict:
    """Fetch HTML + stylesheets with curl and write html.dump / css.dump / sources.json."""
    sources = []
    raw_headers = ""
    if a.html_file:
        html, enc = decode_body(Path(a.html_file).read_bytes(), "")
        final = url
        sources.append({"kind": "html", "url": f"file:{a.html_file}", "ok": True, "status": 0, "bytes": len(html.encode())})
        print(f"[+] HTML from file {a.html_file}")
    else:
        print(f"[+] curl {url}")
        r = curl_fetch(url, a, "text/html,application/xhtml+xml,*/*;q=0.8", want_headers=True)
        raw_headers = r.get("raw_headers", "")
        sources.append({"kind": "html", "url": url, "ok": r["ok"], "status": r["status"], "bytes": len(r["body"].encode()), "error": r["error"]})
        if not r["ok"]:
            sys.exit(f"Could not fetch {url}: {r['error']}")
        html, final, enc = r["body"], r.get("final_url") or url, r["encoding"]
        ctype = r.get("content_type", "").lower()
        if ctype and not any(k in ctype for k in ("html", "xml", "text/plain")):
            sys.exit(f"{url} is not an HTML page (content-type {ctype}). If you have the rendered HTML saved, pass it with --html-file.")
    if not re.search(r"<[A-Za-z!]", html[:50000]):
        sys.exit("The page content does not look like HTML (no tags found); nothing to analyse.")
    head = f"<!-- capture:design source={final} fetched={time.strftime('%Y-%m-%dT%H:%M:%S')} via={'curl.exe' if os.name == 'nt' else 'curl'} encoding={enc} -->\n"
    ensure_parent(str(out / "html.dump"))
    if raw_headers:      # response headers of the page request (cookie values redacted)
        (out / "headers.dump").write_text(raw_headers + "\n", encoding="utf-8")
    else:
        (out / "headers.dump").unlink(missing_ok=True)       # never leave headers from an earlier run next to new dumps
    (out / "html.dump").write_text(head + html, encoding="utf-8")

    tree = parse_html(html)
    base = next((n.attrs["href"] for n in tree.walk() if n.tag == "base" and n.attrs.get("href")), "")
    base_url = urljoin(final, base) if base else final
    queue: list[tuple[str, int]] = []
    for n in tree.walk():
        if n.tag == "link" and n.attrs.get("href"):
            rel = n.attrs.get("rel", "").lower()
            if "stylesheet" in rel or (rel == "preload" and n.attrs.get("as") == "style"):
                queue.append((urljoin(base_url, n.attrs["href"]), 0))
    seen, css_parts, host = set(), [], urlparse(final).netloc
    n_css = 0
    while queue and n_css < a.max_css:
        u, depth = queue.pop(0)
        if u in seen or u.startswith("data:"):
            continue
        seen.add(u)
        if a.no_external_css and urlparse(u).netloc != host:
            sources.append({"kind": "css", "url": u, "ok": False, "status": 0, "error": "external skipped (--no-external-css)"})
            continue
        print(f"[+] curl {u}")
        r = curl_fetch(u, a, "text/css,*/*;q=0.1")
        ctype = r.get("content_type", "").lower()
        ok = r["ok"] and "html" not in ctype
        sources.append({"kind": "css", "url": u, "ok": ok, "status": r["status"], "bytes": len(r["body"].encode()), "error": "" if ok else (r["error"] or f"unexpected content-type {ctype}")})
        if not ok:
            print(f"    skipped: {sources[-1]['error']}")
            continue
        n_css += 1
        css_parts.append(source_block(u, f"status {r['status']}, {len(r['body'].encode())} bytes", r["body"]))
        if depth < 3:
            for imp in parse_css(r["body"]).imports:
                queue.append((urljoin(r.get("final_url") or u, imp), depth + 1))

    blocks, attrs = extract_inline_css(tree)
    for i, b in enumerate(blocks, 1):
        css_parts.append(source_block(f"inline <style> #{i} (in html.dump)", f"{len(b.encode())} bytes", b))
    if attrs:
        css_parts.append(source_block("inline style attributes (in html.dump)", f"{len(attrs)} elements",
                                      "\n".join(f"{sel} {{ {val} }}" for sel, val in attrs)))
    (out / "css.dump").write_text("".join(css_parts), encoding="utf-8")
    (out / "sources.json").write_text(json.dumps({"page": final, "tool": curl_bin(), "sources": sources}, indent=2), encoding="utf-8")
    total_css = sum(len(p) for p in css_parts)
    print(f"[+] html.dump ({len(html):,} chars) and css.dump ({n_css} linked sheet(s), {len(blocks)} <style>, {len(attrs)} inline attrs, {total_css:,} chars)")
    if not css_parts:
        print("[!] No CSS found in the served HTML. If the page is JS-rendered, run `dom` first and pass --html-file.")
    return {"final": final}


def out_name(url: str) -> str:
    """Folder name for a URL: host + path slug (+ short hash of the query), so different pages never collide."""
    name = folder_name(url)
    q = urlparse(url).query
    return f"{name}_{hashlib.md5(q.encode()).hexdigest()[:6]}" if q else name


def _output_format(path: str | None, requested: str | None, mode: str) -> str:
    """Pick md/json/both: an explicit --format wins, otherwise the -o extension, otherwise md."""
    if requested:
        return requested
    ext = Path(path).suffix.lower() if path else ""
    if ext == ".json":
        return "json"
    if ext == ".md":
        return "md"
    return "both" if mode == "both" else "md"


def _write_single(output: str, fmt: str, tokens, pat, meta: dict) -> list[Path]:
    """Write the consolidated report(s) requested with -o. Returns the paths actually written."""
    target = Path(output)
    written: list[Path] = []
    formats = ["md", "json"] if fmt == "both" else [fmt]
    for one in formats:
        suffix = ".md" if one == "md" else ".json"
        path = target if target.suffix.lower() == suffix else target.with_suffix(suffix) \
            if target.suffix else Path(str(target) + suffix)
        ensure_parent(str(path))
        if one == "json":
            doc = {"meta": meta}
            if tokens is not None:
                doc["tokens"] = tokens
            if pat is not None:
                doc["patterns"] = pat
            path.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
        else:
            parts = []
            if tokens is not None:
                parts.append(render_tokens_md(tokens, meta))
            if pat is not None:
                parts.append(render_patterns_md(pat, tokens, meta))
            path.write_text("\n\n---\n\n".join(parts), encoding="utf-8")
        written.append(path)
    return written


# ---------- CLI ----------
def add_args(p):
    p.add_argument("items", nargs="*", metavar="MODE URL",
                   help="tokens | patterns | both, then the page URL (ask the user which mode if unclear)")
    p.add_argument("--mode", metavar="MODE", help="Mode, same as the first positional (tokens|patterns|both and aliases)")
    p.add_argument("--url", help="Page URL, same as the second positional")
    add_output_args(
        p,
        dir_help="Output folder for dumps and reports (default .capture/design/<name>; name = host + path, "
                 "plus a short hash if the URL has a query)",
    )
    p.add_argument("--format", choices=["md", "json", "both"],
                   help="Format for -o/--output (default: infer from the extension, else md; both in both mode)")
    add_json_args(p)
    p.add_argument("--reuse", action="store_true", help="Skip fetching; analyse existing html.dump/css.dump in --output-dir")
    p.add_argument("--html-file", help="Analyse this HTML (e.g. output of `dom`) instead of fetching the page; URL is used as base")
    p.add_argument("--max-css", type=int, default=40, help="Cap on stylesheets fetched (default 40)")
    p.add_argument("--no-external-css", action="store_true", help="Skip stylesheets on other hosts (e.g. Google Fonts CSS)")
    p.add_argument("--keep-text", action="store_true", help="Keep (truncated) text in HTML exemplars; default replaces text with an ellipsis")
    p.add_argument("--top", type=int, default=12, help="How many components / top colors to report (default 12)")
    p.add_argument("--timeout", type=int, default=30, help="curl --max-time seconds (default 30)")
    p.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES, help="Skip any single resource larger than this (default 20 MB)")
    p.add_argument("--header", action="append", metavar="'Name: value'", help="Extra request header for curl (repeatable)")
    p.add_argument("--user-agent", default=default_user_agent(), help="User agent (default: browser-like; env CAPTURE_USER_AGENT overrides)")
    p.add_argument("--signatures", metavar="FILE", help="JSON file with extra/override technology signatures (same format as scripts/data/tech_signatures.json)")
    p.add_argument("--insecure", action="store_true", help="curl -k (self-signed local HTTPS)")


def run(args):
    items = list(args.items)
    mode = None
    if items and items[0].lower() in MODES:
        mode = MODES[items.pop(0).lower()]
    if args.mode:
        if args.mode.lower() not in MODES:
            sys.exit(f"Unknown --mode {args.mode!r}. Use tokens, patterns or both.")
        mode = MODES[args.mode.lower()]
    url = args.url or (items[0] if items else None)
    if not mode:
        print("MODE REQUIRED: ask the user which design capture they want:\n"
              "  tokens   - design system: colors, typography, spacing, radius, shadows, motion, breakpoints\n"
              "  patterns - HTML usage patterns: skeleton, sections, repeated components + their CSS, for a high-fidelity clone\n"
              "  both\nThen run: capture.py design <tokens|patterns|both> <url>", file=sys.stderr)
        sys.exit(2)
    if not url and not args.reuse:
        sys.exit("Give the page URL (e.g. https://example.com or http://localhost:8000).")
    if url:
        try:
            url = normalize_url(url)          # bare domains, localhost, and existing local files (file://)
        except FileNotFoundError as e:
            sys.exit(str(e))

    name = out_name(url) if url else "site"
    out = Path(args.output_dir) if args.output_dir else Path(".capture/design") / name
    out.mkdir(parents=True, exist_ok=True)
    payload = {"command": "design", "mode": mode, "url": url or "", "output_dir": str(out)}

    with begin(args) as real:
        if args.reuse:
            if not (out / "html.dump").exists() or not (out / "css.dump").exists():
                sys.exit(f"--reuse needs {out}/html.dump and css.dump")
            m = re.match(r"<!-- capture:design source=(\S+)", (out / "html.dump").read_text(encoding="utf-8")[:300])
            final = m.group(1) if m else (url or "")
            print(f"[+] reusing dumps in {out}")
        else:
            final = fetch_all(url, args, out)["final"]

        # analyse FROM the dumps (single source of truth)
        html_text = re.sub(r"^<!-- capture:design[^>]*-->\n", "", (out / "html.dump").read_text(encoding="utf-8"), count=1)
        sheet = Sheet()
        srcs = read_css_dump(out / "css.dump")
        for label, _info, text in srcs:
            parse_css(text, label, sheet)
        meta = {"url": final, "host": urlparse(final).netloc or name, "css_sources": len(srcs)}
        written = [out / "html.dump", out / "css.dump", out / "sources.json"]
        tokens = None
        pat = None

        if mode in ("tokens", "both"):
            tokens = analyze_tokens(sheet, top=args.top)
            (out / "design-tokens.json").write_text(json.dumps(tokens, indent=2, ensure_ascii=False), encoding="utf-8")
            (out / "design-system.md").write_text(render_tokens_md(tokens, meta), encoding="utf-8")
            written += [out / "design-system.md", out / "design-tokens.json"]
            s = tokens["stats"]
            sizes = [x["px"] for x in tokens["typography"]["sizes"]]
            print(f"[+] tokens: {s['unique_colors']} colors, {s['variables']} variables ({len(tokens['variables']['scales'])} scales, "
                  f"{sum(len(d) for d in tokens['colors']['ramps'].values())} color ramps), {len(tokens['typography']['fonts'])} font faces, "
                  f"{len(sizes)} font sizes, spacing: {tokens['spacing']['scale_guess']}, {len(tokens['breakpoints'])} breakpoint queries")

        if mode in ("patterns", "both"):
            headers = parse_header_block((out / "headers.dump").read_text(encoding="utf-8")) if (out / "headers.dump").exists() else {}
            pat = analyze_patterns(html_text, sheet.rules, final, keep_text=args.keep_text, top=args.top, headers=headers,
                                   css_text="\n".join(t for _l, _i, t in srcs), css_banners=css_banner_list([(l, t) for l, _i, t in srcs]),
                                   signatures_file=args.signatures)
            (out / "design-patterns.json").write_text(json.dumps(pat, indent=2, ensure_ascii=False), encoding="utf-8")
            (out / "design-patterns.md").write_text(render_patterns_md(pat, tokens, meta), encoding="utf-8")
            written += [out / "design-patterns.md", out / "design-patterns.json"]
            print(f"[+] patterns: {pat['document']['elements']} elements, {len(pat['sections'])} top-level sections, "
                  f"{len(pat['components'])} repeated components, {len(pat['custom_elements'])} custom elements, naming: {pat['classes']['verdict']}")

        if args.output:
            fmt = _output_format(args.output, args.format, mode)
            single = _write_single(args.output, fmt, tokens, pat, meta)
            written += single
            payload["output"] = [str(p) for p in single]

        print("Saved:")
        for w in written:
            print(f"  {w}  ({w.stat().st_size:,} bytes)")
        payload["files"] = [str(w) for w in written]
        payload["url"] = final
        if tokens is not None:
            payload["tokens"] = tokens.get("stats", {})
        if pat is not None:
            payload["patterns"] = {
                "sections": len(pat["sections"]),
                "components": len(pat["components"]),
                "custom_elements": len(pat["custom_elements"]),
                "naming": pat["classes"]["verdict"],
            }
    emit(args, payload, real)


if __name__ == "__main__":
    from _common import utf8_console
    utf8_console()
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    add_args(ap)
    try:
        run(ap.parse_args())
    except SystemExit:
        raise
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
