#!/usr/bin/env python3
"""probe_registries.py - resolve CURRENT and STABLE package truth from public
registries and GitHub, stdlib only. Answers the question an agent must not
answer from training memory: "what version does this library actually ship today,
and is that the stable release?"

Layers this script covers (the agent covers the rest):
  1. Context7 or equivalent MCP  - agent tool call, optional, skip when down
  2. official registries         - npm/pypi/crates/go/nuget/rubygems/packagist
  3. GitHub                      - releases, tags, pushed_at, archived
  4. official docs / blogs       - WebFetch
  5. web search                  - WebSearch

Key rule: the registry "latest" DIST-TAG is not necessarily the latest STABLE -
tags can point at beta/rc/next. We read the full version list, filter prereleases
(npm -rc.1, PEP440 2.0b5, Go rc pseudo-versions, RubyGems .rc1, NuGet -preview,
composer beta, crates -rc), and rank real semver.

Usage:
  python scripts/probe_registries.py resolve <eco>:<name> [more...]   # full stable report
  python scripts/probe_registries.py <eco>:<name> [more...]           # compact one-line table
  ecologies: npm pypi github crates go nuget rubygems packagist

Examples:
  python scripts/probe_registries.py resolve npm:@ionic/core github:ionic-team/ionic-framework
"""
import gzip
import json
import re
import sys
import urllib.request

UA = {"User-Agent": "registry-probe"}
ELOS = ("npm", "pypi", "github", "crates", "go", "nuget", "rubygems", "packagist")


def _get(url, raw=False):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            data = gzip.decompress(data)
    return data.decode("utf-8", "replace") if raw else json.loads(data)


def _ver_key(v):
    """Sort key: numeric parts, then stable beats prerelease, then prerelease text."""
    m = re.match(r"^v?(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:\.(\d+))?(.*)$", v.strip())
    if not m:
        return ((-1,), 1, v)
    nums = tuple(int(x) for x in m.group(1, 2, 3, 4) if x is not None)
    rest = m.group(5).lower()
    stable = _is_stable(v)
    return (nums, 0 if stable else 1, rest)


def _is_stable(v):
    """No prerelease marker in any ecosystem dialect (build metadata +postN are stable)."""
    v = v.strip().lstrip("v")
    core = re.match(r"^\d+(\.\d+)*", v)
    rest = v[core.end():] if core else v
    rest = re.sub(r"^[+.](?:build.*)$", "", rest)          # +build / +incompatible handled by caller
    rest = re.sub(r"^\.post\d+$", "", rest)                  # python post-release = stable
    if v.endswith("+incompatible"):
        rest = v[:-len("+incompatible")]
        rest = re.sub(r"^-.*$", "", rest)
    return rest == ""


def registry_latest_stable(ecology, name, versions):
    """versions: iterable of (version_string, released_or_None). Returns dict."""
    pairs = list(versions)
    stable = [p for p in pairs if _is_stable(p[0])]
    all_sorted = sorted(pairs, key=lambda p: _ver_key(p[0]), reverse=True)
    stable_sorted = sorted(stable, key=lambda p: _ver_key(p[0]), reverse=True)
    return {"newest_any": all_sorted[0][0] if all_sorted else None,
            "newest_any_date": all_sorted[0][1] if all_sorted else None,
            "latest_stable": stable_sorted[0][0] if stable_sorted else None,
            "latest_stable_date": stable_sorted[0][1] if stable_sorted else None,
            "prerelease_is_newest": bool(all_sorted) and not _is_stable(all_sorted[0][0]),
            "recent": [(v, d) for v, d in all_sorted[:5]]}


# ---------------------------------------------------------------- registry layer

