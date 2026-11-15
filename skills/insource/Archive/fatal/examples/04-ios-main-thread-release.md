# Example 4 - The same lesson on iOS: last release on the wrong thread (ILLUSTRATIVE)

**Prompt:** "Rare `EXC_BAD_ACCESS` in `-[UIView dealloc]` on a background queue."
- Class B/A: report shows `Exception Type: EXC_BAD_ACCESS`, **Crashed Thread: 7 (com.apple.root.default-qos)**, frames `objc_release` → `-[MyOverlay dealloc]` → `-[UIView removeFromSuperview]`.
- Reading: the *last strong reference* was dropped on a background queue, so ARC ran `dealloc` there; UIKit objects require the main thread. This is the ARC twin of the finalizer-thread problem (concepts-primer §5).
- Evidence needed: thread role (queue name), main thread idle, Main Thread Checker output in debug runs.
- Fix family: keep UI objects referenced from the main thread only; hop to main before dropping the last reference (`DispatchQueue.main.async { overlay = nil }`); reuse views instead of creating per tick.
- Symbolicate with the dSYM matching the Binary Image **UUID** (`atos -o … -l <load addr> -arch arm64 <addr>`).
