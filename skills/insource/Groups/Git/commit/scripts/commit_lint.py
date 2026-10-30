#!/usr/bin/env python3
"""commit_lint.py - lint a git commit message the way a reviewer plus a commit-msg hook would.

Usage:
  python scripts/commit_lint.py --file MSG        lint one message (as written with git commit -F MSG)
  python scripts/commit_lint.py --message "..."   lint a single-line or inline message
  python scripts/commit_lint.py --staged          scan the staged diff for secrets and junk
  python scripts/commit_lint.py --history [-n N] [--shared REF]   learn the repo style; flag
                                            staging vocabulary and duplicate messages
  python scripts/commit_lint.py                   self-test (14 fixtures, every defect must be caught)

Exit codes: 0 clean, 1 findings, 2 usage or read error. Output is ASCII-only (Windows consoles).

Findings:
  subject      length, imperative mood, trailing punctuation, vague verbs, empty, missing type/scope shape
  structure    missing blank line after the subject, body lines over 72 columns, tabs, CRLF, trailing space
  conventional unknown type, scope with a space, '!' without a BREAKING CHANGE footer, footer placement
  content      the subject names files instead of the change, a subject that asserts work no diff supports
  trailer      malformed Co-authored-by / Signed-off-by / Closes / Fixes / BREAKING CHANGE
  secret       key material, tokens, credential-bearing URLs or private IPs anywhere in the message
  junk         staged content that should not be committed: .env, key files, huge binaries, debug printers
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

TYPES = {"feat", "fix", "docs", "style", "refactor", "perf", "test", "build", "ci", "chore", "revert"}
SUBJECT_SOFT, SUBJECT_HARD, BODY_WRAP = 50, 72, 72

NON_IMPERATIVE = re.compile(
    r"^(?:"
    r"(?:add|fix|updat|remov|chang|implement|refactor|renam|delet|merge|revert|bump|improv|"
    r"optimi[sz]|clean|releas|includ|resolv|migrat|document|remov|replac|extract|guard|drop|"
    r"allow|reject|prevent|deprecat|enabl|disabl|test|cover|refactor|bump|us)ed"          # past tense
    r"|(?:add|fix|updat|remov|chang|implement|refactor|renam|delet|merg|revert|bump|improv|"
    r"optimi[sz]e?|clean|resolv|migrat|document|replac|extract|allow|reject|prevent|enabl|"
    r"disabl|cover|us(?:ing)?|mak|writ)(?:ing|s)\b"                                       # gerund / 3rd person
    r")[ :]", re.I)
VAGUE = re.compile(r"^(?:wip+|update[sd]?|fix(?:e[sd])? ?(?:bug|issue)?|bugs?|fixes|hotfix|"
                   r"patch(?:es)?|changes?|misc\.?|stuff|asdf|test(?:ing)?|temp|tweak|tweaks?|"
                   r"clean(?:up)?|improvement(?:s)?|minor|fixes|code|merge confict|new|"
                   r"update files?|some|various|comment[s]?|readme|first commit|initial(?: commit)?)$",
                   re.I)
FILE_NAMED = re.compile(r"\b\w+\.(?:ts|tsx|js|jsx|py|go|rs|java|cs|rb|php|c|h|cpp|vue|svelte|json|ya?ml|md)\b")
FOOTER_KEY = re.compile(r"^(?:Closes|Fixes|Resolves|Refs|See|Breaks|Docker-Tag|Change-Id|"
                        r"Co-authored-by|Co-developed-by|Signed-off-by|Reviewed-by|Acked-by|Tested-by|"
                        r"Reported-by|Issue|TODO|BREAKING CHANGE)\s*:", re.I)
PERSON_TRAILER = re.compile(r"^(?:Co-authored-by|Co-developed-by|Signed-off-by|Reviewed-by|Acked-by|"
                            r"Tested-by|Reported-by):\s+[^<@]+ <[^@<>@\s]+@[^@<>\s]+>\s*$", re.I)
ISSUE_TRAILER = re.compile(r"^(?:Closes|Fixes|Resolves|Refs|See):\s*\S+", re.I)
SECRET_PATTERNS = [
    ("private-key", r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    ("aws-key", r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    ("gh-token", r"\b(?:ghp|gho|github_pat)_[0-9A-Za-z_]{20,}\b"),
    ("jwt", r"\beyJ[0-9A-Za-z_-]{8,}\.[0-9A-Za-z_-]{8,}\.[0-9A-Za-z_-]{4,}\b"),
    ("cred-url", r"[a-zA-Z][a-zA-Z0-9+.-]*://[^/\s:]+:[^@\s/]{3,}@"),
    ("generic-secret", r"(?i)\b(?:api[_-]?key|secret|passwd|password|access[_-]?token)\b\s*[:=]\s*['\"]?[^\s'\"]{8,}"),
    ("slack-webhook", r"https://hooks\.slack\.com/services/[A-Za-z0-9/]+"),
]
JUNK_PATHS = re.compile(r"(^|/)\.env(\.|$)|(^|/)id_(?:rsa|ed25519)$|\.pem$|\.p12$|\.key$|node_modules/|"
                        r"(^|/)(?:dist|build|target|\.next|__pycache__)/|\.DS_Store$")
DEBUG_LEFTOVER = re.compile(r"^\+\s*(?:console\.log\(|print\(|fmt\.Print|dbg!\(|var_dump\(|debugger\b)", re.M)


def split_message(text: str) -> tuple[str, list[str], list[str]]:
    lines = [l.rstrip("\r") for l in text.strip("\ufeff").splitlines()]
    lines = [l for l in lines if not l.startswith("#")]          # git's comment lines, if a template leaked in
    if not lines:
        return "", [], []
    subject = lines[0]
    rest = lines[1:]
    body, footers = [], []
    # trailing contiguous trailer block, preceded by a blank line
    i = len(rest)
    while i > 0 and FOOTER_KEY.match(rest[i - 1].strip()):
        i -= 1
    if i < len(rest) and i > 0 and rest[i - 1].strip() == "":
        footers = [l.strip() for l in rest[i:]]
        body = rest[:i - 1]
    else:
        footers = [l.strip() for l in rest if FOOTER_KEY.match(l.strip()) and l.strip() not in body]
        body = [l for l in rest if not FOOTER_KEY.match(l.strip())]
    return subject, body, footers


def lint_message(text: str, style: dict | None = None) -> list[str]:
    f: list[str] = []
    subject, body, footers = split_message(text)
    if not text.strip():
        return ["subject: empty message"]
    if not subject.strip():
        f.append("subject: empty subject line")
    raw_first = text.strip().splitlines()[0]
    if raw_first.endswith("\r"):
        f.append("structure: CRLF line endings in the message - normalize to LF")
    if len(raw_first) != len(raw_first.rstrip()):
        f.append("structure: trailing whitespace on the subject")

    # ---- subject
    s = subject.strip()
    conv = re.match(r"^(?P<type>[a-z][a-z-]*)(?P<scope>\((?P<sc>[^()]*)\))?(?P<bang>!)?:\s?(?P<desc>.*)$", s)
    if conv:
        if conv.group("type") not in TYPES:
            f.append("conventional: unknown type %r (known: %s)" % (conv.group("type"), ", ".join(sorted(TYPES))))
        sc = conv.group("sc") or ""
        if sc and (" " in sc.strip() or len(sc.split()) > 2):
            f.append("conventional: scope %r is too long - a scope is one or two words naming the area" % sc)
        if s.lower().startswith(("fix:", "feat:", "refactor:")) and conv.group("scope") is None:
            pass
        if conv.group("bang") and not any(fl.upper().startswith("BREAKING CHANGE") for fl in footers):
            f.append("conventional: '!' marks a breaking change but no BREAKING CHANGE: footer explains it "
                     "- consumers read the footer, not the punctuation")
        desc = conv.group("desc")
        budget = SUBJECT_HARD
    else:
        desc, budget = s, SUBJECT_HARD
    if len(s) > SUBJECT_HARD:
        f.append("subject: %d characters - over the hard ceiling; the tail belongs in the body" % len(s))
    elif len(s) > SUBJECT_SOFT:
        f.append("subject: %d characters - above the 50-character budget (fine if the repo's own limit is "
                 "higher; state it in the lint config)" % len(s))
    if s.endswith((".", "!", "?", ":", ";")):
        f.append("subject: ends with punctuation - a summary line is not a sentence")
    if VAGUE.match(desc.strip() if desc else s):
        f.append("subject: vague - %r says nothing a reader can act on; name the change and the area" % s[:40])
    if NON_IMPERATIVE.match(desc.strip() if desc else s):
        f.append("subject: not imperative - complete this sentence instead: 'If applied, this commit will ___'")
    if s and s[0].isdigit():
        f.append("subject: starts with a number - a ticket key belongs in a trailer, not the summary")
    if style and style.get("casing") and desc:
        want = style["casing"]
        first = re.sub(r"^[^A-Za-z]+", "", desc)[:1]
        if first and ((want == "upper" and first.islower()) or (want == "lower" and first.isupper())):
            f.append("subject: %r casing does not match this repo's history (mostly %s-case)"
                     % (first, want))

    # ---- structure
    lines = [l for l in text.splitlines() if not l.startswith("#")]
    if len(lines) > 1 and lines[1].strip():
        f.append("structure: no blank line after the subject - tools read line 2 as part of the summary")
    for i, l in enumerate(body, start=3):
        if l.rstrip() != l:
            f.append("structure: line %d has trailing whitespace" % i)
        if "\t" in l:
            f.append("structure: line %d contains a tab" % i)
        if len(l) > BODY_WRAP + 8 and not l.lstrip().startswith(("```", "http")):
            f.append("structure: line %d is %d columns - wrap the body at %d" % (i, len(l), BODY_WRAP))
    if body and any(FILE_NAMED.search(l) and re.search(r"(?i)\b(?:changed|updated|modified|edited)\b", l)
                    for l in body):
        f.append("content: body restates the diff ('changed file.x') - say what is now true instead")
    if FILE_NAMED.search(s) and not conv:
        f.append("content: subject names a file rather than the change - the reader can see the filename in "
                 "the diff")
    joined = " ".join(body).lower()
    for claim in ("all tests pass", "tests pass", "builds clean", "no behavior change", "100% coverage"):
        if claim in joined and "not run" in joined:
            f.append("content: body both claims %r and says it was not run - pick the honest one" % claim)

    # ---- footers and trailers
    for fl in footers:
        if PERSON_TRAILER.match(fl) or ISSUE_TRAILER.match(fl):
            continue
        if re.match(r"^BREAKING CHANGE\s*:", fl, re.I):
            detail = fl.split(":", 1)[1].strip()
            if len(detail) < 15:
                f.append("trailer: BREAKING CHANGE needs an explanation a consumer can migrate from, not a "
                         "label")
            continue
        if FOOTER_KEY.match(fl):
            key = fl.split(":", 1)[0]
            if re.match(r"^(?:Co-authored-by|Signed-off-by|Reviewed-by|Acked-by|Tested-by|Reported-by|"
                        r"Co-developed-by)$", key, re.I):
                f.append("trailer: %r is malformed - expected 'Name <email@domain>'" % fl[:50])
            elif not fl.split(":", 1)[1].strip():
                f.append("trailer: %r has an empty value" % key)
    if any(re.match(r"^(?:Closes|Fixes|Resolves): ?#?\d+", fl) for fl in footers) and s:
        if re.search(r"(?:#|APP-|ISSUE-)\d+", s):
            f.append("trailer: issue reference is in both the subject and the footer - keep the subject "
                     "readable and let the trailer link")
    body_all = "\n".join(body)
    if "BREAKING CHANGE:" in body_all and not footers:
        f.append("conventional: BREAKING CHANGE written in the body - generators read it as a footer after a "
                 "blank line")
    for kw in ("cve-", "deprecat", "migrat", "revert"):
        if kw in s.lower() and not body:
            f.append("content: %r in the subject with no body - this is the kind of change a reader needs "
                     "the reason for" % kw)
            break

    # ---- secrets in the message
    for name, pat in SECRET_PATTERNS:
        if re.search(pat, text):
            f.append("secret: %s pattern in the commit message - it is copied into every clone and often a "
                     "public mirror; rotate the value, do not just reword" % name)
    return f


# ------------------------------------------------------------------ staged diff

def git(args: list[str]) -> str:
    r = subprocess.run(["git"] + args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout if r.returncode == 0 else ""


def scan_staged() -> tuple[list[str], str]:
    diff = git(["diff", "--cached", "--unified=0"])
    names = git(["diff", "--cached", "--name-only"]).split()
    findings: list[str] = []
    if not names:
        return ["junk: nothing staged - nothing to check (run git add <paths> first)"], ""
    for n in names:
        if JUNK_PATHS.search(n.replace("\\", "/")):
            findings.append("junk: %r looks like an env file, key, cache or build artifact - confirm it "
                            "belongs in history" % n)
        if os.path.exists(n) and os.path.getsize(n) > 2_000_000:
            findings.append("junk: %r is %.1f MB - large binaries need LFS or an artifact store"
                            % (n, os.path.getsize(n) / 1e6))
    for name, pat in SECRET_PATTERNS:
        added = "".join(l[1:] + "\n" for l in diff.splitlines() if l.startswith("+"))
        if re.search(pat, added):
            findings.append("secret: staged additions contain a %s pattern - unstage and rotate" % name)
    added_lines = "\n".join(l for l in diff.splitlines() if l.startswith("+"))
    for m in DEBUG_LEFTOVER.finditer(added_lines):
        findings.append("junk: debug leftover staged: %s" % m.group(0).strip()[:70])
        break
    return findings, "\n".join(names)


# ------------------------------------------------------------------ history

STAGING_PREFIX = re.compile(r"^\s*(?:wip-fix|wip|temp|debug|try|checkpoint|save)\b", re.I)


def audit_subjects(subjects: list[str]) -> tuple[dict, list[str], list[str]]:
    """Pure: given commit subjects, learn the repo's style and report what should not be there."""
    if not subjects:
        return {}, ["history: no commits to read (fresh repo, or not inside a working tree)"], []
    clean = [" ".join(s.split()) for s in subjects]
    conv = sum(1 for s in clean if re.match(r"^[a-z][a-z-]*(\([^)]*\))?!?:", s))
    upper = sum(1 for s in clean if re.sub(r"^[^A-Za-z]+", "", s)[:1].isupper())
    lower = sum(1 for s in clean if re.sub(r"^[^A-Za-z]+", "", s)[:1].islower())
    longish = sum(1 for s in clean if len(s) > SUBJECT_SOFT)
    style = {
        "conventional": conv >= max(1, len(clean) // 2),
        "casing": "upper" if upper > lower else "lower" if lower else None,
        "subject_soft": SUBJECT_HARD if longish > len(clean) * 0.6 else SUBJECT_SOFT,
    }
    notes = ["style: %d/%d conventional, mostly %s-case - follow the repo, not an imported format"
             % (conv, len(clean), style["casing"] or "mixed")]
    findings: list[str] = []

    for s in clean:
        if STAGING_PREFIX.match(s):
            findings.append("staging: %r is checkpoint vocabulary - fine while developing, and a policy "
                            "violation once it is on a shared branch (squash, drop, or reword)" % s[:60])
    counts: dict[str, int] = {}
    for s in clean:
        counts[s] = counts.get(s, 0) + 1
    for s, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        if n > 1:
            findings.append("duplicate: %r appears %d times - duplicate fixes are acceptable, duplicate "
                            "messages are not: which one is the real change?" % (s[:60], n))

    outliers = []
    for s in clean:
        why = []
        if len(s) > SUBJECT_HARD:
            why.append("%d chars" % len(s))
        if VAGUE.match(s.strip()) or (style["conventional"] and re.match(r"^[a-z][a-z-]*(\([^)]*\))?!?: ?$", s)):
            why.append("vague")
        if NON_IMPERATIVE.match(re.sub(r"^[a-z][a-z-]*(\([^)]*\))?!?: ?", "", s)):
            why.append("not imperative")
        if why:
            outliers.append("%s  (%s)" % (s[:60], ", ".join(why)))
    seen, uniq = set(), []
    for o in outliers:
        if o not in seen:
            seen.add(o)
            uniq.append(o)
    if uniq:
        notes.append("outliers in recent history:")
        notes += ["  - " + o for o in uniq[:10]]
    return style, notes, findings


def history_style(n: int = 25, shared: str | None = None) -> tuple[dict, list[str], list[str]]:
    spec = ["log", "-n", str(n), "--format=%s"] + ([shared] if shared else [])
    raw = git(spec)
    subjects = [s for s in raw.split("\n") if s.strip()]
    return audit_subjects(subjects)


# ------------------------------------------------------------------ cli

def main(argv: list[str]) -> int:
    if not argv:
        return selftest()
    if "--file" in argv:
        p = argv[argv.index("--file") + 1]
        try:
            text = open(p, encoding="utf-8").read()
        except OSError as exc:
            print("error: cannot read %s (%s)" % (p, exc))
            return 2
        findings = lint_message(text)
    elif "--message" in argv:
        findings = lint_message(argv[argv.index("--message") + 1].replace("\\n", "\n"))
    elif "--staged" in argv:
        findings, names = scan_staged()
        if names:
            print("staged: %d file(s)" % len(names.split("\n")))
    elif "--history" in argv:
        n = int(argv[argv.index("-n") + 1]) if "-n" in argv else 25
        shared = argv[argv.index("--shared") + 1] if "--shared" in argv else None
        _, notes, findings = history_style(n, shared)
        for note in notes:
            print(note)
        print("history%s: %d finding(s)" % (" @ " + shared if shared else "", len(findings)))
        for x in findings:
            print("  - %s" % x)
        return 1 if findings else 0
    else:
        print(__doc__.strip().splitlines()[2:])
        return 2
    label = "message" if findings else "message"
    print("%s: %d finding(s)" % (label, len(findings)))
    for f in findings:
        print("  - %s" % f)
    return 1 if findings else 0


# ------------------------------------------------------------------ self-test

GOOD = """fix(orders): stop double-charging retried webhooks

The retry loop re-sent payloads on every 5xx, including 501/503 which the
processor treats as permanent failures, so a customer could be charged twice.

Retries now cover 429, 502 and 504 with Retry-After honored, and the delivery id
is derived from the order id so duplicates deduplicate upstream.

Closes #4821
Reported-by: Support <support@example.com>
"""

CASES = [
    ("good message", GOOD, []),
    ("vague subject", "fix: bug\n", ["vague"]),
    ("past tense subject", "fixed the login problem with the session\n", ["imperative"]),
    ("gerund subject", "updating export handler to support csv\n", ["imperative"]),
    ("subject too long", "fix(auth): prevent the token refresh loop from firing when the clock is wrong\n",
     ["characters"]),
    ("trailing period", "fix(auth): reject expired tokens.\n", ["punctuation"]),
    ("no blank line", "fix(auth): reject expired tokens\nbecause they were cached\n", ["blank line"]),
    ("body too wide", "fix(auth): reject expired tokens\n\n" + ("word " * 20) + "\n", ["columns"]),
    ("unknown type", "feature(auth): add magic login\n", ["unknown type"]),
    ("bang without footer", "feat(search)!: return an object instead of an array\n", ["BREAKING CHANGE"]),
    ("bad co-author", "fix(x): handle empty responses\n\nCo-authored-by: jordan\n", ["malformed"]),
    ("secret in message", "fix(api): rotate\n\nold key AKIA1234567890ABCDEF was in the config\n", ["secret"]),
    ("subject names a file", "update webhook_retry.ts\n", ["names a file"]),
    ("revert without body", 'Revert "feat(search): add suggestions"\n', ["no body"]),
]


HISTORY_CASES = [
    ("history clean", ["feat(search): add prefix suggestions", "fix(orders): reject expired tokens",
                       "docs: document env setup"], []),
    ("history staging words", ["wip: save progress", "fix(assets): resolve path issue",
                               "debug: trace loader"], ["staging"]),
    ("history wip-fix parked", ["wip-fix(data): temp empty-row fix - extract to fix/*"], ["staging"]),
    ("history duplicate messages", ["fix(graph): handle NaN", "fix(graph): handle NaN",
                                    "fix(graph): handle NaN"], ["duplicate"]),
]


def selftest() -> int:
    fails = 0
    for name, msg, expect in CASES:
        findings = lint_message(msg)
        joined = " | ".join(findings)
        caught = [e for e in expect if e in joined]
        ok = (not findings) if not expect else len(caught) == len(expect)
        print("%-28s %s %s" % (name, "PASS" if ok else "FAIL",
                               "" if ok else "expected %s, got [%s]" % (expect, joined[:110])))
        fails += 0 if ok else 1
    for name, subjects, expect in HISTORY_CASES:
        _, _, findings = audit_subjects(subjects)
        joined = " | ".join(findings)
        caught = [e for e in expect if e in joined]
        ok = (not findings) if not expect else len(caught) == len(expect)
        print("%-28s %s %s" % (name, "PASS" if ok else "FAIL",
                               "" if ok else "expected %s, got [%s]" % (expect, joined[:110])))
        fails += 0 if ok else 1
    total = len(CASES) + len(HISTORY_CASES)
    print("self-test: %d/%d fixtures behaved" % (total - fails, total))
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