def npm(name):
    d = _get(f"https://registry.npmjs.org/{name}")
    tags = d.get("dist-tags", {})
    versions = list(d.get("versions", {}))
    latest_tag = tags.get("latest")
    dep = (d["versions"].get(latest_tag) or {}).get("deprecated") if latest_tag else None
    repo = ((d["versions"].get(latest_tag) or {}).get("repository") or {})
    r = registry_latest_stable("npm", name, [(v, d["time"].get(v)) for v in versions])
    r.update({"dist_tags": {k: v for k, v in tags.items() if k in ("latest", "next", "beta", "rc", "stable")},
              "deprecated": dep or False, "license": (d["versions"].get(latest_tag) or {}).get("license"),
              "repo": (repo.get("url") if isinstance(repo, dict) else repo) or
                      ((d.get("repository") or {}).get("url") if isinstance(d.get("repository"), dict) else d.get("repository"))})
    return r


def pypi(name):
    d = _get(f"https://pypi.org/pypi/{name}/json")
    releases = d.get("releases", {})
    versions = []
    for ver, files in releases.items():
        date = files[0]["upload_time"] if files else None
        if any(f.get("yanked") for f in files if isinstance(f, dict)):
            continue
        versions.append((ver, date))
    r = registry_latest_stable("pypi", name, versions)
    r.update({"dist_tags": {"latest-tag-doc": d["info"]["version"]},
              "deprecated": any(str(c).startswith("Private ::") for c in d["info"].get("classifiers", [])),
              "license": d["info"].get("license") or None,
              "repo": (d["info"].get("project_urls") or {}).get("Source")
                      or (d["info"].get("project_urls") or {}).get("Homepage")})
    return r


def crates(name):
    d = _get(f"https://crates.io/api/v1/crates/{name}")
    versions = [(v["num"], v["created_at"]) for v in d.get("versions", []) if not v.get("yanked")]
    r = registry_latest_stable("crates", name, versions)
    r.update({"dist_tags": {"newest": d["crate"]["newest_version"],
                            "max-stable": d["crate"]["max_stable_version"]},
              "deprecated": False, "license": None, "repo": d["crate"].get("repository")})
    return r


def go(module):
    lst = _get(f"https://proxy.golang.org/{module.lower()}/@v/list", raw=True)
    versions = [(v, None) for v in lst.split() if v]
    if not versions:  # tagless module: @latest may still answer with a pseudo-version
        d = _get(f"https://proxy.golang.org/{module.lower()}/@latest")
        versions = [(d["Version"], d["Time"])]
    r = registry_latest_stable("go", module, versions)
    r.update({"dist_tags": {}, "deprecated": False, "license": None,
              "repo": f"https://{module}" if module.startswith("github.com/") else None})
    return r


def nuget(name):
    idx = _get(f"https://api.nuget.org/v3/registration5-gz-semver2/{name.lower()}/index.json")
    versions = []
    for page in idx.get("items", []):
        leaves = page.get("items") or [page]
        for leaf in leaves:
            ce = leaf.get("catalogEntry")
            if ce is None and leaf.get("@id"):
                try:
                    ce = _get(leaf["@id"])
                except Exception:
                    continue
            if ce:
                versions.append((ce["version"], ce.get("published")))
    r = registry_latest_stable("nuget", name, versions)
    listed = [leaf for page in idx.get("items", []) for leaf in (page.get("items") or [page])][-1]
    r.update({"dist_tags": {}, "deprecated": bool(listed.get("deprecation")), "license": None, "repo": None})
    return r


def rubygems(name):
    versions = _get(f"https://rubygems.org/api/v1/versions/{name}.json")
    pairs = [(v["number"], v.get("created_at")) for v in versions if not v.get("yanked")]
    d = _get(f"https://rubygems.org/api/v1/gems/{name}.json")
    text = ((d.get("info") or "") + " " + (d.get("name") or "")).lower()
    r = registry_latest_stable("rubygems", name, pairs)
    r.update({"dist_tags": {"current": d["version"]}, "deprecated": "deprecat" in text,
              "license": d.get("license"), "repo": d.get("source_code_uri") or d.get("homepage_uri")})
    return r


def packagist(name):
    d = _get(f"https://repo.packagist.org/p2/{name}.json")
    entries = d["packages"][name]
    r = registry_latest_stable("packagist", name, [(e["version"], e.get("time")) for e in entries])
    r.update({"dist_tags": {}, "deprecated": bool(entries[0].get("abandoned")),
              "license": (entries[0].get("license") or [None])[0],
              "repo": entries[0].get("source", {}).get("url")})
    return r


