/**
 * Brand palette module template — two roles, one home.
 *
 * Copy into the shared package (`<shared-package>/brand/palette.ts`), replace EVERY hex with the value you
 * measured (references/02 §5), and import it from: the asset generator, the card composer, the SVG favicon,
 * the manifest writer. Never from a component that also has a stylesheet colour.
 *
 * Rule: `BRAND_MARK` is measured from the artwork and is not re-toned. `BRAND_ACCENT` mirrors the
 * stylesheet and is locked by a test. Collapsing them is how an icon silently stops matching the logo.
 *
 * The values below are ILLUSTRATIVE — a neutral deep-plate + emerald scheme, chosen to show the shape of
 * the module. They are not a brand. Replace all of them.
 */

/** Colours measured from the supplied artwork (5-bit bucketing, ink pixels only). */
export const BRAND_MARK = {
  primaryLight: '#34D399',
  primary: '#10B981',
  primaryDeep: '#059669',
  secondary: '#0D9488',
  secondarySoft: '#14B8A6',
  plate: '#0B1220',
  plateMid: '#12203A',
  plateSoft: '#1B2C4A',
  onPlate: '#F8FAFC',
  onPlateMuted: '#CBD5E1',
} as const

/** Mirrored from the UI stylesheet's token file. Locked by a conformance test. */
export const BRAND_ACCENT = {
  base: '#84CC16',
  strong: '#65A30D',
  deep: '#4D7C0F',
} as const

/** Composed tokens for surfaces (icons, tiles, cards). */
export const BRAND = {
  /** Opaque plate behind every icon and card. */
  surface: BRAND_MARK.plate,
  /** Gradient stops for the card background. */
  gradient: [BRAND_MARK.plateMid, BRAND_MARK.plateSoft] as const,
  /** Primary artwork colour. */
  primary: BRAND_MARK.primary,
  /** Text on the surface. */
  onSurface: BRAND_MARK.onPlate,
  /** Secondary text on the surface. */
  onSurfaceMuted: BRAND_MARK.onPlateMuted,
} as const

/** Card geometry and encoder budget — one object, imported by the composer and the fidelity test. */
export const OG_CARD = {
  width: 1200,
  height: 630,
  /** Preview-quality ceiling, not a platform limit. */
  maxBytes: 300 * 1024,
  /** Floyd–Steinberg strength; chosen by eye at 300 px display width. */
  ditherStrength: 0.35,
  /** Try each rung until the encoded card fits `maxBytes`. */
  paletteLadder: [256, 128, 64] as const,
} as const

/** Content must stay inside this box (rounded corners, domain chips, play buttons). */
export const OG_SAFE_AREA = {
  x: 72,
  y: 64,
  width: OG_CARD.width - 144,
  height: OG_CARD.height - 128,
} as const

/**
 * Content families. NOT a fixed list to copy — derive it from the product:
 *
 *   WHAT      a family is one kind of indexable content that shares a card layout and a badge.
 *   MEMBERSHIP a family exists only when it has all four: a static card per locale, a badge copy key,
 *              a resolver (what a slug means for it), and a contract test asserting its routes.
 *   EXTENSION add a family by adding those four things in one change; never by reusing another
 *              family's badge "for now".
 *
 * The names below are an example shape (a home card, a listing kind, a detail kind, a person kind, a
 * policy kind), not a required set.
 */
export const OG_FAMILIES = [
  'home',
  'listing',
  'detail',
  'profile',
  'legal',
] as const

export type OgFamily = (typeof OG_FAMILIES)[number]

/** Copy keys — the only strings a card may contain besides entity names. */
export const OG_COPY_KEYS = {
  siteName: 'og.site_name',
  tagline: 'og.tagline',
  badge: (family: OgFamily) => `og.badge.${family}`,
  stat: (name: string) => `og.stat.${name}`,
} as const

/** Static card path, derived — never hand-written at a call site. */
export function staticOgCardPath(family: OgFamily | 'default', locale: string): string {
  return `/og/og-${family}-${locale}.png`
}

/** Dynamic card path, derived. */
export function ogDynamicPath(family: OgFamily, locale: string, slug: string): string {
  return `/og/${family}/${locale}/${slug}.png`
}
