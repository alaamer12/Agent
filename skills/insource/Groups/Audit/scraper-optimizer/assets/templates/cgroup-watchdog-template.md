# Template: Cgroup Memory Watchdog Governor

This template provides a background daemon thread/task that polls Linux control groups (v1 and v2) and executes tiered pressure relief before the container runtime issues an uncatchable OOM SIGKILL.

---

## Python Implementation (`cgroup_watchdog.py`)

```python
"""
cgroup_watchdog.py - Production cgroup v1/v2 reactive memory governor.
"""
import ctypes
import gc
import logging
import os
import sys
import threading
from pathlib import Path
from typing import Callable, List, Optional, Tuple, Union

log = logging.getLogger("memory_governor")
IS_LINUX = sys.platform.startswith("linux")

_POSIX_FADV_DONTNEED = 4

_libc = None
if IS_LINUX:
    try:
        _libc = ctypes.CDLL("libc.so.6", use_errno=True)
    except Exception as err:
        log.warning(f"Failed to load glibc: {err}")

def drop_file_cache(path: Union[str, Path]) -> None:
    """Flush and evict page cache for a specific file path."""
    if not IS_LINUX:
        return
    p = Path(path)
    if not p.is_file():
        return
    try:
        fd = os.open(str(p), os.O_RDONLY)
        try:
            try:
                os.fdatasync(fd)
            except OSError:
                pass
            os.posix_fadvise(fd, 0, 0, _POSIX_FADV_DONTNEED)
        finally:
            os.close(fd)
    except Exception:
        pass

def trim_process_heap() -> None:
    """Invoke runtime GC and force glibc to release unused arenas to kernel."""
    gc.collect()
    if _libc is not None:
        try:
            _libc.malloc_trim(0)
        except Exception:
            pass

def read_cgroup_memory() -> Tuple[float, float, float]:
    """Returns (usage_mb, cache_mb, limit_mb) from cgroup v2 or v1."""
    if not IS_LINUX:
        return 0.0, 0.0, 0.0

    mb = 1024 * 1024

    # Cgroup v2
    cgroup_v2_usage = Path("/sys/fs/cgroup/memory.current")
    if cgroup_v2_usage.exists():
        try:
            usage = int(cgroup_v2_usage.read_text().strip())
            limit_raw = Path("/sys/fs/cgroup/memory.max").read_text().strip()
            limit = 0 if limit_raw == "max" else int(limit_raw)
            
            cache = 0
            stat_file = Path("/sys/fs/cgroup/memory.stat")
            if stat_file.exists():
                for line in stat_file.read_text().splitlines():
                    parts = line.split()
                    if parts and parts[0] == "file":
                        cache = int(parts[1])
                        break
            return usage / mb, cache / mb, limit / mb
        except Exception:
            pass

    # Cgroup v1 fallback
    cgroup_v1_usage = Path("/sys/fs/cgroup/memory/memory.usage_in_bytes")
    if cgroup_v1_usage.exists():
        try:
            usage = int(cgroup_v1_usage.read_text().strip())
            limit_val = int(Path("/sys/fs/cgroup/memory/memory.limit_in_bytes").read_text().strip())
            limit = 0 if limit_val > (1 << 60) else limit_val
            
            cache = 0
            stat_file = Path("/sys/fs/cgroup/memory/memory.stat")
            if stat_file.exists():
                for line in stat_file.read_text().splitlines():
                    parts = line.split()
                    if parts and parts[0] == "total_cache":
                        cache = int(parts[1])
                        break
            return usage / mb, cache / mb, limit / mb
        except Exception:
            pass

    return 0.0, 0.0, 0.0

class CgroupMemoryGovernor:
    def __init__(self, soft_ratio: float = 0.75, hard_ratio: float = 0.88, interval_sec: float = 10.0):
        self.soft_ratio = soft_ratio
        self.hard_ratio = hard_ratio
        self.interval_sec = interval_sec
        self._handlers: List[Tuple[int, Callable[[bool], None]]] = []
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def register_handler(self, priority: int, handler: Callable[[bool], None]) -> None:
        self._handlers.append((priority, handler))
        self._handlers.sort(key=lambda x: x[0])

    def start(self) -> None:
        if self._thread is None:
            self._thread = threading.Thread(target=self._run, daemon=True, name="mem-governor")
            self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)

    def _run(self) -> None:
        while not self._stop_event.wait(self.interval_sec):
            usage, cache, limit = read_cgroup_memory()
            if limit <= 0:
                continue

            ratio = usage / limit
            if ratio >= self.hard_ratio:
                log.warning(f"Hard memory ceiling: {usage:.1f}MB / {limit:.1f}MB ({ratio:.1%}). Cache: {cache:.1f}MB")
                self._dispatch(aggressive=True)
            elif ratio >= self.soft_ratio:
                log.info(f"Soft memory ceiling: {usage:.1f}MB / {limit:.1f}MB ({ratio:.1%}). Cache: {cache:.1f}MB")
                self._dispatch(aggressive=False)

    def _dispatch(self, aggressive: bool) -> None:
        for _, handler in self._handlers:
            try:
                handler(aggressive)
            except Exception as err:
                log.error(f"Governor callback error: {err}")
        trim_process_heap()
```
