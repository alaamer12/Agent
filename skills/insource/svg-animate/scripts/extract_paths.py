#!/usr/bin/env python3
"""Extract path data + render-relevant attributes from an SVG as JSON.

Usage:
  python3 extract_paths.py <file.svg>            # full JSON dump
  python3 extract_paths.py <file.svg> --lengths  # include estimated path lengths

Never extract `d` alone: fill, fill-rule, stroke and friends travel with it.
"""
import json
import math
import re
import sys


def parse_svg(content):
    m = re.search(r'<svg[^>]*>', content)
    if not m:
        sys.exit("ERROR: no <svg> root found")
    tag = m.group(0)
    attrs = dict(re.findall(r'([\w:-]+)="([^"]*)"', tag))
    paths = []
    for p in re.findall(r'<path\b[^>]*?/>', content):
        a = dict(re.findall(r'([\w:-]+)="([^"]*)"', p))
        if 'd' in a:
            paths.append(a)
    return attrs, paths


TOKEN_RE = re.compile(r'([MLHVCSQTAZmlhvcsqtaz])|(-?\d*\.?\d+(?:e[-+]?\d+)?)')


def points_for_segment(cmd, nums, cur, start):
    """Yield sampled points for one command. Handles absolute + relative."""
    rel = cmd.islower()
    C = cmd.upper()
    pts = []
    if C == 'L' or C == 'H' or C == 'V':
        x, y = (cur[0] + nums[-2], cur[1] + nums[-1]) if rel else (nums[-2] if len(nums) > 1 else cur[0], nums[-1])
        if C == 'H':
            x = cur[0] + nums[0] if rel else nums[0]
            y = cur[1]
        if C == 'V':
            y = cur[1] + nums[0] if rel else nums[0]
            x = cur[0]
        return [cur, (x, y)], (x, y)
    if C == 'C':
        p0, c1, c2, p1 = cur, (nums[0], nums[1]), (nums[2], nums[3]), (nums[4], nums[5])
        if rel:
            c1, c2, p1 = (p0[0]+c1[0], p0[1]+c1[1]), (p0[0]+c2[0], p0[1]+c2[1]), (p0[0]+p1[0], p0[1]+p1[1])
        for i in range(1, 33):
            t = i / 32.0
            mt = 1 - t
            x = mt**3*p0[0] + 3*mt**2*t*c1[0] + 3*mt*t**2*c2[0] + t**3*p1[0]
            y = mt**3*p0[1] + 3*mt**2*t*c1[1] + 3*mt*t**2*c2[1] + t**3*p1[1]
            pts.append((x, y))
        return [cur] + pts, p1
    if C == 'Q':
        p0, c, p1 = cur, (nums[0], nums[1]), (nums[2], nums[3])
        if rel:
            c, p1 = (p0[0]+c[0], p0[1]+c[1]), (p0[0]+p1[0], p0[1]+p1[1])
        for i in range(1, 25):
            t = i / 24.0
            mt = 1 - t
            x = mt**2*p0[0] + 2*mt*t*c[0] + t**2*p1[0]
            y = mt**2*p0[1] + 2*mt*t*c[1] + t**2*p1[1]
            pts.append((x, y))
        return [cur] + pts, p1
    if C == 'A':
        x, y = (cur[0]+nums[-2], cur[1]+nums[-1]) if rel else (nums[-2], nums[-1])
        return [cur, (x, y)], (x, y)
    if C == 'Z':
        return [cur, start], start
    return [cur], cur


def path_lengths(d):
    """Return (total_length, longest_subpath_length) sampling all contours."""
    toks = TOKEN_RE.findall(d)
    seq = []
    for cmd, num in toks:
        if cmd:
            seq.append((cmd, None))
        else:
            seq.append((None, float(num)))
    cur = (0.0, 0.0)
    start = (0.0, 0.0)
    cmd = None
    pending = []
    total = 0.0
    sub_total = 0.0
    longest_sub = 0.0

    def close_subpath():
        nonlocal sub_total, longest_sub
        longest_sub = max(longest_sub, sub_total)
        sub_total = 0.0

    def flush():
        nonlocal total, sub_total, cur, start, pending, cmd
        if cmd is None or not pending:
            return
        C = cmd.upper()
        arities = {'M': 2, 'L': 2, 'H': 1, 'V': 1, 'C': 6, 'S': 4, 'Q': 4, 'T': 2, 'A': 7, 'Z': 0}
        arity = arities.get(C, 2)
        i = 0
        while i < len(pending):
            chunk = pending[i:i+arity]
            if len(chunk) < arity:
                break
            if C == 'M':
                close_subpath()
            pts, nxt = points_for_segment(cmd, chunk, cur, start)
            seg = sum(math.dist(pts[j], pts[j+1]) for j in range(len(pts)-1))
            total += seg
            sub_total += seg
            cur = nxt
            if C == 'M':
                start = cur
                cmd = 'l' if cmd.islower() else 'L'  # subsequent pairs are implicit lineto
                C = 'L'
            i += arity
        pending = []

    for kind, val in seq:
        if kind:
            flush()
            cmd = kind
            if cmd.upper() == 'Z':
                flush()
        else:
            pending.append(val)
    flush()
    close_subpath()
    return round(total, 2), round(longest_sub, 2)


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: extract_paths.py <file.svg> [--lengths]")
    want_lengths = '--lengths' in sys.argv
    f = sys.argv[1]
    content = open(f).read()
    attrs, paths = parse_svg(content)
    out = {'file': f, 'svg': attrs, 'path_count': len(paths), 'paths': paths}
    if want_lengths:
        lens = [path_lengths(p['d']) for p in paths]
        for p, (tot, sub) in zip(out['paths'], lens):
            p['length_total'] = tot
            p['length_longest_subpath'] = sub
        out['max_subpath_length'] = max((s for _, s in lens), default=0)
        out['total_length_all_paths'] = round(sum(t for t, _ in lens), 2)
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