REGISTRY = {"npm": npm, "pypi": pypi, "crates": crates, "go": go,
            "nuget": nuget, "rubygems": rubygems, "packagist": packagist}

# ------------------------------------------------------------------ github layer


def github(slug):
    repo = _get(f"https://api.github.com/repos/{slug}")
    versions = []
    try:
        for page in (1, 2):
            rel = _get(f"https://api.github.com/repos/{slug}/releases?per_page=100&page={page}")
            if not rel:
                break
            versions += [(x["tag_name"], x.get("published_at")) for x in rel
                         if not x.get("draft") and not x.get("prerelease")]
            if len(rel) < 100:
                break
    except Exception:
        pass
    if not versions:
        try:
            tags = _get(f"https://api.github.com/repos/{slug}/tags?per_page=100")
            versions = [(t["name"], None) for t in tags]
        except Exception:
            versions = []
    r = registry_latest_stable("github", slug, versions)
    r.update({"dist_tags": {}, "deprecated": repo["archived"],
              "license": (repo.get("license") or {}).get("spdx_id"),
              "repo": repo["html_url"], "pushed_at": repo["pushed_at"]})
    if repo.get("homepage"):
        r["homepage"] = repo["homepage"]
    return r


# ------------------------------------------------------------------------ CLI


def print_resolve(spec, r):
    eco, _, name = spec.partition(":")
    print(f"== {eco}:{name}")
    ls, lsd = r.get("latest_stable"), r.get("latest_stable_date")
    na, nad = r.get("newest_any"), r.get("newest_any_date")
    flag = "  <- PRERELEASE is newest; stable lags" if r.get("prerelease_is_newest") else ""
    print(f"   latest STABLE : {ls}  ({str(lsd)[:19]})")
    print(f"   newest release: {na}  ({str(nad)[:19]}){flag}")
    if r.get("dist_tags"):
        print(f"   dist tags     : {r['dist_tags']}")
    if r.get("pushed_at"):
        print(f"   last push     : {r['pushed_at'][:19]}")
    if r.get("deprecated"):
        print(f"   DEPRECATED    : {r['deprecated']}")
    print(f"   license       : {r.get('license') or '-'}  repo: {r.get('repo') or '-'}")
    if r.get("homepage"):
        print(f"   homepage      : {r['homepage']}")
    recent = ", ".join(f"{v}" for v, _ in r.get("recent", [])[:5])
    if recent:
        print(f"   recent        : {recent}")


def main(argv):
    args = argv[1:]
    if not args or "-h" in args or "--help" in args:
        print(__doc__)
        return 0
    resolve = args[0] == "resolve"
    specs = args[1:] if resolve else args
    failures = 0
    rows = []
    for spec in specs:
        eco, _, name = spec.partition(":")
        if eco == "github":
            fn = github
        elif eco in REGISTRY:
            fn = REGISTRY[eco]
        else:
            print(f"== {spec}\n   ERROR: unknown ecosystem (have: {', '.join(ELOS)})")
            failures += 1
            continue
        if not name:
            print(f"== {spec}\n   ERROR: missing package name")
            failures += 1
            continue
        try:
            r = fn(name)
        except Exception as e:
            print(f"== {spec}\n   ERROR: {type(e).__name__} {getattr(e, 'code', '')} {getattr(e, 'reason', e)}")
            failures += 1
            continue
        if resolve:
            print_resolve(spec, r)
        else:
            dep = r.get("deprecated")
            rows.append((eco, name, str(r.get("latest_stable") or "-"),
                         str(r.get("latest_stable_date") or "-")[:19],
                         "PRERELEASE-NEWEST" if r.get("prerelease_is_newest") else ("DEPRECATED" if dep else "alive")))
    if not resolve:
        head = ("eco", "package", "stable", "released", "status")
        ws = [max(len(str(x[i])) for x in (rows + [head])) for i in range(5)]
        for row in (head,) + tuple(rows):
            print("  ".join(str(c).ljust(w) for c, w in zip(row, ws)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
