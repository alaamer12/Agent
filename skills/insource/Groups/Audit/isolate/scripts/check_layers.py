#!/usr/bin/env python3
"""Validate a layers tree and print which layer wins each file for a profile. Stdlib only.

Usage:
  check_layers.py LAYERS_ROOT [--base BASE_DIR] [--profile axis=value,axis=value] [--json]

Folder convention (axis and value names must not contain '.' or '+'):
  LAYERS_ROOT/<axisA>/<valueA>/<component>/<files>                    one coordinate
  LAYERS_ROOT/<axisA>+<axisB>/<valueA>.<valueB>/<component>/<files>   two or more coordinates

Checks:
  ERROR  malformed folder (axis count != value count, repeated axis, empty name)
  ERROR  ambiguity: two layers of equal specificity can match the same context, both provide the same
         relative path, and no layer with the union of their coordinates provides it (needs a tie-breaker)
  WARN   (with --base) a layer file identical to the base file at the same relative path: a fork, not an overlay
  INFO   (with --base) a layer file with no base counterpart: allowed for helpers reachable only through a seam

With --profile it prints the resolved map: for each relative path, the most specific matching layer,
or "base" when no layer matches. Equal-specificity matches print AMBIGUOUS. Exit code 1 when errors exist.
"""
import argparse
import hashlib
import itertools
import json
import os
import sys


def digest(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def load_layers(root, errors):
    layers = {}
    for axes_spec in sorted(os.listdir(root)):
        ap = os.path.join(root, axes_spec)
        if not os.path.isdir(ap):
            continue
        axes = axes_spec.split("+")
        for vals_spec in sorted(os.listdir(ap)):
            vp = os.path.join(ap, vals_spec)
            if not os.path.isdir(vp):
                continue
            vals = vals_spec.split(".")
            lid = f"{axes_spec}/{vals_spec}"
            if len(axes) != len(vals) or "" in axes or "" in vals or len(set(axes)) != len(axes):
                errors.append(f"malformed layer folder '{lid}': axes {axes} do not pair with values {vals}")
                continue
            files = {}
            for dirpath, _, names in os.walk(vp):
                for n in names:
                    full = os.path.join(dirpath, n)
                    files[os.path.relpath(full, vp)] = full
            layers[lid] = {"coords": dict(zip(axes, vals)), "files": files}
    return layers


def consistent(a, b):
    return all(b.get(k, v) == v for k, v in a.items())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("layers_root")
    ap.add_argument("--base")
    ap.add_argument("--profile", help="e.g. channel=canary,audience=eg")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not os.path.isdir(args.layers_root):
        sys.exit(f"not a directory: {args.layers_root}")

    errors, warns, infos = [], [], []
    layers = load_layers(args.layers_root, errors)

    by_path = {}
    for lid, layer in layers.items():
        for rel in layer["files"]:
            by_path.setdefault(rel, []).append(lid)

    # Ambiguity check
    for rel, lids in sorted(by_path.items()):
        for a, b in itertools.combinations(lids, 2):
            ca, cb = layers[a]["coords"], layers[b]["coords"]
            if len(ca) != len(cb) or ca == cb or not (consistent(ca, cb) and consistent(cb, ca)):
                continue
            union = {**ca, **cb}
            tie = [x for x in lids if layers[x]["coords"] == union]
            if not tie:
                errors.append(f"ambiguous: '{rel}' is provided by '{a}' and '{b}' and no layer with coordinates "
                              f"{union} provides it; add a tie-breaker layer")

    # Fork / helper checks
    if args.base:
        for lid, layer in layers.items():
            for rel, full in layer["files"].items():
                bp = os.path.join(args.base, rel)
                if os.path.isfile(bp):
                    if digest(bp) == digest(full):
                        warns.append(f"fork: '{lid}/{rel}' is identical to the base file; delete it")
                else:
                    infos.append(f"added: '{lid}/{rel}' has no base counterpart (ok only if reachable through a seam)")

    # Resolved map
    resolved = None
    if args.profile:
        ctx = dict(p.split("=", 1) for p in args.profile.split(",") if "=" in p)
        resolved = {}
        for rel, lids in sorted(by_path.items()):
            match = [x for x in lids if all(ctx.get(k) == v for k, v in layers[x]["coords"].items())]
            if not match:
                resolved[rel] = "base"
                continue
            best = max(len(layers[x]["coords"]) for x in match)
            top = [x for x in match if len(layers[x]["coords"]) == best]
            resolved[rel] = top[0] if len(top) == 1 else "AMBIGUOUS: " + ", ".join(top)
            if len(top) > 1:
                errors.append(f"profile {ctx}: '{rel}' resolves ambiguously between {top}")

    if args.json:
        json.dump({"errors": errors, "warnings": warns, "info": infos, "resolved": resolved}, sys.stdout, indent=2)
        print()
    else:
        print(f"Layers found: {len(layers)}")
        for lid in sorted(layers):
            print(f"  - {lid}  ({len(layers[lid]['files'])} files)")
        for title, items in (("ERRORS", errors), ("WARNINGS", warns), ("INFO", infos)):
            if items:
                print(f"\n{title}")
                print("\n".join(f"  - {i}" for i in items))
        if resolved is not None:
            print(f"\nResolved map for {args.profile}")
            for rel, who in resolved.items():
                print(f"  {rel} -> {who}")
        if not errors:
            print("\nOK: no errors.")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
