#!/usr/bin/env python3
"""sweep.py - find every place a claim, term, or value may live. Read-only.

Merges two jobs that used to be separate tools:
  * surface sweep   - expands each term into the forms it takes in real repos
                      (identifier conventions + plurals, HTML entities, unicode/JSON
                      escapes, URL-encoding, curly quotes, Arabic/Persian digits,
                      flexible whitespace) and groups hits by surface type
                      (source, locale, docs, config, test, snapshot, history, ...).
  * footprint check - also reports file and directory NAMES containing the term,
                      hits hiding inside EXCLUDED dirs (vendor/build look-alikes),
                      and a loud warning when a search returns zero.

Usage:
  python sweep.py "Build faster" hero.title            # terms as positional args
  python sweep.py --term "order status" --root ./src    # or --term (repeatable)
  python sweep.py catalog --count                       # per-surface counts only
  python sweep.py catalog --files-only                  # just the file list
  python sweep.py catalog --json                        # machine-readable

Verification (after editing) - reconcile what remains against what the user approved:
  python sweep.py catalog --allow CHANGELOG.md --allow "docs/legacy/*" --allow vendor
  -> every remaining hit is labelled APPROVED or UNAPPROVED; exit code 1 if any
     UNAPPROVED remain. Pass the same --allow list you showed the user in the report.

Other flags:
  --skip-dir NAME      extra directory name to skip (repeatable; env SWEEP_EXCLUDE=a,b also works)
  --max-per-file N     lines shown per file (default 8)
  --no-excluded-scan   do not look inside skipped dirs for look-alikes

stdlib only. Counts are LINES, not occurrences. Text search cannot see images, PDFs,
CMS/database content or remote dashboards - the footer lists those blind spots.
Exit codes: 0 ran, 1 unapproved hits remain (only with --allow), 2 bad input.
"""
import argparse, bisect, fnmatch, html, json, os, re, sys, urllib.parse
from collections import defaultdict

# Directories that are noise most of the time. They are NOT hidden: hits inside them are
# summarised separately because vendored code is where unrelated look-alikes live.
SKIP_DIRS = {
    ".git", "node_modules", ".next", ".nuxt", ".turbo", ".svelte-kit", "dist", "build", "out",
    "coverage", ".cache", "venv", ".venv", "__pycache__", ".tox", ".mypy_cache", ".pytest_cache",
    "target", ".gradle", ".mvn", "bin", "obj", "vendor", "_build", "deps", "Pods", "DerivedData",
    ".build", ".dart_tool", ".stack-work", "dist-newstyle", ".terraform", ".idea", ".vscode",
}
NEVER_SCAN = {".git"}            # not even the excluded-dir look-alike scan
MAX_BYTES = 2_000_000
EXCLUDED_SCAN_FILE_CAP = 4000    # bound the look-alike scan so huge node_modules stay fast

# Order matters: first match wins.
CATEGORIES = [
    ("generated", r"(\.lock$|package-lock\.json$|pnpm-lock|yarn\.lock|\.min\.|\.map$|(^|/)(generated|__generated__|gen)/)"),
    ("history",   r"(changelog|changes\.md|history|release[-_ ]?notes|(^|/)migrations?/|(^|/)archive/|(^|/)adr/)"),
    ("snapshot",  r"(__snapshots__|\.snap$|\.approved\.)"),
    ("test",      r"((^|/)(tests?|__tests__|spec|e2e|cypress|playwright)/|\.(test|spec)\.|_test\.|Tests?\.)"),
    ("locale",    r"((^|/)(locales?|i18n|l10n|lang|languages|translations?|messages|intl)/|\.(po|pot|arb|xlf|xliff|strings|xcstrings|resx)$|(^|/)strings[^/]*\.xml$)"),
    ("ci",        r"((^|/)\.(github|gitlab|circleci)/|(^|/)(azure-pipelines|jenkinsfile|dockerfile))"),
    ("docs",      r"(\.(md|mdx|rst|adoc|txt)$|(^|/)docs?/)"),
    ("fixture",   r"((^|/)(seed|seeds|fixtures?|mocks?|__mocks__)/)"),
    ("style",     r"\.(css|scss|sass|less|styl)$"),
    ("config",    r"(\.(toml|ini|ya?ml|cfg|conf|plist)$|(^|/)\.env|package\.json$|manifest|app\.json|\.config\.)"),
    ("source",    r"\.(tsx?|jsx?|mjs|cjs|vue|svelte|astro|py|rb|go|rs|java|kt|swift|cs|php|dart|html?|sql|json|ex|exs|scala|c|cc|cpp|h|hpp)$"),
]
CATEGORIES = [(n, re.compile(p, re.I)) for n, p in CATEGORIES]

