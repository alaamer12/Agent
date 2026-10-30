#!/usr/bin/env python3
"""locale_parity.py - inspect JSON locale files (i18next / vue-i18n / next-intl style).

Layouts understood:   locales/<lang>.json      locales/<lang>/<namespace>.json
Nested keys are flattened to dotted keys; namespaced keys print as "ns:key".

Modes:
  --key hero.title           show that key's value in EVERY language (find gaps fast)
  --grep "old wording"       show every key whose value contains the text, in any language
  (default)                  parity report: missing / extra keys vs the reference language,
                             plus values identical to the reference (possibly untranslated)

Usage:
  python locale_parity.py --root src/locales [--ref en] [--key hero.title] [--grep TEXT]
Exit code 1 when keys are missing (usable in CI after an update).
"""
import argparse, json, os, re, sys
from collections import defaultdict

LANG = re.compile(r"^[A-Za-z]{2,3}([-_][A-Za-z0-9]{2,4})?$")


def flatten(d, prefix=""):
    if isinstance(d, dict):
        for k, v in d.items():
            yield from flatten(v, f"{prefix}.{k}" if prefix else str(k))
    else:
        yield prefix, d


def load(root):
    data = defaultdict(dict)  # lang -> key -> value
    root_name = os.path.basename(os.path.normpath(root))
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in {"node_modules", ".git"}]
        for fn in fns:
            if not fn.endswith(".json"):
                continue
            fp = os.path.join(dp, fn)
            stem, parent = fn[:-5], os.path.basename(dp)
            if LANG.match(parent) and parent != root_name:
                lang, ns = parent, stem
            elif LANG.match(stem):
                lang, ns = stem, ""
            else:
                continue
            try:
                with open(fp, encoding="utf-8") as f:
                    obj = json.load(f)
            except Exception as e:
                print(f"warning: cannot parse {fp}: {e}", file=sys.stderr)
                continue
            for k, v in flatten(obj):
                data[lang][f"{ns}:{k}" if ns else k] = v
    return data


def key_matches(k, wanted):
    return k == wanted or k.endswith(":" + wanted) or k.endswith("." + wanted)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True)
    ap.add_argument("--ref", help="reference language (default: the one with most keys)")
    ap.add_argument("--key")
    ap.add_argument("--grep")
    a = ap.parse_args()

    data = load(a.root)
    if not data:
        sys.exit("no locale JSON files found under " + a.root)
    langs = sorted(data)
    print(f"languages ({len(langs)}): {', '.join(langs)}\n")

    if a.key:
        for lang in langs:
            found = [(k, v) for k, v in sorted(data[lang].items()) if key_matches(k, a.key)]
            for k, v in found:
                print(f"{lang:8} {k} = {v!r}")
            if not found:
                print(f"{lang:8} (missing) {a.key}")
        return

    if a.grep:
        needle, n = a.grep.lower(), 0
        for lang in langs:
            for k, v in sorted(data[lang].items()):
                if isinstance(v, str) and needle in v.lower():
                    print(f"{lang:8} {k} = {v!r}")
                    n += 1
        print(f"\n{n} match(es)")
        return

    ref = a.ref or ("en" if "en" in data else max(langs, key=lambda l: len(data[l])))
    if ref not in data:
        sys.exit(f"reference language {ref!r} not found; have: {', '.join(langs)}")
    rk = set(data[ref])
    print(f"reference: {ref} ({len(rk)} keys)\n")
    bad = False
    for lang in langs:
        if lang == ref:
            continue
        keys = set(data[lang])
        miss, extra = sorted(rk - keys), sorted(keys - rk)
        same = sorted(k for k in rk & keys
                      if isinstance(data[ref][k], str) and data[lang][k] == data[ref][k]
                      and re.search(r"[A-Za-z]{4,}", data[ref][k]))
        status = "ok" if not (miss or extra or same) else "needs review"
        print(f"{lang}: {status}  (missing {len(miss)}, extra {len(extra)}, identical-to-{ref} {len(same)})")
        for label, lst in (("missing", miss), ("extra", extra), ("identical", same)):
            for k in lst[:15]:
                print(f"    {label:9} {k}")
            if len(lst) > 15:
                print(f"    {label:9} ... +{len(lst) - 15} more")
        bad = bad or bool(miss)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
