// iosMain/ShareSheet.ios.kt  ✅ new file — iOS's real implementation
actual fun shareText(text: String) {
    val controller = UIActivityViewController(listOf(text), null)
    currentViewController?.presentViewController(controller, true, null)
}