REVIEW_HINT = {
    "history":   "usually LEAVE (records of the past) - confirm",
    "generated": "do not hand-edit; fix the source and regenerate",
    "snapshot":  "regenerate with the test runner after the source change",
    "locale":    "UPDATE in every language - stale translations are misleading",
    "config":    "check for contracts (env vars, keys, flags) before editing",
    "test":      "update expected values; ASK if the test protects the old behavior",
}
# Suggested report bucket per surface (see assets/report-template.md). A hint, not a verdict:
# read the line before deciding. 'source' in particular can be Core, Internal or Contract.
BUCKET_HINT = {
    "source": "Core / Internal / Contract (read each)", "locale": "User-facing",
    "docs": "Docs", "config": "Internal or Contract", "style": "Internal",
    "test": "Verification", "snapshot": "Verification (regenerate)", "fixture": "Verification / seed data",
    "ci": "Internal (CI may assert text)", "generated": "Generated (regenerate)",
    "history": "Historical (likely leave)", "other": "Unclassified (read)",
}
ORDER = ["source", "locale", "docs", "config", "style", "test", "snapshot", "fixture",
         "ci", "generated", "history", "other"]


def categorize(rel):
    p = rel.replace(os.sep, "/")
    for name, rx in CATEGORIES:
        if rx.search(p):
            return name
    return "other"


# --------------------------------------------------------------------------- variants
def words(term):
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", term)
    return [w for w in re.split(r"[^0-9A-Za-z\u00C0-\uFFFF]+", spaced) if w]


def pluralize(w):
    lw = w.lower()
    if lw.endswith("ies"):
        return w                                   # already plural
    if lw.endswith(("ss", "us", "is")):
        return w + "es"                            # class, status, analysis (singular)
    if lw.endswith("s"):
        return w                                   # already plural
    if re.search(r"[^aeiou]y$", lw):
        return w[:-1] + "ies"
    if lw.endswith(("x", "z", "ch", "sh")):
        return w + "es"
    return w + "s"


def conventions(ws):
    """The spellings different ecosystems use for the same multi-word concept."""
    low = [w.lower() for w in ws]
    return {
        "kebab-case": "-".join(low),
        "snake_case": "_".join(low),
        "dot.case": ".".join(low),
        "camelCase": low[0] + "".join(w.capitalize() for w in low[1:]),
        "PascalCase": "".join(w.capitalize() for w in low),
        "CONSTANT_CASE": "_".join(w.upper() for w in ws),
        "Train-Case": "-".join(w.capitalize() for w in low),
        "flatcase": "".join(low),
        "spaced": " ".join(low),
    }


def variants(term):
    out = {"exact": term}
    ws = words(term)
    sentence_like = bool(re.search(r"[,;!?]", term))
    if 1 < len(ws) <= 6:
        out.update(conventions(ws))
    # plurals: identifiers and short concept names, not sentences
    if ws and len(ws) <= 3 and not sentence_like:
        last = pluralize(ws[-1])
        if last != ws[-1]:
            pws = ws[:-1] + [last]
            for label, text in conventions(pws).items() if len(pws) > 1 else \
                    {"snake_case": last.lower(), "PascalCase": last.capitalize(),
                     "CONSTANT_CASE": last.upper()}.items():
                out["plural " + label] = text
    # delimiter-joined fragments (CSS BEM block__element / block--modifier)
    if len(ws) >= 1 and not sentence_like and len(ws) <= 3:
        k = "-".join(w.lower() for w in ws)
        out["BEM __element"] = k + "__"
        out["BEM --modifier"] = k + "--"
    # encodings and typography
    esc = html.escape(term, quote=True)
    if esc != term:
        out["html-escaped"] = esc
    ent = term.encode("ascii", "xmlcharrefreplace").decode()
    if ent != term:
        out["html-entities"] = ent
    if any(ord(c) > 127 for c in term):
        out["\\u-escape"] = "".join(c if ord(c) < 128 else "\\u%04x" % ord(c) for c in term)
    js = json.dumps(term, ensure_ascii=False)[1:-1]
    if js != term:
        out["json-escaped"] = js
    for label, fn in (("url-encoded", urllib.parse.quote), ("url-plus", urllib.parse.quote_plus)):
        enc = fn(term)
        if enc != term:
            out[label] = enc
    if "'" in term:
        out["curly-apostrophe"] = term.replace("'", "\u2019")
    if "\u2019" in term:
        out["straight-apostrophe"] = term.replace("\u2019", "'")
    if '"' in term:
        out["curly-quotes"] = re.sub(r'"([^"]*)"', "\u201c\\1\u201d", term)
    if re.search(r"\d", term):
        out["arabic-indic-digits"] = term.translate(str.maketrans("0123456789", "\u0660\u0661\u0662\u0663\u0664\u0665\u0666\u0667\u0668\u0669"))
        out["persian-digits"] = term.translate(str.maketrans("0123456789", "\u06f0\u06f1\u06f2\u06f3\u06f4\u06f5\u06f6\u06f7\u06f8\u06f9"))
    return out


