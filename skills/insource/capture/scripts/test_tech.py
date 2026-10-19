"""Offline tests for evidence-based technology detection and the data-driven / structural heuristics.

  python test_tech.py        # exit 0 = all passed
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _cssparse as css  # noqa: E402
import _data  # noqa: E402
import _htmlpatterns as hp  # noqa: E402
import _techdetect as td  # noqa: E402
import _tokens  # noqa: E402
import website  # noqa: E402


def run_detect(html, headers=None, css_text="", banners=None, sigs=None):
    root, comments = hp.parse_html_full(html)
    return td.detect(root, comments, headers or {}, css_text, banners or [], "https://example.test/", sigs)


def names(t):
    return [i["name"] for i in t["identified"]]


def main() -> int:
    failures = []

    def check(name, cond):
        print(("ok   " if cond else "FAIL ") + name)
        if not cond:
            failures.append(name)

    # ---- a framework that appears in NO list: evidence must still surface ----
    zorb = ('<html><head><meta name="generator" content="Zorblax 9.1.3"><!-- Built with Zorblax 9.1.3 -->'
            '<script src="/zorblax/runtime-9f3ac1d2.js" type="module"></script>'
            '<script src="https://cdn.jsdelivr.net/npm/zorb-ui@4.2.0/dist/zorb.min.js"></script>'
            '<script id="__zorb_data__" type="application/json">{}</script><script>window.__ZORBLAX_STATE__ = {a:1};</script></head>'
            '<body><div data-zorb-island="x" zb-hydrate="1" class="zorb-3k2j1h card"><p zb-bind="a">hi</p></div></body></html>')
    hdr = {"x-powered-by": ["Zorblax-Server/2.0"], "set-cookie": ["zbsession=SECRETVALUE; Path=/; HttpOnly"], "server": ["nginx/1.25"], "x-request-id": ["r1"]}
    t = run_detect(zorb, hdr)
    check("unlisted framework is not falsely 'identified'", "Zorblax" not in names(t))
    check("unlisted: generator meta surfaced", t["generator"] == ["Zorblax 9.1.3"])
    check("unlisted: informative header surfaced, noise header dropped", "x-powered-by: Zorblax-Server/2.0" in t["headers"] and not any("x-request-id" in h for h in t["headers"]))
    check("unlisted: cookie NAME kept, VALUE never stored", t["cookie_names"] == ["zbsession"] and "SECRETVALUE" not in json.dumps(t))
    check("unlisted: package inferred from CDN URL", any(p["name"] == "zorb-ui" and p["version"] == "4.2.0" for p in t["packages"]))
    check("unlisted: attribute-prefix families", {"zb-", "data-zorb"} <= {p["prefix"] for p in t["attribute_prefixes"]})
    check("unlisted: generated class shape with prefix", any(g["shape"] == "name-hash" and g["prefixes"][0][0] == "zorb" for g in t["generated_classes"]))
    check("unlisted: window global, json id, comment", "__ZORBLAX_STATE__" in t["globals"] and "__zorb_data__" in t["json_script_ids"] and t["comments"])
    check("unlisted: content-hashed module script fingerprint", t["build"]["hashed_assets"] == 1 and t["build"]["module_scripts"] == 1)
    check("known server from header still attributed", "nginx" in names(t))

    # ---- names that the old hard-coded list never contained ----
    astro = run_detect('<meta name="generator" content="Astro v4.5.2"><astro-island uid="1"></astro-island><p data-astro-cid-abc123x>x</p>')
    check("Astro identified with version", [(i["name"], i["confidence"], i["version"]) for i in astro["identified"]][:1] == [("Astro", "high", "4.5.2")])
    check("Hugo identified with version", [(i["name"], i["version"]) for i in run_detect('<meta name="generator" content="Hugo 0.121.0">')["identified"]] == [("Hugo", "0.121.0")])
    check("Hono identified from header", "Hono" in names(run_detect("<p>x</p>", {"x-powered-by": ["Hono"]})))
    check("plain page: nothing claimed", run_detect("<html><body><p>hello</p></body></html>")["identified"] == [])
    check("URL signals ignore query strings (no false positive from ?placement=animejscom)",
          "anime.js" not in names(run_detect('<script src="https://cdn.ads.example/carbon.js?serve=X&placement=animejscom"></script>')))
    check("URL signals still match the path of a versioned file", "anime.js" in names(run_detect('<script src="/js/anime.min.js?v=3"></script>')))
    check("Tailwind from CSS custom properties", "Tailwind CSS" in names(run_detect("<p>x</p>", css_text="*{--tw-ring-color:#fff}")))
    check("Bootstrap from CSS banner", "Bootstrap" in names(run_detect("<p>x</p>", banners=[{"source": "b.css", "banner": "Bootstrap v5.3.0 (https://getbootstrap.com)"}])))

    # ---- user-extensible signatures ----
    sig_dir = tempfile.mkdtemp(prefix="sig-")
    f = os.path.join(sig_dir, "mine.json")
    json.dump({"signatures": [{"name": "Zorblax", "category": "meta-framework", "signals": [{"in": "meta_generator", "re": "^zorblax", "weight": "strong"}]}]}, open(f, "w"))
    t2 = run_detect(zorb, hdr, sigs=f)
    shutil.rmtree(sig_dir, ignore_errors=True)
    check("--signatures file adds a technology with version", any(i["name"] == "Zorblax" and i["version"] == "9.1.3" and i["confidence"] == "high" for i in t2["identified"]))

    # ---- headers ----
    raw = "HTTP/1.1 301 Moved\r\nLocation: /x\r\n\r\nHTTP/2 200\r\nServer: nginx\r\nSet-Cookie: sid=abc123; Path=/\r\nX-Vercel-Id: iad1::x\r\n\r\n"
    ph = td.parse_header_block(raw)
    check("header parser uses the final response after redirects", "location" not in ph and ph["server"] == ["nginx"])
    check("redaction removes cookie values, keeps names", "abc123" not in td.redact_headers(raw) and "sid=<redacted>" in td.redact_headers(raw))
    check("hosting attributed from headers", {"nginx", "Vercel"} <= set(names(run_detect("<p>x</p>", ph))))

    # ---- URL grammars ----
    def pk(u):
        return [(p["name"], p["version"]) for p in run_detect(f'<script src="{u}"></script>')["packages"]]
    check("CDN grammar: jsDelivr", pk("https://cdn.jsdelivr.net/npm/@scope/pkg@1.2.3/x.js") == [("@scope/pkg", "1.2.3")])
    check("CDN grammar: unpkg", pk("https://unpkg.com/react@18.2.0/umd/react.js") == [("react", "18.2.0")])
    check("CDN grammar: cdnjs", pk("https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js") == [("gsap", "3.12.5")])
    check("versioned filename grammar", pk("/assets/jquery-3.7.1.min.js") == [("jquery", "3.7.1")])
    gf = run_detect('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Open+Sans&display=swap">')
    check("font families from css2?family= URLs", gf["google_fonts"] == ["Inter", "Open Sans"])
    th = run_detect('<script src="https://static.hotjar.com/c/hotjar.js"></script><script src="https://cdn.example-cdn.io/a.js"></script>')
    check("third-party hosts flagged as tracker from data file", {h["host"]: h["tracker"] for h in th["third_party_hosts"]} == {"static.hotjar.com": True, "cdn.example-cdn.io": False})

    # ---- shape heuristics (no vocabulary) ----
    check("attr_prefix families", [td.attr_prefix(x) for x in ("hx-get", "wire:click", "data-astro-cid-x", "data-id", "aria-label", "onclick", "@click", "_ngcontent-abc", "href")]
          == ["hx-", "wire:", "data-astro", None, None, None, "@", "_ngcontent", None])
    check("class_shape flags generated names only", [td.class_shape(c) is not None for c in ("astro-3l2k1j", "svelte-1abcd2e", "btn-primary", "title2", "col-md6", "card__title")]
          == [True, True, False, False, False, False])

    # ---- data files ----
    check("data: full CSS named colour table", len(_data.load_json("css_named_colors.json")) >= 148 and "rebeccapurple" in _data.load_json("css_named_colors.json"))
    check("data: tracker list suffix match", _data.host_listed("static.hotjar.com", _data.load_lines("trackers.txt")) and not _data.host_listed("example.com", _data.load_lines("trackers.txt")))
    check("data: 'show more' phrases include Arabic, Spanish, Japanese", all(l in _data.load_json("more_phrases.json") for l in ("ar", "es", "ja")))

    # ---- website blocklist ----
    a = SimpleNamespace(no_default_blocklist=False, block=["ads.acme.io"])
    b = website.blocklist(a)
    u = lambda h: SimpleNamespace(hostname=h, netloc=h)
    check("website: default tracker blocked", not website.external_allowed(u("static.hotjar.com"), [], b))
    check("website: --block host (and subdomain) blocked", not website.external_allowed(u("x.ads.acme.io"), [], b))
    check("website: normal CDN allowed with --external", website.external_allowed(u("cdn.example.com"), [], b))
    check("website: --no-default-blocklist lifts defaults", website.external_allowed(u("static.hotjar.com"), [], website.blocklist(SimpleNamespace(no_default_blocklist=True, block=[]))))
    check("website: externals off unless requested", not website.external_allowed(u("cdn.example.com"), None, b))

    # ---- structural token heuristics ----
    tk = _tokens.analyze_tokens(css.parse_css("""
