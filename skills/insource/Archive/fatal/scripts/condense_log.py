#!/usr/bin/env python3
"""condense_log.py - read a HUGE log or agent transcript in a short-but-complete form.

  condense_log.py transcript.md                 # digest: every turn/tool call kept, bulk output trimmed
  condense_log.py transcript.md --outline       # headings only (see the shape first)
  condense_log.py big.log --max-lines 150       # plain log: collapse repeats, keep errors + head/tail
  condense_log.py transcript.md --user-chars 2000 --block-lines 12

Every kept line carries its ORIGINAL line number [L123]; zoom with `sed -n 123,180p file`.
Learned pattern (agent sessions exported as markdown): ## User / ## Thinking / ### Ran|Failed to run|Read|Searched|Fetched|Edited
<what> / fenced blocks. The story lives in user messages, 1-sentence Thinking summaries and Failed/Ran headers; bulk output
(listings, 600-line stack dumps, diffs) rarely does - but its FIRST lines and its ERROR lines usually do. That is what is kept.
(Measured: a 4,497-line / 219 KB transcript -> ~440 lines / ~36 KB.)
"""
import argparse
import collections
import re
import signal

ERR = re.compile(r"(Traceback|Error|ERROR|Failed|failed|Exception|FATAL|fatal|denied|not found|404|0x[cC]000[0-9a-fA-F]{4}|SIG[A-Z]{3,5}\b)")
HEAD = re.compile(r"^(#{1,4}) (.*)")


def clip(s, n):
    s = s.strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def outline(lines):
    for i, l in enumerate(lines, 1):
        m = HEAD.match(l)
        if m:
            print("[L%d] %s %s" % (i, m.group(1), clip(m.group(2), 150)))


def digest_markdown(lines, a):
    i, n, stats = 0, len(lines), collections.Counter()
    while i < n:
        m = HEAD.match(lines[i])
        if not m:
            i += 1
            continue
        level, title = len(m.group(1)), m.group(2)
        j, infence = i + 1, False
        while j < n:
            if lines[j].startswith("```"):
                infence = not infence
            elif not infence and HEAD.match(lines[j]) and len(HEAD.match(lines[j]).group(1)) <= max(level, 3):
                break
            j += 1
        body = lines[i + 1: j]
        if title.startswith("User"):
            print("\n[L%d] USER: %s" % (i + 1, clip(" ".join(x.strip() for x in body if x.strip()), a.user_chars)))
            stats["user"] += 1
        elif title.startswith("Thinking"):
            print("[L%d] think: %s" % (i + 1, clip(" ".join(x.strip() for x in body if x.strip() and not x.startswith("#")), a.think_chars)))
        elif level >= 3:
            stats[title.split(" ")[0]] += 1
            print("[L%d] %s%s" % (i + 1, "!! " if title.startswith("Failed") else "- ", clip(title, a.header_chars)))
            k = 0
            while k < len(body):
                if body[k].startswith("```"):
                    lang, e = body[k][3:].strip(), k + 1
                    while e < len(body) and not body[e].startswith("```"):
                        e += 1
                    blk = body[k + 1: e]
                    if lang == "diff":
                        print("      diff +%d/-%d" % (sum(1 for x in blk if x.startswith("+") and not x.startswith("+++")),
                                                      sum(1 for x in blk if x.startswith("-") and not x.startswith("---"))))
                    elif any(x.strip() for x in blk):
                        shown = [x for x in blk if x.strip()][: a.block_lines]
                        for x in shown:
                            print("      | " + clip(x, a.line_chars))
                        errs = [x for x in blk[a.block_lines:] if ERR.search(x)][:3]
                        for x in errs:
                            print("      ! " + clip(x, a.line_chars))
                        hidden = len(blk) - len(shown) - len(errs)
                        if hidden > 0:
                            print("      … %d more lines (L%d-L%d)" % (hidden, i + k + 2, i + e + 1))
                    k = e + 1
                else:
                    k += 1
        else:
            print("[L%d] %s %s" % (i + 1, "#" * level, clip(title, 150)))
        i = j
    print("\n# structure counts: " + ", ".join("%s=%d" % kv for kv in stats.most_common()))


def digest_plain(lines, a):
    norm = lambda s: re.sub(r"\s+", " ", re.sub(r"0x[0-9a-fA-F]+|\d+", "#", s)).strip()[:100]
    cnt = collections.Counter(norm(l) for l in lines if l.strip())
    first = {}
    for i, l in enumerate(lines, 1):
        first.setdefault(norm(l), i)
    keep = [(i, l) for i, l in enumerate(lines, 1) if l.strip() and (i <= a.head or i > len(lines) - a.tail or ERR.search(l))
            and not (cnt[norm(l)] > 3 and first[norm(l)] != i)]
    for i, l in keep[: a.max_lines]:
        r = cnt[norm(l)]
        print("[L%d]%s %s" % (i, (" x%d" % r) if r > 3 else "", clip(l, a.line_chars)))
    if len(keep) > a.max_lines:
        print("… %d more kept lines; raise --max-lines or grep" % (len(keep) - a.max_lines))
    top = [(k, c) for k, c in cnt.most_common(6) if c > 3]
    if top:
        print("\n# most repeated message shapes")
        for k, c in top:
            print("  x%d %s" % (c, k))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("--outline", action="store_true")
    for name, d in (("user-chars", 900), ("think-chars", 260), ("header-chars", 170), ("line-chars", 150), ("block-lines", 5),
                    ("head", 25), ("tail", 25), ("max-lines", 250)):
        ap.add_argument("--" + name, type=int, default=d)
    a = ap.parse_args()
    lines = open(a.path, encoding="utf-8", errors="replace").read().split("\n")
    if a.outline:
        return outline(lines)
    (digest_markdown if sum(1 for l in lines if l.startswith(("## ", "### "))) >= 5 else digest_plain)(lines, a)


if __name__ == "__main__":
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    main()
