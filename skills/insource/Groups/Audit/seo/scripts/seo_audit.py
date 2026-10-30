#!/usr/bin/env python3
"""seo_audit.py — self-contained first-packet SEO auditor (universal 100-point rubric).

Works on ANY stack: it only needs a URL (served by anything) or a local HTML file
(build output, saved "View Source"). No project dependencies; stdlib only.

Usage:
    python seo_audit.py <url | html-file> [-k KEYWORD] [-m wincher|google|raw]
                        [--target 100] [--json] [--ua "custom UA"] [--timeout SEC]

Modes (crawler patience budgets): wincher=500ms, google=5000ms, raw=no limit.
Exit codes: 0 at/above target, 1 below, 2 fetch/parse error.

Scores 7 sections / 100 points: Title 27, Headings 20, Body 28, Meta 5, Media 4,
Code 6, URL 10. See references/rubric.md for exact thresholds.
"""

import argparse
import json
import re
import sys
import time
from html.parser import HTMLParser
from urllib.request import Request, urlopen

BUDGETS = {"wincher": 500, "google": 5000, "raw": 10**9}
UAS = {
    "wincher": "Mozilla/5.0 (compatible; WincherBot/2.1; +http://www.wincher.com/) Web-Crawler",
    "google": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "raw": "python-seo-audit/1.0",
}


def normalize(text):
    text = re.sub(r"[\u0610-\u061A\u064B-\u065F\u0300-\u036F]", "", text)
    text = re.sub(r"[\u0623\u0625\u0627\u0671]", "\u0627", text)
    text = text.replace("\u0629", "\u0647")
    return text.lower().strip()


def kw_count(kw, text):
    if not kw or not text:
        return 0
    return normalize(text).count(normalize(kw))


def kw_position(kw, text):
    if not kw or not text:
        return -1
    nkw, ntxt = normalize(kw), normalize(text)
    pos = ntxt.find(nkw)
    if pos == -1:
        return -1
    return round((1 - pos / max(len(ntxt), 1)) * 100)


