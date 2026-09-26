// commonMain/ShareSheet.kt  ✅ shared shell — Kotlin Multiplatform's OWN file-separation mechanism.
// No custom PlatformSelect helper needed here: `expect`/`actual` combined with source sets
// (commonMain/, androidMain/, iosMain/) IS the file-separation + select-helper mechanism for
// this ecosystem (see references/utilities.md §1 and §3) — the compiler enforces it.
// The non-varying function stays here, untouched — it never needed a platform split.
expect fun shareText(text: String)

fun formatShareMessage(title: String, url: String): String =
    "$title\n$url" // no platform variance — fine as-is, stays in the shared source set
