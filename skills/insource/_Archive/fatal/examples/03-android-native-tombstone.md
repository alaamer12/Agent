# Example 3 - Android class A/B via tombstone (ILLUSTRATIVE, synthetic data)

**Prompt:** "Crash reports from Pixel devices only: 'signal 11' but no Java stack."
```
*** *** *** ***
Build fingerprint: 'google/…/user/release-keys'
ABI: 'arm64'
pid: 9123, tid: 9150, name: RenderThread  >>> com.example.app <<<
signal 11 (SIGSEGV), code 1 (SEGV_MAPERR), fault addr 0x0000000000000018
backtrace:
  #00 pc 00000000001a2b3c  /data/app/…/lib/arm64/libgfx.so (Gfx::Surface::flush+44) (BuildId: 5f3c…)
  #01 pc 00000000001a3100  /data/app/…/lib/arm64/libgfx.so (Gfx::Renderer::draw+212)
```
1. Class B: SEGV_MAPERR at `0x18` ⇒ null pointer + field offset 0x18 [E1].
2. Symbols: use the **unstripped** `libgfx.so` whose BuildId matches: `ndk-stack -sym obj/local/arm64-v8a < tombstone.txt`. If BuildIds differ, stop - names would lie.
3. "Pixel only": compare device-specific facts (driver, ABI, Android version) in the report header before theorising.
4. Check `adb shell dumpsys activity exit-info com.example.app` → `REASON_CRASH_NATIVE` confirms it's not a lmkd kill.
5. If instead the reason is `REASON_LOW_MEMORY` or `SIGKILL`, it's class E: analyse memory, not a backtrace.
