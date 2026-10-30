// androidMain/ShareSheet.android.kt  ✅ new file — Android's real implementation
actual fun shareText(text: String) {
    val intent = Intent(Intent.ACTION_SEND).apply {
        type = "text/plain"
        putExtra(Intent.EXTRA_TEXT, text)
    }
    currentActivity?.startActivity(Intent.createChooser(intent, null))
}