class PacketParser(HTMLParser):
    """Incremental parser; each element records arrival time (ms) while streaming."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = None
        self.description = None
        self.canonical = None
        self.h = {"h1": [], "h2": [], "h3": []}
        self.images = []
        self.css = []
        self.alternates = []      # (hreflang, href, ms)
        self.ld_count = 0         # JSON-LD script blocks in raw HTML
        self.text_parts = []
        self.word_count = 0
        self._t = 0.0
        self._cur = None          # tag currently collecting text
        self._skip_depth = 0

    def set_time(self, ms):
        self._t = ms

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "script" and (d.get("type") or "").lower() == "application/ld+json":
            self.ld_count += 1
        if tag in ("script", "style", "noscript", "template"):
            self._skip_depth += 1
            return
        if tag == "title" and self.title is None:
            self._cur = "title"
        elif tag == "meta":
            name = (d.get("name") or "").lower()
            if name == "description" and self.description is None:
                self.description = (d.get("content") or "", self._t)
        elif tag == "link":
            rel = (d.get("rel") or "").lower()
            href = d.get("href") or ""
            if rel == "canonical" and self.canonical is None:
                self.canonical = (href, self._t)
            elif rel == "stylesheet" and href and not href.startswith("data:"):
                self.css.append((href, self._t))
            elif rel == "alternate" and d.get("hreflang"):
                self.alternates.append(((d.get("hreflang") or "").lower(), href, self._t))
        elif tag in self.h:
            self._cur = tag
        elif tag == "img":
            self.images.append((d.get("src", ""), d.get("alt", "") or "", self._t))

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "template"):
            self._skip_depth = max(0, self._skip_depth - 1)
        elif tag == "title" or tag in self.h:
            if self._cur == tag:
                self._cur = None

    def handle_data(self, data):
        text = data.strip()
        if not text or self._skip_depth:
            return
        if self._cur == "title" and self.title is None:
            self.title = (text, self._t)
        elif self._cur in self.h:
            self.h[self._cur].append((text, self._t))
        self.text_parts.append(text)
        self.word_count += len(text.split())


def load(source, mode, ua, timeout):
    """Stream HTML; returns (parser, total_bytes, timing) or raises."""
    p = PacketParser()
    start = time.monotonic()
    if re.match(r"^https?://", source):
        req = Request(source, headers={"User-Agent": ua, "Accept": "text/html"})
        resp = urlopen(req, timeout=timeout)
        deadline = BUDGETS[mode] / 1000.0 if mode != "raw" else None
        total = 0
        aborted = False
        while True:
            elapsed = time.monotonic() - start
            if deadline and elapsed > deadline:
                aborted = True
                break
            try:
                chunk = resp.read(4096)
            except Exception:
                aborted = True
                break
            if not chunk:
                break
            total += len(chunk)
            p.set_time(elapsed * 1000)
            try:
                p.feed(chunk.decode("utf-8", errors="replace"))
            except Exception:
                pass
        ttfb_ms = None
        return p, total, aborted, ttfb_ms
    with open(source, "rb") as f:
        raw = f.read()
    p.set_time(0.0)
    p.feed(raw.decode("utf-8", errors="replace"))
    return p, len(raw), False, None


def score(p, url, kw, mode, total_bytes):
    ok = (lambda t: mode == "raw" or t is None or t <= BUDGETS[mode])
    checks = []

    def add(section, label, earned, maxp, detail):
        checks.append({"section": section, "check": label, "earned": earned,
                       "max": maxp, "detail": detail})

    title = p.title[0] if p.title and ok(p.title[1]) else ""
    h1s = [(t, ms) for t, ms in p.h["h1"] if ok(ms)]
    body = " ".join(p.text_parts)
    wc = p.word_count

    # Title /27
    add("Title", "exists", 7 if title else 0, 7, title[:60] or "missing/too late")
    if kw:
        c = kw_count(kw, title)
        add("Title", "keyword", 8 if 1 <= c <= 2 else (4 if c > 2 else 0), 8, f"{c}x")
        pos = kw_position(kw, title)
        add("Title", "position", 6 if pos >= 80 else (3 if pos >= 50 else 0), 6, f"pos {pos}")
    else:
        add("Title", "keyword", 0, 8, "no keyword provided")
        add("Title", "position", 0, 6, "no keyword provided")
    n = len(title)
    add("Title", "length", 6 if 30 <= n <= 60 else (3 if n < 30 or n <= 70 else 0), 6, f"{n} chars")

    # Headings /20
    h1 = " ".join(t for t, _ in h1s)
    if kw and h1:
        add("Headings", "keyword-in-h1", 5 if kw_count(kw, h1) else 0, 5, h1[:60])
        pos = kw_position(kw, h1)
        add("Headings", "h1-position", 5 if pos >= 80 else (3 if pos >= 50 else 0), 5, f"pos {pos}")
    else:
        add("Headings", "keyword-in-h1", 0, 5, "h1 missing or no keyword")
        add("Headings", "h1-position", 0, 5, "h1 missing or no keyword")
    add("Headings", "h1-length", 2 if h1 and len(h1) <= 40 else 0, 2, f"{len(h1)} chars")
    add("Headings", "h1-count", 4 if len(h1s) == 1 else 0, 4, f"{len(h1s)} h1")
    core = normalize(re.split(r"[|\u2013-]", title)[0]).strip() if title else ""
    same = bool(h1) and bool(core) and core == normalize(h1)
    add("Headings", "h1-differs-from-title", 0 if same or not h1 or not title else 2, 2,
        "identical" if same else "differs")
    subs = " ".join(t for tag in ("h2", "h3") for t, ms in p.h[tag] if ok(ms))
    if kw:
        sub_hits = sum(1 for tag in ("h2", "h3") for t, ms in p.h[tag] if ok(ms) and kw_count(kw, t))
        add("Headings", "keyword-in-subheadings", 2 if sub_hits >= 2 else (1 if sub_hits == 1 else 0),
            2, f"{sub_hits} keyword headings")
    else:
        add("Headings", "keyword-in-subheadings", 0, 2, "no keyword provided")

    # Body /28
    add("Body", "word-count", 14 if wc >= 500 else (7 if wc >= 300 else (3 if wc >= 100 else 0)),
        14, f"{wc} words")
    if kw:
        c = kw_count(kw, body)
        add("Body", "keyword-mentions", 14 if c >= 3 else (7 if c == 2 else (3 if c == 1 else 0)),
            14, f"{c}x")
    else:
        add("Body", "keyword-mentions", 0, 14, "no keyword provided")

    # Meta /5
    desc = p.description[0] if p.description and ok(p.description[1]) else ""
    add("Meta", "keyword-in-description", 5 if desc and kw_count(kw, desc) else 0, 5, desc[:60] or "missing")

    # Media /4
    vis_imgs = [(s, a, ms) for s, a, ms in p.images if ok(ms)]
    hit = any(kw_count(kw, a) for _, a, _ in vis_imgs)
    add("Media", "keyword-in-alt", 4 if hit else 0, 4,
        f"{len(vis_imgs)} imgs, alt {'has' if hit else 'lacks'} keyword")

    # Code /6
    add("Code", "external-css", 3 if any(ok(ms) for _, ms in p.css) else 0, 3, f"{len(p.css)} sheets")
    pct = (len(body) / max(total_bytes, 1)) * 100
    add("Code", "visible-text-ratio", 3 if pct >= 2 else (1 if pct >= 1 else 0), 3, f"{pct:.2f}%")

    # URL /10
    if re.match(r"^https?://", url):
        if kw:
            full = kw_count(kw, url) > 0
            partial = bool(re.match(r"^https?://", url)) and not full and any(
                w in normalize(url) for w in normalize(kw).split())
            add("URL", "keyword-in-url", 5 if full else (3 if partial else 0), 5, "")
        else:
            add("URL", "keyword-in-url", 0, 5, "no keyword provided")
        add("URL", "https", 5 if url.lower().startswith("https://") else 0, 5, "")
    else:
        add("URL", "https", 0, 0, "local file — skipped")

    earned = sum(c["earned"] for c in checks)
    total = sum(c["max"] for c in checks)
    alts = [(hl, u) for hl, u, ms in p.alternates if ok(ms)]
    hreflang = None
    if alts:
        self_ref = any(u and u.rstrip("/") == url.rstrip("/") for _, u in alts)
        bad_codes = [hl for hl, _ in alts
                     if not re.fullmatch(r"[a-z]{2,3}(-[a-z]{2,3}(-[a-z]{2,4})?)?|x-default", hl)]
        hreflang = {"count": len(alts), "languages": sorted({hl for hl, _ in alts}),
                    "self_referencing": self_ref, "invalid_codes": bad_codes}
    return {"checks": checks, "earned": earned, "max": total,
            "pct": round(earned / total * 100) if total else 0,
            "words": wc, "ratio_pct": round(pct, 2),
            "hreflang": hreflang, "ld_json_blocks_in_raw_html": p.ld_count}


def main():
    ap = argparse.ArgumentParser(description="Universal first-packet SEO auditor")
    ap.add_argument("source", help="http(s) URL or local HTML file")
    ap.add_argument("--keyword", "-k", default="")
    ap.add_argument("--mode", "-m", default="wincher", choices=list(BUDGETS))
    ap.add_argument("--target", type=int, default=100)
    ap.add_argument("--ua", default=None)
    ap.add_argument("--timeout", type=int, default=15)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    try:
        p, total_bytes, aborted, _ = load(args.source, args.mode,
                                          args.ua or UAS[args.mode], args.timeout)
    except Exception as e:
        print(f"ERROR: cannot fetch/parse {args.source}: {str(e)[:200]}")
        return 2

    r = score(p, args.source, args.keyword, args.mode, total_bytes)
    r["source"] = args.source
    r["mode"] = args.mode
    r["bytes"] = total_bytes
    r["truncated_at_budget"] = aborted

    if args.json:
        print(json.dumps(r, ensure_ascii=False))
    else:
        sections = {}
        for c in r["checks"]:
            sections.setdefault(c["section"], [0, 0])
            sections[c["section"]][0] += c["earned"]
            sections[c["section"]][1] += c["max"]
        print(f"SEO AUDIT  {args.source}  mode={args.mode}  kw='{args.keyword or '(none)'}'")
        for s, (e, m) in sections.items():
            if m == 0:
                continue
            flag = "OK " if e == m else "LOW"
            print(f"  [{flag}] {s:<10} {e:>3}/{m}")
            for c in r["checks"]:
                if c["section"] == s and c["earned"] < c["max"]:
                    print(f"         - {c['check']}: {c['earned']}/{c['max']} {c['detail']}")
        if aborted:
            print(f"  NOTE: read stopped at {BUDGETS[args.mode]}ms budget — late content scored 0 (fix timing, P10)")
        h = r["hreflang"]
        if h:
            if not h["self_referencing"]:
                print("  WARN: hreflang set present but page does NOT self-reference (top real-world error)")
            if h["invalid_codes"]:
                print(f"  WARN: invalid hreflang codes: {h['invalid_codes']}")
        elif re.match(r"^https?://", args.source):
            print("  INFO: no hreflang annotations found in raw HTML (needed if this page has language variants)")
        if r["ld_json_blocks_in_raw_html"] == 0:
            print("  INFO: no JSON-LD in raw HTML — may be JS-injected; verify with a rendered check before reporting it missing")
        print(f"SCORE: {r['earned']}/{r['max']} ({r['pct']}%)  words={r['words']}  ratio={r['ratio_pct']}%")
        print("GATE: PASS" if r["pct"] >= args.target else "GATE: FAIL")
    return 0 if r["pct"] >= args.target else 1


if __name__ == "__main__":
    sys.exit(main())
