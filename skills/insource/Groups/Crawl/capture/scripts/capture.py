"""Dispatcher: python capture.py designs|screenshots|siteshots|page|website|dom|design|images [options]"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design, designs, dom, images, page, screenshots, siteshots, website  # noqa: E402
from _common import utf8_console  # noqa: E402

utf8_console()

COMMANDS = {
    "designs": (designs, "Batch-capture all HTML designs in a designs folder"),
    "screenshots": (screenshots, "Screenshot one URL / local HTML file"),
    "siteshots": (siteshots, "Discover a site's routes and screenshot each one as a scroll series"),
    "page": (page, "Capture a running desktop app window (Windows)"),
    "design": (design, "Extract design tokens and/or HTML patterns via curl (css.dump, html.dump)"),
    "dom": (dom, "Save the fully rendered, fully expanded DOM for scraping"),
    "website": (website, "Download a whole website for offline use (real browser)"),
    "images": (images, "Download a page's images at highest resolution, deduplicated, with a JSON report"),
}

if len(sys.argv) > 1 and sys.argv[1].lower() in COMMANDS:
    sys.argv[1] = sys.argv[1].lower()          # /capture DOM == /capture dom
ap = argparse.ArgumentParser(prog="capture")
sub = ap.add_subparsers(dest="cmd", required=True)
for name, (mod, helptext) in COMMANDS.items():
    mod.add_args(sub.add_parser(name, help=helptext))
args = ap.parse_args()
try:
    COMMANDS[args.cmd][0].run(args)
except KeyboardInterrupt:
    print("Interrupted.", file=sys.stderr)
    sys.exit(130)
except BrokenPipeError:                     # e.g. `capture.py ... | head`
    try:
        sys.stdout.close()
    except Exception:
        pass
    sys.exit(0)
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
