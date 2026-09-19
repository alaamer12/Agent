# Polyglot Walkthrough: Byte-Budgeted Backpressure Pipelines

In high-concurrency web scrapers, data payload sizes vary across orders of magnitude (e.g., 2 KB JSON vs 20 MB HTML/DOM with inlined images). A queue bounded by item count (`maxsize=200`) provides zero protection against memory exhaustion.

Below are idiomatic before-and-after implementations across the top 4 runtimes: **Python**, **Go**, **Node.js/TypeScript**, and **Rust**.

---

## 1. Python (CPython 3.11+ asyncio)

### Before: Unbounded Item-Count Queue (Vulnerable to Payload Spikes)
```python
import asyncio

# NAIVE: 200 items of 10 MB DOMs = 2.0 GB RAM!
queue: asyncio.Queue = asyncio.Queue(maxsize=200)

async def producer(urls):
    for url in urls:
        html = await fetch(url) # Can be 10 MB
        await queue.put(html)   # Blocks only on COUNT, oblivious to bytes
```

### After: Byte-Budgeted Semaphore-Gated Pipeline
```python
import asyncio
from typing import Generic, TypeVar

T = TypeVar("T")

class ByteBudgetedQueue(Generic[T]):
    """Queue bounded strictly by total in-flight payload bytes."""
    def __init__(self, max_bytes: int):
        self._max_bytes = max_bytes
        self._current_bytes = 0
        self._queue: list[tuple[T, int]] = []
        self._cond = asyncio.Condition()

    async def put(self, item: T, byte_size: int) -> None:
        async with self._cond:
            # Backpressure: wait if adding this payload breaches memory ceiling
            while self._current_bytes + byte_size > self._max_bytes and self._current_bytes > 0:
                await self._cond.wait()
            self._current_bytes += byte_size
            self._queue.append((item, byte_size))
            self._cond.notify_all()

    async def get(self) -> tuple[T, int]:
        async with self._cond:
            while not self._queue:
                await self._cond.wait()
            item, byte_size = self._queue.pop(0)
            return item, byte_size

    async def task_done(self, byte_size: int) -> None:
        async with self._cond:
            self._current_bytes = max(0, self._current_bytes - byte_size)
            self._cond.notify_all()
```

---

## 2. Go (1.21+ Goroutines & Sync.Cond)

### Before: Native Fixed-Slot Channel
```go
// NAIVE: 200 items of 15MB pages = 3.0 GB RAM
ch := make(chan []byte, 200)

func producer(urls []string) {
    for _, url := range urls {
        body := fetch(url)
        ch <- body // Only blocks when 200 slots are full
    }
}
```

### After: Byte-Bounded Flow Controller
```go
package pipeline

import (
	"sync"
)

type ByteBoundedQueue struct {
	maxBytes     int64
	currentBytes int64
	mu           sync.Mutex
	notFull      *sync.Cond
	notEmpty     *sync.Cond
	items        [][]byte
	closed       bool
}

func NewByteBoundedQueue(maxBytes int64) *ByteBoundedQueue {
	q := &ByteBoundedQueue{
		maxBytes: maxBytes,
		items:    make([][]byte, 0),
	}
	q.notFull = sync.NewCond(&q.mu)
	q.notEmpty = sync.NewCond(&q.mu)
	return q
}

func (q *ByteBoundedQueue) Push(payload []byte) {
	size := int64(len(payload))
	q.mu.Lock()
	defer q.mu.Unlock()

	// Suspend producer when in-flight memory exceeds budget
	for q.currentBytes+size > q.maxBytes && q.currentBytes > 0 && !q.closed {
		q.notFull.Wait()
	}

	q.currentBytes += size
	q.items = append(q.items, payload)
	q.notEmpty.Signal()
}

func (q *ByteBoundedQueue) Pop() ([]byte, bool) {
	q.mu.Lock()
	defer q.mu.Unlock()

	for len(q.items) == 0 && !q.closed {
		q.notEmpty.Wait()
	}
	if len(q.items) == 0 && q.closed {
		return nil, false
	}

	item := q.items[0]
	q.items = q.items[1:]
	q.currentBytes -= int64(len(item))
	q.notFull.Broadcast()
	return item, true
}
```

---

## 3. Node.js / TypeScript (Streams & HighWaterMark)

### Before: ObjectMode Array Buffering
```typescript
// NAIVE: Accumulating payloads in an array queue
const queue: string[] = [];
async function enqueue(html: string) {
  queue.push(html); // Unbounded heap growth
}
```

### After: Byte-Budgeted Transform Stream
```typescript
import { Transform, TransformCallback } from 'node:stream';

export class ByteBudgetedTransform extends Transform {
  constructor(maxMemoryBytes: number = 64 * 1024 * 1024) {
    super({
      objectMode: true,
      highWaterMark: maxMemoryBytes,
      writableByteLength(chunk: { html: string }) {
        return Buffer.byteLength(chunk.html, 'utf-8');
      },
      readableByteLength(chunk: { html: string }) {
        return Buffer.byteLength(chunk.html, 'utf-8');
      }
    });
  }

  _transform(chunk: { html: string }, encoding: BufferEncoding, callback: TransformCallback): void {
    // Process chunk without buffering entire collection in heap
    this.push(chunk);
    callback();
  }
}
```

---

## 4. Rust (Tokio Semaphore-Gated Channel)

### Before: Fixed-Length Tokio MPSC Channel
```rust
// NAIVE: 100 items of 20MB strings = 2.0 GB allocation
let (tx, mut rx) = tokio::sync::mpsc::channel::<Vec<u8>>(100);
```

### After: Byte-Budgeted Token Semaphore
```rust
use std::sync::Arc;
use tokio::sync::{mpsc, Semaphore};

pub struct ByteBudgetSender {
    tx: mpsc::Sender<Vec<u8>>,
    semaphore: Arc<Semaphore>,
    max_budget: usize,
}

pub struct ByteBudgetReceiver {
    rx: mpsc::Receiver<Vec<u8>>,
    semaphore: Arc<Semaphore>,
}

pub fn byte_budget_channel(max_bytes: usize) -> (ByteBudgetSender, ByteBudgetReceiver) {
    let semaphore = Arc::new(Semaphore::new(max_bytes));
    let (tx, rx) = mpsc::channel(256);
    (
        ByteBudgetSender { tx, semaphore: semaphore.clone(), max_budget: max_bytes },
        ByteBudgetReceiver { rx, semaphore },
    )
}

impl ByteBudgetSender {
    pub async fn send(&self, payload: Vec<u8>) -> Result<(), mpsc::error::SendError<Vec<u8>>> {
        let size = payload.len().min(self.max_budget) as u32;
        // Backpressure point: acquire byte permits before pushing
        let permit = self.semaphore.acquire_many(size).await.unwrap();
        permit.forget(); // Consumed into channel; returned on read
        self.tx.send(payload).await
    }
}

impl ByteBudgetReceiver {
    pub async fn recv(&mut self) -> Option<Vec<u8>> {
        if let Some(payload) = self.rx.recv().await {
            let size = payload.len() as u32;
            self.semaphore.add_permits(size as usize);
            Some(payload)
        } else {
            None
        }
    }
}
```
