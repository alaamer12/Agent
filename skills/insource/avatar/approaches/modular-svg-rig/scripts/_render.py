"""Shared headless-browser renderer used by the avatar scripts.

Renders SVG text (or a local HTML file) to a PIL image with Playwright/Chromium.
No web server is needed: SVG is inlined into a wrapper page, HTML is opened via file://.
"""
import io
from pathlib import Path

from PIL import Image

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    raise SystemExit(
        "Playwright is required: pip install playwright pillow numpy scipy "
        "--break-system-packages && playwright install chromium"
    )


class Renderer:
    """Reusable renderer: one browser for many renders (fast for sampled checks)."""

    def __init__(self, size=600, scale=2):
        self.size = size      # CSS pixels (square viewport)
        self.scale = scale    # device pixel ratio -> output is size*scale px
        self._pw = self._browser = self._page = None

    def __enter__(self):
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch()
        self._page = self._browser.new_page(
            viewport={"width": self.size, "height": self.size},
            device_scale_factor=self.scale,
        )
        return self

    def __exit__(self, *exc):
        self._browser.close()
        self._pw.stop()

    def _shot(self, transparent, selector=None):
        opts = {"omit_background": transparent}
        if selector:
            return self._page.locator(selector).first.screenshot(**opts)
        return self._page.screenshot(clip={"x": 0, "y": 0, "width": self.size, "height": self.size}, **opts)

    def svg(self, svg_text, transparent=False, bg="transparent"):
        """Render an <svg> string. transparent=True keeps the alpha channel."""
        html = (
            "<!doctype html><html><head><style>html,body{margin:0;padding:0;"
            f"background:{'transparent' if transparent else bg}}}"
            f"svg{{display:block;width:{self.size}px;height:{self.size}px}}"
            f"</style></head><body>{svg_text}</body></html>"
        )
        self._page.set_content(html)
        return Image.open(io.BytesIO(self._shot(transparent))).convert("RGBA")

    def file(self, path, transparent=False, selector=None):
        """Render a local .svg or .html file (opened via file://)."""
        self._page.goto(Path(path).resolve().as_uri())
        return Image.open(io.BytesIO(self._shot(transparent, selector))).convert("RGBA")
