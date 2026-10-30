#!/usr/bin/env python3
"""revoke.py - mechanical help for revoking identifying data from an artifact.

Two commands, no third-party dependencies, ASCII output.

  python scripts/revoke.py scan FILE                 find candidate specific data (advisory inventory)
  python scripts/revoke.py verify --map MAP --out F   prove nothing survived, and nothing was broken
  python scripts/revoke.py                            self-test over 9 fixtures

Exit codes: 0 clean, 1 findings, 2 usage or read error.

MAP file - one substitution per line, `#` starts a comment, blank lines ignored:

  acme-corp        ->  [customer-1]        # pseudonymize: referenced 6 times, must stay distinct
  10.42.7.19       ->  [REDACTED-HOST]     # redact
  2025-03-03       ->  about two hours later

verify checks, in the order they bite:

  leak        an original token still appears in the output, including case, spacing and split variants
              (acme-corp / Acme Corp / ACME_CORP / acme.corp)
  fragment    a replacement still contains its original (or its first letters) - [acme-corp-redacted]
  collision   one placeholder used for two different originals - distinctness collapsed
  dup-map     one original mapped to two replacements - inconsistent
  mask        partial masks that reveal shape: a**@x.com, 555-***-4121, key prefixes
  secret      high-entropy or key-shaped strings left in the output
  map-inline  the substitution map itself embedded in the artifact - that is the re-identification key
  unused      a map entry never applied (a hint that the token was written differently)

scan is deliberately noisy: it proposes, you decide. verify is deliberate: it fails loudly.
"""
from __future__ import annotations

import math
import re
import sys
from collections import defaultdict

# ------------------------------------------------------------------ patterns