:root{--bg:#fff;--fg:#111;--accent:#06f;--space-tiny:2px;--space-small:4px;--space-big:16px;--font-body:"Tomato Sans",sans-serif;--font-code:Mono;--font-head:Serif}
.night{--bg:#000;--fg:#eee;--accent:#6af}
[data-mode=sepia]{--bg:#f4ecd8;--fg:#433;--accent:#a52}
@media (prefers-color-scheme:dark){:root{--bg:#111;--fg:#ddd;--accent:#8cf}}
@media (min-width:900px){:root{--space-big:24px}}
.a{color:rebeccapurple;background:tomato;font-family:Orange,Tomato;border:1px solid salmon}
.b{accent-color:teal;content:"red"}"""))
    sel = {s["selector"] for s in tk["themes"]["override_scopes"]}
    check("themes: detected by variable overlap, any name", {".night", "[data-mode=sepia]"} <= sel and tk["themes"]["override_scope_count"] == 3)
    check("themes: responsive root overrides are not themes", all("min-width" not in s["context"] for s in tk["themes"]["override_scopes"]))
    check("families: any shared prefix, any suffix", {f["family"] for f in tk["variables"]["scales"]} == {"--space", "--font"})
    check("families: size scale ordered by definition when suffixes are free-form", [m["name"] for m in next(f for f in tk["variables"]["scales"] if f["family"] == "--space")["members"]] == ["--space-tiny", "--space-small", "--space-big"])
    check("colours: names counted only in colour properties", {c["hex"] for c in tk["colors"]["in_use"]} == {"#663399", "#ff6347", "#fa8072", "#008080"})

    # ---- atomic-CSS measured from the stylesheet, not guessed from names ----
    atoms = "".join(f".u{i}{{padding:{i}px}}" for i in range(12))
    html = "".join(f'<div class="{" ".join(f"u{j}" for j in range(i, i + 4) if j < 12)}">x</div>' for i in range(0, 9))
    pat = hp.analyze_patterns(f"<body>{html}</body>", css.parse_css(atoms).rules)
    check("utility-first verdict comes from tiny rules, not class names", "utility-first" in pat["classes"]["verdict"] and pat["classes"]["utility_share"] >= 0.9)
    pat2 = hp.analyze_patterns("<body>" + html + "</body>", [])
    check("no stylesheet rules -> utility share unknown, no guess", pat2["classes"]["utility_share"] is None and "utility" not in pat2["classes"]["verdict"].split("(")[0])

    # ---- report renders, including the unknown-technology evidence ----
    md = hp.render_patterns_md(hp.analyze_patterns(zorb, [], "https://example.test/", headers=hdr), None, {"host": "example.test", "url": "https://example.test/"})
    check("report: Technology evidence section lists raw traces", "## Technology evidence" in md and "Zorblax 9.1.3" in md and "zorb-ui@4.2.0" in md and "SECRETVALUE" not in md)

    print(f"\n{'FAILED: ' + ', '.join(failures) if failures else 'all technology/heuristic tests passed'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