def compile_variants(term):
    """Labelled variant regexes (case-insensitive; the matched snippet shows real casing)
    plus a separator-tolerant catch-all for spellings nobody anticipated."""
    merged = {}                                          # lowercase text -> (text, [labels])
    for label, text in variants(term).items():
        key = text.lower()
        if not key:
            continue
        merged.setdefault(key, (text, []))[1].append(label)
    compiled = []
    for key, (text, labels) in merged.items():
        pat = re.escape(text).replace(r"\ ", r"\s+")      # tolerate line wraps / double spaces
        compiled.append(("/".join(labels), re.compile(pat, re.I)))
    ws = words(term)
    loose = None
    if len(ws) > 1 and not re.search(r"[,;!?]", term):
        loose = re.compile(r"[\s\-_.]*".join(re.escape(w) for w in ws), re.I)
    return compiled, loose, ws


def name_patterns(terms):
    """Substrings that make a file or directory NAME relevant."""
    pats = set()
    for t in terms:
        ws = words(t)
        if not ws:
            continue
        low = [w.lower() for w in ws]
        for sep in ("", "-", "_", "."):
            pats.add(sep.join(low))
        pats.add(t.lower())
        pats.add(ws[0].lower() + "".join(w.capitalize() for w in low[1:]))
        for w in (pluralize(low[-1]),):
            pats.add("-".join(low[:-1] + [w])); pats.add("_".join(low[:-1] + [w]))
    return {p for p in pats if len(p) >= 3}


# --------------------------------------------------------------------------- files
def looks_binary(fp):
    try:
        if os.path.getsize(fp) > MAX_BYTES:
            return True
        with open(fp, "rb") as f:
            return b"\0" in f.read(4096)
    except OSError:
        return True


def walk(root, skip):
    """Yield (kind, path): files/dirs in scope, plus ('excluded', dirpath) for skipped dirs."""
    for dp, dns, fns in os.walk(root):
        keep = []
        for d in dns:
            if d in skip:
                if d not in NEVER_SCAN:
                    yield "excluded", os.path.join(dp, d)
            else:
                keep.append(d)
                yield "dir", os.path.join(dp, d)
        dns[:] = keep
        for fn in fns:
            yield "file", os.path.join(dp, fn)


def read_text(fp):
    try:
        with open(fp, encoding="utf-8", errors="ignore") as f:
            return f.read()
    except OSError:
        return ""


