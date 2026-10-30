/** Reusable inline-SVG charts (shared module — pages must not duplicate this). */
export function sparkline(points, { w = 120, h = 32, color = "var(--accent)" } = {}) {
  if (!points || points.length < 2) return "";
  const min = Math.min(...points), max = Math.max(...points), span = max - min || 1;
  const pts = points.map((v, i) =>
    `${(i / (points.length - 1)) * w},${h - 4 - ((v - min) / span) * (h - 8)}`).join(" ");
  return `<svg class="spark" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" fill="none" aria-hidden="true">
    <polyline points="${pts}" stroke="${color}" stroke-width="2" stroke-linecap="round"/>
  </svg>`;
}
