// ShareSheet.kt  ❌ mixed-concern: one method branches internally, another has no variance
object ShareSheet {
    fun shareText(text: String) {
        if (Platform.isAndroid) {
            // Android: ACTION_SEND intent
            val intent = Intent(Intent.ACTION_SEND).apply {
                type = "text/plain"
                putExtra(Intent.EXTRA_TEXT, text)
            }
            currentActivity?.startActivity(Intent.createChooser(intent, null))
        } else if (Platform.isIOS) {
            // iOS: UIActivityViewController — totally different API shape
            val controller = UIActivityViewController(listOf(text), null)
            currentViewController?.presentViewController(controller, true, null)
        }
        // desktop/web: silently does nothing — nobody decided that on purpose
    }

    fun formatShareMessage(title: String, url: String): String =
        "$title\n$url" // no platform variance — fine as-is
}