def allowed(rel, allow):
    p = rel.replace(os.sep, "/")
    for pat in allow:
        pat = pat.replace(os.sep, "/").rstrip("/")
        if p == pat or fnmatch.fnmatch(p, pat) or p.startswith(pat + "/") or ("/" + pat + "/") in ("/" + p):
            return True
    return False


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("terms", nargs="*", help="old text / key / value / name (several allowed)")
    ap.add_argument("--term", action="append", default=[], help="same as a positional term (repeatable)")
    ap.add_argument("--root", default=".")
    ap.add_argument("--skip-dir", action="append", default=[])
    ap.add_argument("--max-per-file", type=int, default=8)
    ap.add_argument("--count", action="store_true", help="per-surface counts only, no hit lines")
    ap.add_argument("--files-only", action="store_true", help="list matching files only")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--allow", action="append", default=[],
                    help="path/glob the user approved to leave unchanged (repeatable); enables reconciliation")
    ap.add_argument("--no-excluded-scan", action="store_true")
    a = ap.parse_args()

    terms = list(a.terms) + list(a.term)
    if not terms:
        ap.error("give at least one term")
    if not os.path.isdir(a.root):
        print(f"error: path not found: {a.root}", file=sys.stderr)
        sys.exit(2)
    for t in terms:
        if not words(t) and not t.strip():
            print("error: empty term", file=sys.stderr); sys.exit(2)
        if len(t.strip()) < 4:
            print(f"warning: term {t!r} is very short - expect noisy hits; anchor it with context", file=sys.stderr)

    extra = [s for s in os.environ.get("SWEEP_EXCLUDE", "").split(",") if s]
    skip = SKIP_DIRS | set(a.skip_dir) | set(extra)
    plan = {t: compile_variants(t) for t in terms}
    name_pats = name_patterns(terms)

    hits = defaultdict(lambda: defaultdict(dict))     # category -> rel -> {line: record}
    file_names, dir_names, excluded_dirs = [], [], []
    scanned = 0

    for kind, path in walk(a.root, skip):
        rel = os.path.relpath(path, a.root)
        if kind == "excluded":
            excluded_dirs.append(path)
            continue
        base = os.path.basename(path).lower()
        if any(p in base for p in name_pats):
            (dir_names if kind == "dir" else file_names).append(rel)
        if kind != "file" or looks_binary(path):
            continue
        text = read_text(path)
        if not text:
            continue
        scanned += 1
        lines = text.splitlines()
        starts, pos = [], 0
        for ln in lines:
            starts.append(pos); pos += len(ln) + 1
        cat = categorize(rel)
        for term, (comp, loose, _ws) in plan.items():
            for label, rx in comp:
                for m in rx.finditer(text):
                    i = max(0, bisect.bisect_right(starts, m.start()) - 1)
                    rec = hits[cat][rel].setdefault(i + 1, {
                        "line": i + 1, "terms": set(), "forms": set(), "matched": [],
                        "text": lines[i].strip()[:160] if i < len(lines) else ""})
                    rec["terms"].add(term); rec["forms"].add(label)
                    snip = re.sub(r"\s+", " ", m.group(0))[:40]
                    if snip not in rec["matched"] and len(rec["matched"]) < 3:
                        rec["matched"].append(snip)
            if loose is not None:
                for m in loose.finditer(text):
                    i = max(0, bisect.bisect_right(starts, m.start()) - 1)
                    rec = hits[cat][rel].get(i + 1)
                    if rec is None:                 # only report loose hits no labelled form caught
                        rec = hits[cat][rel].setdefault(i + 1, {
                            "line": i + 1, "terms": set(), "forms": set(), "matched": [],
                            "text": lines[i].strip()[:160] if i < len(lines) else ""})
                        rec["forms"].add("loose"); rec["terms"].add(term)
                        snip = re.sub(r"\s+", " ", m.group(0))[:40]
                        if snip not in rec["matched"]:
                            rec["matched"].append(snip)

    # hits inside excluded directories (vendored / build output): count, never edit
    excluded_hits = {}
    if not a.no_excluded_scan:
        budget = EXCLUDED_SCAN_FILE_CAP
        rx_all = []
        for term, (comp, loose, _ws) in plan.items():
            rx_all.extend(rx for _l, rx in comp)
            if loose is not None:
                rx_all.append(loose)
        for ed in sorted(set(excluded_dirs)):
            n = 0
            for dp, dns, fns in os.walk(ed):
                dns[:] = [d for d in dns if d not in NEVER_SCAN]
                for fn in fns:
                    if budget <= 0:
                        break
                    fp = os.path.join(dp, fn)
                    if looks_binary(fp):
                        continue
                    budget -= 1
                    t = read_text(fp)
                    if t and any(rx.search(t) for rx in rx_all):
                        n += 1
            if n:
                excluded_hits[os.path.relpath(ed, a.root)] = n
        if budget <= 0:
            excluded_hits["(scan capped)"] = EXCLUDED_SCAN_FILE_CAP

    # flatten {line: record} -> sorted lists
    flat = {c: {rel: [dict(r, terms=sorted(r["terms"]), forms=sorted(r["forms"]))
                      for _, r in sorted(lines_.items())]
                for rel, lines_ in files.items()}
            for c, files in hits.items()}
    total = sum(len(v) for c in flat.values() for v in c.values())
    nfiles = sum(len(c) for c in flat.values())

    # reconciliation against the user-approved skip list
    unapproved = 0
    if a.allow:
        for cat, files in flat.items():
            for rel, hs in files.items():
                ok = allowed(rel, a.allow)
                for h in hs:
                    h["approved"] = ok
                    if not ok:
                        unapproved += 1

    if a.json:
        print(json.dumps({"hits": flat, "file_names": file_names, "dir_names": dir_names,
                          "excluded_dir_hits": excluded_hits, "total_hits": total,
                          "unapproved": unapproved if a.allow else None}, ensure_ascii=False, indent=2))
        sys.exit(1 if (a.allow and unapproved) else 0)

    print(f"# sweep: {total} hit line(s) in {nfiles} file(s)   ({scanned} text files scanned)")
    print(f"  terms: {', '.join(repr(t) for t in terms)}")
    print("  (counts are matching LINES, not occurrences; one line can hold several)\n")

    if a.files_only:
        for cat in ORDER:
            for rel in sorted(flat.get(cat, {})):
                print(f"{cat:10} {rel}")
    else:
        for cat in ORDER:
            if cat not in flat:
                continue
            n = sum(len(v) for v in flat[cat].values())
            hint = f"  <- {REVIEW_HINT[cat]}" if cat in REVIEW_HINT else ""
            print(f"## {cat} ({n} hits, {len(flat[cat])} files)  [bucket: {BUCKET_HINT[cat]}]{hint}")
            if a.count:
                print()
                continue
            for rel in sorted(flat[cat]):
                hs = flat[cat][rel]
                print(f"  {rel}")
                for h in hs[:a.max_per_file]:
                    tag = "+".join(h["forms"])
                    if len(terms) > 1:
                        tag += " | " + ", ".join(t if len(t) <= 24 else t[:21] + "..." for t in h["terms"])
                    mark = ""
                    if a.allow:
                        mark = " [APPROVED]" if h["approved"] else " [UNAPPROVED]"
                    m = ("«" + "», «".join(h["matched"]) + "» ") if h["matched"] else ""
                    print(f"    L{h['line']:<5} [{tag}]{mark} {m}{h['text']}")
                if len(hs) > a.max_per_file:
                    print(f"    ... +{len(hs) - a.max_per_file} more")
            print()

    print("-- File names containing the term")
    for n in sorted(file_names)[:30]:
        print("   " + n)
    if not file_names:
        print("   none")
    print("-- Directory names containing the term")
    for n in sorted(dir_names)[:30]:
        print("   " + n)
    if not dir_names:
        print("   none")

    print("\n-- Hits inside EXCLUDED directories (not counted above)")
    if excluded_hits:
        for d, n in sorted(excluded_hits.items()):
            if d == "(scan capped)":
                print(f"   scan stopped after {n} files; results above are partial")
            else:
                print(f"   {d:40} {n:5} file(s)  <- review: possible look-alike or generated output; do not edit")
    else:
        print("   none" if not a.no_excluded_scan else "   (skipped: --no-excluded-scan)")

    if total == 0 and not file_names and not dir_names:
        print("\n!! ZERO MATCHES. This does NOT prove nothing else needs changing. The phrase may not")
        print("!! match how the code spells it (e.g. 'max projects' will not match MAX_FREE_PROJECTS).")
        print("!! Try one distinctive word, the literal value, the identifier, or a related concept word.")

    if a.allow:
        approved = total - unapproved
        print(f"\n== Reconciliation vs approved skip list ({', '.join(a.allow)})")
        print(f"   approved remaining: {approved}")
        print(f"   UNAPPROVED remaining: {unapproved}")
        if unapproved:
            print("   Each unapproved hit is a MISS even if the visible UI already looks right:")
            print("   fix it and re-sweep, or stop and ask if it needs a decision you have not asked about.")

    print("\nBlind spots (text search cannot see these - check by reasoning):")
    print("  images / OG cards / PDFs with baked-in text, CMS or database content,")
    print("  remote dashboards (analytics, email templates, app-store listings),")
    print("  names built at runtime from parts, paraphrases that share no words with the old text.")
    sys.exit(1 if (a.allow and unapproved) else 0)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:          # e.g. `sweep.py ... | head`
        try:
            sys.stdout.close()
        finally:
            os._exit(0)