PATTERNS = [
    ("email",        r"[\w.%+-]+@[\w-]+\.[\w.-]{2,}"),
    ("url",          r"https?://[^\s)\]}'\"<>]+"),
    ("internal-dns", r"\b[\w-]+(?:\.[\w-]+)*\.(?:corp|internal|intranet|lan|local)\b"),
    ("ipv4",         r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    ("uuid",         r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"),
    ("priv-key",     r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    ("aws-key",      r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    ("gh-token",     r"\b(?:ghp|gho|github_pat)_[0-9A-Za-z_]{20,}\b"),
    ("jwt",          r"\beyJ[0-9A-Za-z_-]{8,}\.[0-9A-Za-z_-]{8,}\.[0-9A-Za-z_-]{4,}\b"),
    ("bearer",       r"(?i)\b(?:bearer|token|apikey|api_key|secret)\b[\"' :=,]{1,6}[0-9A-Za-z_\-]{12,}"),
    ("base64-long",  r"\b[0-9A-Za-z+/]{40,}={0,2}\b"),
    ("hex32",        r"\b[0-9a-fA-F]{32,}\b"),
    ("iso-datetime", r"\b\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2}(?::\d{2})?)?\b"),
    ("money",        r"(?<![\w.])[$€£]\s?\d{1,3}(?:[.,]\d{3})*(?:\.\d+)?\b"),
    ("phone",        r"\b\+?\d{1,3}[ .()-]?\(?\d{2,4}\)?[ .()-]?\d{3,4}[ .()-]?\d{0,4}\b"),
    ("abs-path",     r"(?:/home/|/Users/|[A-Za-z]:\\\\Users\\\\|/var/(?:www|log)/|/opt/)[\w./-]+"),
    ("ticket-id",    r"\b[A-Z][A-Z]{2,}-\d{2,6}\b"),
    ("slack-ws",     r"\bhttps?://[\w.-]*slack\.com/[\w/#-]+"),
]

HIGH_ENTROPY_MIN = 3.6   # bits/char; ordinary English sits near 3.0-3.3 for short tokens

SCAN_KINDS = {k: re.compile(p) for k, p in PATTERNS}
MASK_RE = re.compile(r"\w{1,3}\*{2,}|[(*]{3,}\d{2,}|\b[a-z0-9]{2,}(?:\.\.\.|…)\w{0,4}")


def entropy(token: str) -> float:
    counts = defaultdict(int)
    for ch in token:
        counts[ch] += 1
    n = len(token)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def secretish(token: str) -> bool:
    """Entropy alone fires on slugs, env-var names and our own [REDACTED-*] placeholders.

    A token counts as secret-shaped only if it mixes a digit with case or encoding symbols, or it is long
    enough that no human identifier reaches that length.
    """
    if "REDACTED" in token.upper() or "=" in token:
        return False
    if re.fullmatch(r"[A-Z][A-Z0-9_+/.-]{5,}", token):          # DATABASE_URL, INTERNAL-TOOL
        return False
    if re.fullmatch(r"[a-z0-9._/-]+", token) and not any(c.isdigit() for c in token):
        return False                                            # kebab slugs, hostnames, paths
    if re.search(r"\.(?:md|ya?ml|json|py|ts|tsx|js|go|rs|java|cs|sql|png|jpg|pdf|zip|sh)$", token):
        return False                                            # filenames and links, not secrets
    if len(token) >= 32:
        return True
    return any(c.isdigit() for c in token) and (any(c.isupper() for c in token)
                                                or any(c in "+=" for c in token))


def entropy_hits(text: str) -> list[str]:
    out = []
    for tok in re.findall(r"[0-9A-Za-z_\-+/=.]{16,}", text):
        if secretish(tok) and entropy(tok) >= HIGH_ENTROPY_MIN:
            out.append(tok)
    return out
    counts = defaultdict(int)
    for ch in token:
        counts[ch] += 1
    n = len(token)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


# ------------------------------------------------------------------ map handling

def load_map(text: str) -> list[tuple[str, str]]:
    pairs = []
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if "->" in line:
            a, b = line.split("->", 1)
        elif "\t" in line:
            a, b = line.split("\t", 1)
        else:
            raise ValueError("map line needs 'original -> replacement': %r" % raw)
        a, b = a.strip().strip("\"'"), b.strip().strip("\"'")
        if not a or not b:
            raise ValueError("empty side in map line: %r" % raw)
        pairs.append((a, b))
    return pairs


def variants(token: str) -> list[str]:
    """Case and separator forms a leaker would plausibly write."""
    core = re.split(r"[\s_.\-/]+", token.strip())
    core = [c for c in core if c]
    if not core:
        return []
    out: set[str] = set()
    joined = "".join(core)
    for word in (joined, joined.lower(), joined.upper(), joined.capitalize()):
        out.add(word)
    if len(core) > 1:
        low = [c.lower() for c in core]
        for sep in ("-", "_", " ", ".", "/"):
            out.add(sep.join(low))
            out.add(sep.join(w.capitalize() for w in low))
            out.add(sep.join(w.upper() for w in low))
    # leading fragment only when it is distinctive enough to identify
    if len(joined) >= 6:
        out.add(joined.lower()[: max(4, len(joined) // 2)])
    return sorted(x for x in out if len(x) >= 3)


# ------------------------------------------------------------------ scan

def scan(text: str) -> list[tuple[str, str]]:
    hits: dict[str, str] = {}
    for kind, rx in SCAN_KINDS.items():
        for m in rx.finditer(text):
            val = m.group(0)
            hits.setdefault(kind + ":" + val[:80], "%s  %s" % (kind, val[:80]))
    for tok in entropy_hits(text):
        hits.setdefault("entropy:" + tok[:60], "high-entropy  %s" % tok[:60])
    return sorted(hits.values())


# ------------------------------------------------------------------ verify

def verify(text: str, pairs: list[tuple[str, str]]) -> list[str]:
    findings: list[str] = []
    to_repl: dict[str, set[str]] = defaultdict(set)
    to_orig: dict[str, set[str]] = defaultdict(set)
    for orig, repl in pairs:
        to_repl[repl].add(orig.lower())
        to_orig[orig.lower()].add(repl)
    low = text.lower()

    for orig, repl in pairs:
        found = []
        for v in variants(orig) + [orig]:
            if v and v.lower() in low:
                found.append(v)
        if found:
            findings.append("leak: %r survives in the output as %r - apply it everywhere or widen the map"
                            % (orig, ", ".join(sorted(set(found))[:4])))
        if to_orig[orig.lower()] and len(to_orig[orig.lower()]) > 1:
            findings.append("dup-map: %r maps to %s - pick one" % (orig, sorted(to_orig[orig.lower()])))

    frags = {}
    for orig, _ in pairs:
        f = re.sub(r"[\s_.\-/]+", "", orig.lower())
        if len(f) >= 4:
            frags[f] = orig
    for token in re.findall(r"\[[^\]\n]{1,48}\]", text):
        norm = re.sub(r"[\s_.\-/\[\]]+", "", token.lower())
        for f, orig in frags.items():
            if f in norm:
                findings.append("fragment: placeholder %r still contains its original %r" % (token, orig))

    for repl, originals in to_repl.items():
        if len(originals) > 1:
            findings.append("collision: placeholder %r used for %s - distinct entities merged, causality dies"
                            % (repl, ", ".join(sorted(originals))))

    for m in MASK_RE.finditer(text):
        findings.append("mask: partial redaction %r reveals shape (length/domain/prefix)" % m.group(0)[:40])

    advisory = scan(text)
    for a in advisory:
        if a.startswith(("priv-key", "aws-key", "gh-token", "jwt", "bearer", "high-entropy",
                         "email", "internal-dns", "ipv4")):
            findings.append("secret: " + a)

    arrow = r"(?:->|=>|→|\bis read as\b|:|=)"
    for orig, repl in pairs:
        if re.search(re.escape(orig) + r"\s*" + arrow + r"\s*" + re.escape(repl), text, re.I) or \
           re.search(re.escape(repl) + r"\s*" + arrow + r"\s*" + re.escape(orig), text, re.I):
            findings.append("map-inline: %r -> %r appears inside the artifact - that is the "
                            "re-identification key; keep it with the source" % (orig, repl))

    for orig, repl in pairs:
        if not any(v.lower() in low for v in variants(orig) + [orig]) and repl not in text:
            findings.append("unused: %r -> %r applied nowhere - was the token spelled differently?"
                            % (orig, repl))
    return findings


# ------------------------------------------------------------------ cli

def read(path: str) -> str:
    return open(path, encoding="utf-8", errors="replace").read()


def main(argv: list[str]) -> int:
    if not argv:
        return selftest()
    cmd = argv[0]
    opts = {}
    rest = []
    i = 1
    while i < len(argv):
        a = argv[i]
        if a.startswith("--") and i + 1 < len(argv):
            opts[a[2:]] = argv[i + 1]
            i += 2
        else:
            rest.append(a)
            i += 1
    try:
        if cmd == "scan":
            if not rest:
                print("usage: revoke.py scan FILE")
                return 2
            text = read(rest[0])
            hits = scan(text)
            print("scan %s: %d candidate(s) - you decide which are specific" % (rest[0], len(hits)))
            for h in hits[:200]:
                print("  - %s" % h)
            if len(hits) > 200:
                print("  ... %d more" % (len(hits) - 200))
            return 1 if any(h.startswith(("priv-key", "aws-key", "gh-token", "jwt", "bearer", "high-entropy"))
                            for h in hits) else 0
        if cmd == "verify":
            if "map" not in opts or "out" not in opts:
                print("usage: revoke.py verify --map MAP --out SANITIZED")
                return 2
            pairs = load_map(read(opts["map"]))
            findings = verify(read(opts["out"]), pairs)
            print("verify %s: %d map entries, %d finding(s)" % (opts["out"], len(pairs), len(findings)))
            for f in findings:
                print("  - %s" % f)
            return 1 if findings else 0
    except FileNotFoundError as exc:
        print("error: %s" % exc)
        return 2
    except ValueError as exc:
        print("error: %s" % exc)
        return 2
    print("unknown command %r (scan | verify | self-test)" % cmd)
    return 2


# ------------------------------------------------------------------ self-test

SRC_ACME = """Postmortem: acme-corp checkout failed on 2025-03-03 02:14 UTC.
The orders-api host staging.acme-corp.internal (10.42.7.19) stalled behind postgres 14.9.
Contact Marta Nowak at m.nowak@acme-corp.com, key AKIA1234567890ABCDEF.
"""

CLEAN_OUT = """Postmortem: [customer-1] checkout failed about two hours later.
The [orders-service] host [REDACTED-HOST] stalled at [REDACTED-IP] behind a relational database.
Contact [customer-1-owner] at [REDACTED-EMAIL], credential [REDACTED-SECRET].
"""

MAP_OK = ("acme-corp -> [customer-1]\n"
          "staging.acme-corp.internal -> [REDACTED-HOST]\n"
          "10.42.7.19 -> [REDACTED-IP]\n"
          "m.nowak@acme-corp.com -> [REDACTED-EMAIL]\n"
          "AKIA1234567890ABCDEF -> [REDACTED-SECRET]\n")


def case(name, out, mp, expect):
    return (name, out, mp, expect)


FIXTURES = [
    case("clean", CLEAN_OUT, MAP_OK, []),
    case("token survives", CLEAN_OUT.replace("[customer-1]", "acme-corp"), MAP_OK, ["leak"]),
    case("case/split variant", "Notes from Acme Corp about the outage\n", MAP_OK, ["leak"]),
    case("replacement keeps fragment", "see [acme-corp-1] for details\n", MAP_OK, ["fragment"]),
    case("placeholder collision", "[service] called [service]\n",
         "orders-api -> [service]\ninvoices-api -> [service]\n", ["collision"]),
    case("one original two replacements", "x\n",
         "orders-api -> [service-a]\norders-api -> [service-b]\n", ["dup-map"]),
    case("partial mask", "mail a**@domain.com for the invoice\n", "acme-corp -> [customer-1]\n", ["mask"]),
    case("credential left behind", "rotate AKIA1234567890ABCDEF now\n", "acme-corp -> [customer-1]\n",
         ["secret"]),
    case("map written into the artifact", "[customer-1] (acme-corp -> [customer-1]) failed\n", MAP_OK,
         ["map-inline"]),
]


def selftest() -> int:
    bad = 0
    for name, out, mp, expect in FIXTURES:
        findings = verify(out, load_map(mp))
        joined = " | ".join(findings)
        caught = [e for e in expect if any(e in f for f in findings)]
        ok = (not findings) if not expect else len(caught) == len(expect)
        detail = "" if ok else "expected %s, got %s" % (expect, joined[:150] or "nothing")
        print("%-38s %s %s" % ("fixture " + name, "PASS" if ok else "FAIL", detail))
        bad += 0 if ok else 1
    src_hits = scan(SRC_ACME)
    kinds = {h.split(":")[0].split()[0] for h in src_hits}
    for must in ("email", "aws-key", "ipv4", "internal-dns"):
        ok = any(must in k for k in kinds)
        print("%-38s %s" % ("scan finds " + must, "PASS" if ok else "FAIL"))
        bad += 0 if ok else 1
    print("self-test: %d problems" % bad)
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
