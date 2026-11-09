/**
 * glyphs.js — FALLBACK icon module.
 *
 * Use this ONLY when the user has explicitly banned external libraries or CDN.
 * Default behaviour: load Lucide (or another icon library) via CDN instead —
 * see references/libraries.md. Hand-rolled SVG paths are a maintenance burden
 * and produce inferior results compared to a real icon library.
 *
 * To use Lucide via CDN:
 *   1. Add to <head>:
 *        <script src="https://cdn.jsdelivr.net/npm/lucide@latest/dist/umd/lucide.min.js" defer></script>
 *   2. In your page HTML, use:  <i data-lucide="search"></i>
 *   3. After every render() call: if (window.lucide) lucide.createIcons();
 */
  menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>',
  bell: '<path d="M18 8a6 6 0 1 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/>',
  close: '<path d="M18 6L6 18M6 6l12 12"/>',
  chevron: '<path d="M9 18l6-6-6-6"/>',
  up: '<path d="M12 19V5M5 12l7-7 7 7"/>',
  down: '<path d="M12 5v14M19 12l-7 7-7-7"/>',
};

export function icon(name, cls = "") {
  const d = P[name];
  if (!d) return "";
  return `<svg class="icon ${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${d}</svg>`;
}
