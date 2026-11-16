# Example 2 - Class B on Linux (ILLUSTRATIVE, synthetic data)

**Prompt:** "Our daemon exits every few days. There's a `core.4821` in /var/lib/app. Why?"

1. `crash_triage.py` → gdb present; `core_pattern=core`; ulimit unlimited ✔.
2. Class: `decode_status.py 139` ⇒ shell status 128+11 = **SIGSEGV** (class B), but confirm in the core: `gdb -batch -ex 'info signal' ...`.
3. `gdb -batch -ex 'thread apply all bt full' -ex 'info sharedlibrary' /usr/bin/appd core.4821 > bt.txt`
4. Excerpt (synthetic):
```
Program terminated with signal SIGSEGV, Segmentation fault.
#0  Cache::evict (this=0x0, key=...) at cache.cpp:88
#1  Worker::run (this=0x55d0c0a3c2a0) at worker.cpp:141
#2  std::thread::_State_impl<...>::_M_run
#3  start_thread
```
5. Read it: fault at `this=0x0` ⇒ null object, access offset small ⇒ null-deref [E1]. Frames have line numbers and small offsets ⇒ trustworthy (private DWARF) [E1].
6. Who nulls it? `thread apply all bt` shows thread 3 in `Cache::reset()` → a second thread resets the pointer while worker uses it ⇒ **data race** (here the textbook kind: two threads, same memory). [E3] Test: run under `-fsanitize=thread`; add a lock; soak.
7. Contrast with Example 1: *no* thread-affinity rule here, two threads share a pointer. Naming it correctly matters for the fix.
