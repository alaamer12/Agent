#!/usr/bin/env python3
"""Scaffold a feature's role folders and stub units.

Creates the shape the doctrine prescribes — Views with their Renditions colocated,
a feature tier for reusable pieces, `_`-prefixed files for View-scoped Global-Local
implementation, fact sources without markup, Renditions without fact reads — then
lets you fill in the behaviour. Stdlib only.

    python scripts/scaffold_feature.py --feature funds --framework vue \
        --view FundCardView:list,grid --scoped FundCard --wrapper FundCardActions \
        --component AddToWatchlist --component CompareFund --condition layout-toggle

Use --dry-run to print the tree without writing anything. Existing files are never
overwritten; they are reported as skipped.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

FRAMEWORKS = {
    # framework: (unit extension, file casing, dir casing)
    "react":   (".tsx", "pascal", "camel"),
    "solid":   (".tsx", "pascal", "camel"),
    "vue":     (".vue", "pascal", "camel"),
    "svelte":  (".svelte", "pascal", "camel"),
    "blazor":  (".razor", "pascal", "pascal"),
    "dioxus":  (".rs", "snake", "snake"),
}

DOCS = "references/"


def tokens(name: str) -> list[str]:
    """Split any casing into word tokens, preserving acronym groups like `HTML`."""
    name = name.replace("-", "_").replace(" ", "_")
    out = []
    for chunk in name.split("_"):
        if not chunk:
            continue
        found = re.findall(r"[A-Z]+(?![a-z])|[A-Z][a-z0-9]*|[a-z0-9]+", chunk)
        out.extend(found or [chunk])
    return out


def cased(name: str, style: str) -> str:
    parts = tokens(name)
    if not parts:
        return name
    if style == "snake":
        return "_".join(p.lower() for p in parts)
    if style == "kebab":
        return "-".join(p.lower() for p in parts)
    if style == "camel":
        return parts[0] + "".join(p[:1].upper() + p[1:] for p in parts[1:])
    return "".join(p[:1].upper() + p[1:] for p in parts)


def comment(text: str, ext: str) -> str:
    if ext == ".rs":
        return "// " + text
    if ext in {".razor"}:
        return "@* " + text + " *"
    if ext in {".py"}:
        return "# " + text
    return "<!-- " + text + " -->"


def unit(name: str, role: str, ext: str, casing: str, extra: str = "") -> tuple[str, str]:
    """Build one stub file's (name, content) for a role."""
    prefix = "_" if name.startswith("_") else ""
    fname = prefix + cased(name.lstrip("_"), casing) + ext
    if ext == ".rs":
        fn = cased(name, "pascal")
        sig = f"pub fn {fn}() -> Element {{\n    todo!()\n}}"
    else:
        sig = ""
    body = {
        "page": (f"{comment('Role: Page — composes Views only. references/roles.md §3', ext)}\n", sig),
        "view": (f"{comment(f'Role: View — the only unit that consults facts AND selects a Rendition. {DOCS}view-and-rendition.md §2', ext)}\n", sig),
        "rendition": (f"{comment(f'Role: Rendition — props in, markup out. No fact source here or it becomes a View. {DOCS}view-and-rendition.md §5', ext)}\n", sig),
        "component": (f"{comment(f'Role: Component — one purposeful function. Built from the adaptive tier only. {DOCS}primitives-and-imports.md §3', ext)}\n", sig),
        "decoration": (f"{comment(f'Role: Decoration — supports or explains the primary Component. {DOCS}roles.md §6', ext)}\n", sig),
        "scoped": (f"{comment(f'Pole: Global-Local (a) — shared by siblings in THIS folder, no reason to exist outside it. Name is _-prefixed. {DOCS}placement.md §3', ext)}\n", sig),
        "wrapper": (f"{comment(f'Role: Wrapper Component — groups siblings that do NOT coordinate; no responsibility of its own. Run the coordination test. {DOCS}composition-shapes.md §3', ext)}\n", sig),
        "specialised": (f"{comment(f'Role: Specialised Component — composes a base Component with exactly one capability, never copies it. {DOCS}composition-shapes.md §5', ext)}\n", sig),
        "state": (f"{comment(f'Fact source (STATE kind): returns data, never renders. Classification + ownership: the /states skill. /pvc only needs that it does not render.', ext)}\n", sig),
        "condition": (f"{comment(f'Fact source (CONDITION kind): returns data, never renders, read-only surface. Classification + ownership: the /states skill.', ext)}\n", sig),
    }[role]
    header, code = body
    text = header
    if extra:
        text += comment(extra, ext) + "\n"
    if ext == ".rs":
        text += f"\nuse dioxus::prelude::*;\n\n#[component]\n{code}\n"
    elif ext == ".razor":
        text += "\n" + ("@code {\n    [Parameter] public string Message { get; set; } = \"\";\n}\n"
                        if role in ("rendition", "component", "decoration", "scoped", "wrapper") else "@code {\n}\n")
    elif ext in (".vue", ".svelte"):
        text += ("\n<script setup lang=\"ts\">\n</script>\n\n<template>\n  <div></div>\n</template>\n"
                 if role in ("view", "rendition", "component", "decoration", "scoped", "wrapper", "page", "specialised")
                 else "\n<script setup lang=\"ts\">\n</script>\n")
    else:
        text += "\n" + (code.replace("pub fn", "export function").replace(" -> Element", "") + "\n"
                        if code else "export {};\n")
    return fname, text


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    ap = argparse.ArgumentParser(description="Scaffold a role-based feature structure.")
    ap.add_argument("--root", default="src", help="source root (default: src)")
    ap.add_argument("--feature", required=True, help="feature/domain name")
    ap.add_argument("--framework", default="react", choices=sorted(FRAMEWORKS))
    ap.add_argument("--dir", default=None, help="override the feature grouping folder "
                                                "(features/ capabilities/ modules/ …)")
    ap.add_argument("--view", action="append", default=[], metavar="NAME[:rendition,rendition]",
                    help="View, optionally with its Rendition cases after a colon")
    ap.add_argument("--page", action="append", default=[], help="Page under app/pages")
    ap.add_argument("--component", "--components", action="append", default=[],
                    help="feature-tier Component (repeatable)")
    ap.add_argument("--decoration", "--decorations", action="append", default=[],
                    help="feature-tier Decoration (repeatable)")
    ap.add_argument("--scoped", action="append", default=[], metavar="NAME",
                    help="View-scoped Global-Local unit for the most recent --view (`_` prefixed)")
    ap.add_argument("--wrapper", action="append", default=[], metavar="NAME",
                    help="Wrapper Component for the most recent --view (`_` prefixed)")
    ap.add_argument("--state", action="append", default=[], help="State fact source at the feature tier")
    ap.add_argument("--condition", action="append", default=[], help="Condition fact source at the feature tier")
    ap.add_argument("--shared-state", action="append", default=[], help="Global generic State mechanism")
    ap.add_argument("--shared-condition", action="append", default=[], help="Global Condition")
    ap.add_argument("--global-rendition", action="append", default=[], help="Global reusable Rendition")
    ap.add_argument("--primitive", action="append", default=[], help="adaptive-tier primitive (creates base too)")
    ap.add_argument("--specialised", metavar="BASE+SPECIAL", action="append", default=[],
                    help="base Component plus its Specialised form, e.g. SearchInput+DebouncedSearchInput")
    ap.add_argument("--dry-run", action="store_true", help="print the plan, write nothing")
    ns = ap.parse_args(argv)

    ext, casing, dircase = FRAMEWORKS[ns.framework]
    grouping = ns.dir or ("features" if ns.framework != "blazor" else "Features")
    feat = cased(ns.feature, dircase)
    fdir = os.path.join(ns.root, cased(grouping, dircase), feat)

    files: list[tuple[str, str]] = []

    def add(path: str, role: str, name: str, extra: str = ""):
        fname, content = unit(name, role, ext, casing, extra)
        files.append((os.path.join(path, fname).replace("\\", "/"), content))

    for spec in ns.view:
        name, _, rends = spec.partition(":")
        vdir = os.path.join(fdir, cased("views", dircase), cased(name, casing if casing != "snake" else dircase))
        add(vdir, "view", name)
        for r in filter(None, rends.split(",")):
            add(vdir, "rendition", r if r.endswith("Rendition") else r + "Rendition")
        for s in ns.scoped:
            add(vdir, "scoped", "_" + s if not s.startswith("_") else s)
        for w in ns.wrapper:
            add(vdir, "wrapper", "_" + w if not w.startswith("_") else w)
        ns.scoped, ns.wrapper = [], []

    for p in ns.page:
        add(os.path.join(ns.root, cased("app", dircase), cased("pages", dircase), cased(p, casing if casing == "pascal" else dircase)),
            "page", p)

    for c in ns.component:
        add(os.path.join(fdir, cased("components", dircase), cased(c, casing if casing != "snake" else dircase)),
            "component", c)

    for d in ns.decoration:
        add(os.path.join(fdir, cased("decorations", dircase), cased(d, casing if casing != "snake" else dircase)),
            "decoration", d)

    tier = cased("behaviour", dircase)
    for s in ns.state:
        add(os.path.join(fdir, tier), "state",
            s if casing == "snake" else ("use" + cased(s, "pascal") + "State").replace("UseUse", "Use"))
    for c in ns.condition:
        add(os.path.join(fdir, tier), "condition",
            c if casing == "snake" else ("use" + cased(c, "pascal") + "Condition"))

    shared = os.path.join(ns.root, cased("shared", dircase))
    for s in ns.shared_state:
        add(os.path.join(shared, tier), "state", s)
    for c in ns.shared_condition:
        add(os.path.join(shared, cased("conditions", dircase)), "condition", c)
    for r in ns.global_rendition:
        add(os.path.join(ns.root, cased("ui", dircase), cased("renditions", dircase)),
            "rendition", r if r.endswith("Rendition") else r + "Rendition")

    for pr in ns.primitive:
        for sub, role in (("base", "component"), ("adaptive", "component")):
            add(os.path.join(ns.root, cased("ui", dircase), cased(sub, dircase)), role, pr,
                "base tier: re-export the platform control under our own name — one line is complete."
                if sub == "base" else "adaptive tier: base + this system's skin; Components import only this.")

    for spec in ns.specialised:
        base, _, special = spec.partition("+")
        if not special:
            base, special = "", base
        path = os.path.join(fdir, cased("components", dircase), cased(special, casing if casing != "snake" else dircase))
        add(path, "scoped", "_" + base)
        add(path, "specialised", special,
            "Underscore the base only if no standalone consumer exists for this feature's settled behaviour "
            "(references/settled-behavior.md §3).")

    if not files:
        print("nothing to scaffold — pass at least one of --view/--page/--component/--decoration/"
              "--state/--condition/--primitive/--specialised")
        return 2

    created = skipped = 0
    for path, content in files:
        if ns.dry_run:
            print(f"would write  {path}")
            continue
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.exists(path):
            print(f"skipped      {path} (exists)")
            skipped += 1
            continue
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)
        print(f"created      {path}")
        created += 1

    if not ns.dry_run:
        print(f"\n{created} created, {skipped} skipped under {fdir.replace(os.sep, '/')}")
        print("next: fill the View so it consults facts and selects a Rendition, keep Renditions "
              "props-only, then run scripts/check_pvc.py " + ns.root)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
