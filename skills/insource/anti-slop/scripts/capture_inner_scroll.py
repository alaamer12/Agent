"""Capture visible states of scrollable panels that page-level scrolling misses."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from playwright.sync_api import sync_playwright


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--width", type=int, default=1440)
    parser.add_argument("--height", type=int, default=900)
    parser.add_argument("--wait-ms", type=int, default=1000)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": args.width, "height": args.height})
        page.goto(args.url, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(args.wait_ms)
        panels = page.evaluate(
            """() => [...document.querySelectorAll('*')]
              .filter(el => {
                const style = getComputedStyle(el);
                return /(auto|scroll)/.test(style.overflowY) &&
                  el.scrollHeight > el.clientHeight + 24 &&
                  el.clientHeight > 80;
              })
              .map((el, index) => ({
                index,
                height: el.clientHeight,
                scrollHeight: el.scrollHeight,
                label: `${el.tagName.toLowerCase()}-${el.id || el.className || index}`
              }));"""
        )

        if not panels:
            raise SystemExit("No internally scrollable panel was found.")

        for panel in panels:
            print(
                f"Panel {panel['index'] + 1}: {panel['label']} "
                f"({panel['height']}px viewport, {panel['scrollHeight']}px content)"
            )
            overlap = min(100, max(40, panel["height"] // 5))
            max_scroll = panel["scrollHeight"] - panel["height"]
            step_size = max(1, panel["height"] - overlap)
            steps = max(1, math.ceil(max_scroll / step_size) + 1)
            for step in range(steps):
                page.evaluate(
                    """({index, scrollTop}) => {
                      const panels = [...document.querySelectorAll('*')]
                        .filter(el => {
                          const style = getComputedStyle(el);
                          return /(auto|scroll)/.test(style.overflowY) &&
                            el.scrollHeight > el.clientHeight + 24 &&
                            el.clientHeight > 80;
                        });
                      const panel = panels[index];
                      panel.scrollTop = scrollTop;
                    }""",
                    {
                        "index": panel["index"],
                        "scrollTop": min(step * step_size, max_scroll),
                    },
                )
                page.wait_for_timeout(args.wait_ms)
                output = args.output_dir / f"{panel['index'] + 1:02d}-{step + 1:03d}.png"
                page.screenshot(path=str(output))
                print(f"Saved: {output}")

        browser.close()


if __name__ == "__main__":
    main()