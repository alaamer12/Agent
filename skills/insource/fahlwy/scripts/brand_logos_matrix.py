#!/usr/bin/env python3
"""fahlwy brand-logo matrix prover.

Prove a brand-logo source the way the skill demands: real bytes of the right
type, for a NAMED set of brands, with slugs resolved from the provider's own
manifest instead of guessed.

Two failure modes this exists to catch, both invisible to a status code:
  * neighbouring slug -- `thesvg-color/github` 404s while `github-actions`
    exists; a prefix matcher "passes" on the wrong mark. Default behaviour is
    exact-name-only; derived matches need --allow-derived to be reported at all.
  * stub-serving host -- one provider that answers 200 with the SAME 1x1 PNG or
    the same HTML body for every brand. Cross-brand hashes are compared.

Usage:
    brand_logos_matrix.py                      # all providers x default 12 brands
    brand_logos_matrix.py --list-providers
    brand_logos_matrix.py -p simple-icons,thesvg-color -b github,windsurf
    brand_logos_matrix.py --min 10 --json logos.json

Exit 0 only when every probed provider reaches --min verified brands.
TLS verification stays ON; 429/5xx are retried with backoff, 4xx never.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = {"User-Agent": ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                     "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")}
JSD = "https://data.jsdelivr.com/v1/packages"
ICONS = "https://cdn.jsdelivr.net/gh/iconify/icon-sets/json/{}.json"

# The matrix the skill recommends: legacy consumer brands + AI-era ones, since
# the young brands are what actually separates the sources.
DEFAULT_BRANDS = ["github", "youtube", "google", "microsoft", "figma", "slack",
                  "docker", "spotify", "netflix", "vercel", "windsurf", "openai"]

# Proper nouns for the Commons title search, which is case/prefix sensitive.
LABELS = {"github": "GitHub", "youtube": "YouTube", "google": "Google",
          "microsoft": "Microsoft", "figma": "Figma", "slack": "Slack",
          "docker": "Docker", "spotify": "Spotify", "netflix": "Netflix",
          "vercel": "Vercel", "windsurf": "Windsurf", "openai": "OpenAI"}

# Domain-keyed APIs look a brand up by domain, not by slug.
DOMAINS = {"github": ["github.com"], "youtube": ["youtube.com"],
           "google": ["google.com"], "microsoft": ["microsoft.com"],
           "figma": ["figma.com"], "slack": ["slack.com"],
           "docker": ["docker.com"], "spotify": ["spotify.com"],
           "netflix": ["netflix.com"], "vercel": ["vercel.com"],
           "windsurf": ["windsurf.com", "windsurf.art", "codeium.com"],
           "openai": ["openai.com"], "notion": ["notion.so"],
           "anthropic": ["anthropic.com"], "stripe": ["stripe.com"],
           "whatsapp": ["whatsapp.com"], "instagram": ["instagram.com"],
           "supabase": ["supabase.com"], "react": ["reactjs.org"],
           "twitch": ["twitch.tv"], "apple": ["apple.com"], "aws": ["aws.amazon.com"],
           "cursor": ["cursor.com"], "huggingface": ["huggingface.co"],
           "ollama": ["ollama.com"]}

# resolver: ("npm", pkg) | ("gh", "owner/repo", ref, "dir") | ("iconify", set)
#           ("commons",) | ("none",)          -- template placeholder: <slug>|<domain>|<file>
PROVIDERS: dict[str, dict] = {
    "simple-icons": dict(resolver=("npm", "simple-icons"),
                         template="https://cdn.jsdelivr.net/npm/simple-icons@{ver}/icons/{slug}.svg",
                         variants=["{b}"], note="CC0 mono"),
    "svg-logos-gilbarbara": dict(resolver=("gh", "gilbarbara/logos", "main", "logos"),
                                 template="https://raw.githubusercontent.com/gilbarbara/logos/main/logos/{slug}.svg",
                                 variants=["{b}", "{b}-icon"], note="official artwork, colour"),
    "vectorlogo-zone": dict(resolver=("none",),
                            template="https://www.vectorlogo.zone/logos/{b}/{slug}.svg",
                            variants=["{b}-icon", "{b}-ar21", "{b}"],
                            aliases={"react": "reactjs"}, note="press-kit vectors; froze ~2021; many files lack viewBox"),
    "worldvectorlogo": dict(resolver=("none",),
                            template="https://cdn.worldvectorlogo.com/logos/{slug}.svg",
                            variants=["{b}", "{b}-1", "{b}-2", "{b}-3", "{b}-4"],
                            note="no public slug index (Cloudflare) -- enumerate suffixes"),
    "logotypes-repo": dict(resolver=("gh", "yceballost/logotypes", "main", "static/logos"),
                           template="https://raw.githubusercontent.com/yceballost/logotypes/main/static/logos/{slug}.svg",
                           variants=["{b}-glyph-color", "{b}-wordmark-color", "{b}-glyph-black"],
                           note="hosted API dead (402); repo only"),
    "thesvg-color": dict(resolver=("iconify", "thesvg-color"),
                         template="https://api.iconify.design/thesvg-color/{slug}.svg",
                         variants=["{b}", "{b}-dark", "{b}-light"],
                         delay=2.5, note="colour; bare names 404 for ~1/3 of brands"),
    "iconify-simple-icons": dict(resolver=("iconify", "simple-icons"),
                                 template="https://api.iconify.design/simple-icons/{slug}.svg",
                                 variants=["{b}"], delay=2.5, note="copy of simple-icons upstream"),
    "iconify-logos": dict(resolver=("iconify", "logos"),
                          template="https://api.iconify.design/logos/{slug}.svg",
                          variants=["{b}", "{b}-light", "{b}-dark"], delay=2.5,
                          note="copy of gilbarbara upstream"),
    "iconify-cib": dict(resolver=("iconify", "cib"),
                        template="https://api.iconify.design/cib/{slug}.svg",
                        variants=["{b}"], delay=2.5,
                        note="set prefix stripped: cib/github, never cib/cib-github"),
    "lobehub-svg": dict(resolver=("npm", "@lobehub/icons-static-svg"),
                        template="https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@{ver}/icons/{slug}.svg",
                        variants=["{b}", "{b}-color"],
                        note="best AI-era coverage; jsDelivr flat listing returns 0 files here"),
    "lobehub-png": dict(resolver=("npm", "@lobehub/icons-static-png"),
                        template="https://cdn.jsdelivr.net/npm/@lobehub/icons-static-png@{ver}/light/{slug}.png",
                        variants=["{b}"],
                        note="the only real raster tier (640x640)"),
    "devicon": dict(resolver=("npm", "devicon"),
                    template="https://cdn.jsdelivr.net/npm/devicon@{ver}/icons/{b}/{slug}.svg",
                    variants=["{b}-original", "{b}-plain"],
                    note="dev-tool brands only; colour official"),
    "remix": dict(resolver=("npm", "remixicon"),
                  template="https://cdn.jsdelivr.net/npm/remixicon@{ver}/icons/Logos/{slug}.svg",
                  variants=["{b}-fill", "{b}-line"],
                  note="suffix mandatory; folder is capital-L Logos"),
    "tabler": dict(resolver=("npm", "@tabler/icons"),
                   template="https://cdn.jsdelivr.net/npm/@tabler/icons@{ver}/icons/outline/{slug}.svg",
                   variants=["brand-{b}"], note="stroke glyphs; microsoft only as brand-windows"),
    "fontawesome-brands": dict(resolver=("npm", "@fortawesome/fontawesome-free"),
                               template="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@{ver}/svgs/brands/{slug}.svg",
                               variants=["{b}"], note="CC BY 4.0 -- attribution required"),
    "boxicons": dict(resolver=("npm", "boxicons"),
                     template="https://cdn.jsdelivr.net/npm/boxicons@{ver}/svg/logos/{slug}.svg",
                     variants=["bxl-{b}"], note="frozen at 2.x (2020-era coverage)"),
    "wikimedia-commons": dict(resolver=("commons",),
                              template="https://commons.wikimedia.org/wiki/Special:FilePath/{file}",
                              variants=["{b}"], delay=1.6,
                              note="often historical revisions; verify the returned title"),
    "google-favicons": dict(resolver=("none",), kind="domain",
                            template="https://www.google.com/s2/favicons?domain={domain}&sz=256",
                            note="ask sz=256: 144/192/384/512 regress to a 16x16 stub"),
    "icon-horse": dict(resolver=("none",), kind="domain",
                       template="https://icon.horse/icon/{domain}",
                       note="403 without a browser UA"),
    "duckduckgo-ip3": dict(resolver=("none",), kind="domain",
                           template="https://icons.duckduckgo.com/ip3/{domain}.ico",
                           note="ICOs pack several sizes; Content-Length understates"),
    "unavatar": dict(resolver=("none",), kind="domain",
                     template="https://unavatar.io/{domain}?fallback=false",
                     delay=6.0, note="only keyless vector route; 429s fast; fallback=false is mandatory"),
}


def http(url: str, tries: int = 3, cap: int = 2_000_000) -> tuple[int, str, bytes]:
    """GET with backoff on 429/5xx only. Returns (status, content_type, body).

    `cap` matters: index files are many MB, and a too-small read silently
    truncates them -- the JSON then fails to parse and every brand looks absent.
    Asset probes keep the small cap; resolvers pass a big one.
    """
    last = (0, "", b"")
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.status, r.headers.get("Content-Type", "").lower(), r.read(cap)
        except urllib.error.HTTPError as e:
            last = (e.code, "", b"")
            if e.code < 500 and e.code != 429:
                return last
        except Exception as e:                       # noqa: BLE001 - report, don't crash
            last = (0, f"ERR {type(e).__name__}", b"")
        time.sleep(1.5 * (attempt + 1))
    return last


INDEX_CAP = 80_000_000


def magic(buf: bytes) -> str:
    """Image class from bytes; a valid SVG can begin with a UTF-8 BOM."""
    b = buf.lstrip(b"\xef\xbb\xbf")
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    if b[:3] == b"\xff\xd8\xff":
        return "jpeg"
    if b[:4] == b"RIFF" and b[8:12] == b"WEBP":
        return "webp"
    if b[:4] == b"\x00\x00\x01\x00":
        return "ico"
    if b[:4] == b"<svg" or b[:5] == b"<?xml" or b[:1] == b"<":
        return "svg" if b"<svg" in buf[:4096] else "unknown"
    return "unknown"


def png_dims(buf: bytes) -> str:
    return "%dx%d" % struct.unpack(">II", buf[16:24]) if buf[:8] == b"\x89PNG\r\n\x1a\n" else ""


def svg_facts(buf: bytes) -> str:
    t = buf.decode("utf-8", "replace")
    fills = len(set(re.findall(r'fill\s*=\s*"(?:#|rgb)', t)))
    parts = [f"paths={t.count('<path')}", f"fills={fills}"]
    if "<image" in t:
        parts.append("RASTER-IN-SVG")
    if "viewBox" not in t:
        parts.append("no-viewBox")
    return " ".join(parts)


# --- name resolution ---------------------------------------------------------

def npm_names(pkg: str) -> tuple[str, list[str]]:
    """(resolved latest version, stems of the files the package ships).

    Pin the version in the URL: jsDelivr's versionless path serves a STALE cached
    release, and will happily 200 a file the current release deleted (measured:
    simple-icons@16.32.0 404s openai/slack/microsoft, but
    .../npm/simple-icons/icons/openai.svg returns 200 with 1570 B from <=v15).
    """
    _st, _ct, body = http(f"{JSD}/npm/{pkg}", cap=INDEX_CAP)
    try:
        ver = json.loads(body)["tags"]["latest"]
    except Exception:
        return "", []
    _st, _ct, body = http(f"{JSD}/npm/{pkg}@{ver}?structure=flat", cap=INDEX_CAP)
    try:
        files = json.loads(body).get("files", [])
    except Exception:
        return ver, []
    if not files:                       # some packages answer the flat form empty
        _st, _ct, body = http(f"{JSD}/npm/{pkg}@{ver}", cap=INDEX_CAP)
        def walk(node):
            for f in node.get("files", []):
                if f["type"] == "directory":
                    yield from walk(f)
                else:
                    yield f["name"]
        files = [{"name": n} for n in walk(json.loads(body))]
    return ver, sorted({re.sub(r"\.(svg|png)$", "", f["name"].rsplit("/", 1)[-1])
                        for f in files if f["name"].endswith((".svg", ".png"))})


def gh_names(repo: str, ref: str, subdir: str) -> list[str]:
    _st, _ct, body = http(f"{JSD}/gh/{repo}@{ref}?structure=flat", cap=INDEX_CAP)
    try:
        files = json.loads(body).get("files", [])
    except Exception:
        return []
    pre = "/" + subdir.strip("/") + "/"
    return sorted({f["name"][len(pre):].rsplit(".", 1)[0] for f in files
                   if f["name"].startswith(pre) and f["name"].endswith(".svg")})


def iconify_names(set_name: str) -> list[str]:
    _st, _ct, body = http(ICONS.format(set_name), cap=INDEX_CAP)
    try:
        return sorted(json.loads(body)["icons"])
    except Exception:
        return []


def commons_file(brand: str) -> str:
    """Resolve a real File: name through the MediaWiki API -- never guess one.
    Miser Mode answers a disabled param as 200 + {"error":...}, so parse it."""
    prefix = urllib.parse.quote(f"{LABELS.get(brand, brand.capitalize())} logo")
    url = ("https://commons.wikimedia.org/w/api.php?action=query&format=json"
           f"&list=allimages&aiprefix={prefix}&ailimit=30")
    _st, _ct, body = http(url)
    try:
        images = json.loads(body)["query"]["allimages"]
    except Exception:
        return ""
    word = re.compile(rf"\b{re.escape(LABELS.get(brand, brand))}\b", re.I)
    for img in images:                                     # first that is really the brand
        title = img["title"]
        if word.search(title) and not re.search(r"windsurfing|facebook|wordmark map", title, re.I):
            return title.replace("File:", "")
    return ""


def resolve_names(prov: dict) -> tuple[str, list[str]]:
    """(pinned version, index names). Empty version = nothing to pin."""
    kind = prov["resolver"][0]
    if kind == "npm":
        return npm_names(prov["resolver"][1])
    if kind == "gh":
        return "", gh_names(prov["resolver"][1], prov["resolver"][2], prov["resolver"][3])
    if kind == "iconify":
        return "", iconify_names(prov["resolver"][1])
    return "", []


def candidates(prov: dict, brand: str, names: list[str], allow_derived: bool) -> list[tuple[str, bool]]:
    """(slug, exact) pairs to try, ordered. Derived = longer name that merely
    starts with the brand (github-actions for github) and is a different mark."""
    b = prov.get("aliases", {}).get(brand, brand)
    order: list[str] = []
    flags: dict[str, bool] = {}

    def add(slug: str, exact: bool) -> None:
        if slug not in flags:
            order.append(slug)
        flags[slug] = flags.get(slug, False) or exact   # exact wins over derived

    for pat in prov.get("variants", ["{b}"]):
        slug = pat.format(b=b)
        exact = not names or slug in names
        if exact:
            add(slug, True)
        if allow_derived and names:
            for derived in [n for n in names if n.startswith(slug + "-")][:3]:
                add(derived, False)          # neighbour mark, not the brand
    return [(s, flags[s]) for s in order]


def probe(prov: dict, brand: str, names: list[str], allow_derived: bool, ver: str = "") -> dict:
    kind = prov.get("kind", "slug")
    tried: list[tuple[str, bool]] = []
    if kind == "domain":
        domains = DOMAINS.get(brand, [f"{brand}.com"])
        slots = [(d, True) for d in domains]
    elif prov["resolver"][0] == "commons":
        slots = [(commons_file(brand), True)]
    else:
        slots = candidates(prov, brand, names, allow_derived)
    base = prov.get("aliases", {}).get(brand, brand)
    for slug, exact in slots:
        if not slug:
            continue
        tried.append((slug, exact))
        if kind == "domain":
            url = prov["template"].format(domain=slug, b=slug, slug=slug, ver=ver)
        else:
            quoted = urllib.parse.quote(slug, safe=".-")
            url = prov["template"].format(domain=quoted, b=base, slug=quoted, file=quoted, ver=ver)
        st, ct, buf = http(url)
        k = magic(buf)
        ok = k in ("svg", "png", "jpeg", "webp", "ico") and len(buf) > 96
        time.sleep(prov.get("delay", 0.25))
        if ok:
            return {"brand": brand, "url": url, "slug": slug, "exact": exact, "status": st,
                    "type": ct.split(";")[0], "kind": k, "bytes": len(buf),
                    "hash": hashlib.sha256(buf[:8192]).hexdigest()[:12],
                    "detail": svg_facts(buf) if k == "svg" else png_dims(buf), "tried": tried}
    return {"brand": brand, "ok": False, "status": tried[-1][0] if tried else "no-candidate",
            "url": "", "tried": tried, "exact": True}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="prove brand-logo sources with bytes + resolved slugs")
    ap.add_argument("-p", "--providers", default="", help="comma list; default = all")
    ap.add_argument("-b", "--brands", default=",".join(DEFAULT_BRANDS))
    ap.add_argument("--min", type=int, default=10, help="brands a source must serve (default 10)")
    ap.add_argument("--allow-derived", action="store_true",
                    help="also accept names that merely start with the brand (github-actions != github)")
    ap.add_argument("--json", help="write the full matrix to this file")
    ap.add_argument("--list-providers", action="store_true")
    a = ap.parse_args(argv)

    if a.list_providers:
        for name, p in sorted(PROVIDERS.items()):
            print(f"{name:22} {p.get('note', '')}")
        return 0

    brands = [b.strip() for b in a.brands.split(",") if b.strip()]
    picked = ([k for k in a.providers.split(",") if k.strip()] or list(PROVIDERS))
    unknown = [k for k in picked if k not in PROVIDERS]
    if unknown:
        print(f"unknown providers: {', '.join(unknown)}\ntry: --list-providers", file=sys.stderr)
        return 2

    print(f"matrix: {len(picked)} sources x {len(brands)} brands   "
          f"slug source = each provider's own manifest   min={a.min}\n")
    passed_any = 0
    report: dict[str, list] = {}
    for name in picked:
        prov = PROVIDERS[name]
        ver, names = resolve_names(prov)
        idx = "index ok" if names or prov["resolver"][0] in ("none", "commons") else "INDEX FAILED"
        print(f"## {name}  [{prov.get('note', '')}]  {idx}"
              + (f" ({len(names)} names)" if names else "")
              + (f"  PINNED @{ver}" if ver else ""))
        rows = []
        for brand in brands:
            r = probe(prov, brand, names, a.allow_derived, ver)
            rows.append(r)
            if r.get("url"):
                flag = "" if r.get("exact", True) else " [DERIVED-check-with-care]"
                print(f"   {'OK ' if r.get('slug') else 'BAD'} {r['status']:>3} {r.get('kind',''):4} "
                      f"{r.get('bytes', 0):>7}B {r.get('detail', '')[:34]:34} {brand} -> {r.get('slug', '')}{flag}")
            else:
                print(f"   BAD   -  --       -       brand absent ({brand}; tried "
                      f"{', '.join(t[0] for t in r['tried'][:3]) or 'nothing'})")
        good = [r for r in rows if r.get("url")]
        verdict = "COUNTS" if len(good) >= a.min else "does NOT count"
        passed_any += len(good) >= a.min
        dupes = len({r["hash"] for r in good}) < len(good)
        print(f"   -> {len(good)}/{len(brands)} brands  {verdict} (min {a.min})"
              + ("  !! STUB: same bytes for >1 brand" if dupes else "") + "\n")
        report[name] = rows
    print(f"{passed_any}/{len(picked)} sources reach {a.min}+ verified brands.")
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(report, fh, indent=1)
        print(f"wrote {a.json}")
    return 0 if passed_any == len(picked) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
