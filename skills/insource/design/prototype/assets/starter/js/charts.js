/**
 * charts.js — FALLBACK sparkline utility.
 *
 * Use this ONLY for simple polyline trend lines (no axes, no labels) inside
 * table cells when no chart library is loaded, or when the user has banned
 * external dependencies.
 *
 * Default behaviour: use Chart.js via CDN for any chart that needs axes,
 * labels, tooltips, legends, or multiple series — see references/libraries.md.
 * A hand-drawn SVG bar/area/pie chart is NOT an acceptable stand-in for Chart.js.
 *
 * To use Chart.js via CDN:
 *   1. Add to <head>:
 *        <script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js" defer></script>
 *   2. Render a <canvas id="my-chart"> in your DOM builder.
 *   3. In render(), after the canvas is in the DOM:
 *        requestAnimationFrame(() => {
 *          const ctx = document.getElementById("my-chart").getContext("2d");
 *          new Chart(ctx, { type: "bar", data: { ... }, options: { responsive: true } });
 *        });
 */
/** Reusable inline-SVG sparkline (polyline only — no axes, no labels). */
export function sparkline(points, { w = 120, h = 32, color = "var(--accent)" } = {}) {
  if (!points || points.length < 2) return "";
  const min = Math.min(...points), max = Math.max(...points), span = max - min || 1;
  const pts = points.map((v, i) =>
    `${(i / (points.length - 1)) * w},${h - 4 - ((v - min) / span) * (h - 8)}`).join(" ");
  return `<svg class="spark" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" fill="none" aria-hidden="true">
    <polyline points="${pts}" stroke="${color}" stroke-width="2" stroke-linecap="round"/>
  </svg>`;
}
