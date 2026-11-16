# Polyglot Walkthrough: Zero-Cache Streaming I/O & Page-Cache Eviction

Reading entire files into memory (`file.read()`) during HTTP upload/download or data export generates instant memory spikes equal to the file size. Additionally, reading/writing files fills the kernel page cache unless evicted with `posix_fadvise`.

Below are idiomatic before-and-after streaming implementations across **Python**, **Go**, **Node.js/TypeScript**, and **Rust**.

---

## 1. Python (CPython 3.11+ / Starlette ASGI)

### Before: Full-File Memory Read
```python
# NAIVE: Reading 400 MB export into RAM = Instant OOM!
@app.get("/export")
async def download():
    with open("dataset.parquet", "rb") as f:
        data = f.read() # Allocates 400 MB in heap
    return Response(content=data, media_type="application/octet-stream")
```

### After: 64 KB Chunked Streaming Response with Page Cache Dropping
```python
import os
import aiofiles
from starlette.responses import StreamingResponse

CHUNK_SIZE = 64 * 1024 # 64 KB constant window

async def stream_file_chunks(filepath: str):
    try:
        async with aiofiles.open(filepath, "rb") as f:
            while True:
                chunk = await f.read(CHUNK_SIZE)
                if not chunk:
                    break
                yield chunk
    finally:
        # Evict file from kernel page cache after transfer completes
        if hasattr(os, "posix_fadvise"):
            try:
                fd = os.open(filepath, os.O_RDONLY)
                os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED)
                os.close(fd)
            except Exception:
                pass

def export_file(filepath: str) -> StreamingResponse:
    stat = os.stat(filepath)
    return StreamingResponse(
        stream_file_chunks(filepath),
        media_type="application/octet-stream",
        headers={"Content-Length": str(stat.st_size)}
    )
```

---

## 2. Go (1.21+ / `io.CopyBuffer` with `syscall.Fadvise`)

### Before: `os.ReadFile` Buffering
```go
// NAIVE: Buffering whole file into memory
func DownloadHandler(w http.ResponseWriter, r *http.Request) {
    data, _ := os.ReadFile("dataset.parquet") // Allocates full size
    w.Write(data)
}
```

### After: Bounded Buffer Copy with OS Cache Invalidation
```go
package streamer

import (
	"io"
	"net/http"
	"os"
	"syscall"
)

const BufferSize = 64 * 1024 // 64 KB

func StreamDownload(w http.ResponseWriter, r *http.Request, path string) {
	file, err := os.Open(path)
	if err != nil {
		http.Error(w, "Not found", http.StatusNotFound)
		return
	}
	defer func() {
		// Drop kernel page cache for the served file on exit
		_ = syscall.Fadvise(int(file.Fd()), 0, 0, 4) // POSIX_FADV_DONTNEED = 4
		file.Close()
	}()

	stat, _ := file.Stat()
	w.Header().Set("Content-Type", "application/octet-stream")
	w.Header().Set("Content-Length", string(stat.Size()))

	// Fixed 64KB transfer buffer ensures constant memory footprint
	buf := make([]byte, BufferSize)
	_, _ = io.CopyBuffer(w, file, buf)
}
```

---

## 3. Node.js / TypeScript (`stream.pipeline`)

### Before: `fs.readFileSync` Memory Materialization
```typescript
// NAIVE: Reading full file into Node Buffer
app.get('/download', (req, res) => {
  const file = fs.readFileSync('dataset.parquet'); // 400 MB Buffer allocated!
  res.send(file);
});
```

### After: Backpressured Stream Pipeline
```typescript
import fs from 'node:fs';
import { pipeline } from 'node:stream/promises';
import { Request, Response } from 'express';

const CHUNK_SIZE = 64 * 1024; // 64 KB

export async function streamExport(req: Request, res: Response, filePath: string) {
  const stat = await fs.promises.stat(filePath);

  res.writeHead(200, {
    'Content-Type': 'application/octet-stream',
    'Content-Length': stat.size,
  });

  const sourceStream = fs.createReadStream(filePath, {
    highWaterMark: CHUNK_SIZE,
    autoClose: true,
  });

  try {
    // pipeline coordinates backpressure, ensures descriptor closure, and handles errors
    await pipeline(sourceStream, res);
  } catch (err) {
    if (!res.headersSent) {
      res.status(500).send('Stream error');
    }
  }
}
```

---

## 4. Rust (Axum & Tokio ReaderStream)

### Before: `tokio::fs::read`
```rust
// NAIVE: Reading complete vector into memory
let data = tokio::fs::read("dataset.parquet").await.unwrap();
```

### After: ReaderStream with Constant Capacity
```rust
use axum::{
    body::StreamBody,
    http::{header, HeaderMap, StatusCode},
    response::IntoResponse,
};
use tokio::fs::File;
use tokio_util::io::ReaderStream;

const CHUNK_SIZE: usize = 64 * 1024; // 64 KB

pub async fn stream_file_response(path: String) -> Result<impl IntoResponse, StatusCode> {
    let file = File::open(&path).await.map_err(|_| StatusCode::NOT_FOUND)?;
    let metadata = file.metadata().await.map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    // Stream wrapped in fixed 64 KB buffers
    let stream = ReaderStream::with_capacity(file, CHUNK_SIZE);
    let body = StreamBody::new(stream);

    let mut headers = HeaderMap::new();
    headers.insert(header::CONTENT_TYPE, "application/octet-stream".parse().unwrap());
    headers.insert(header::CONTENT_LENGTH, metadata.len().to_string().parse().unwrap());

    Ok((headers, body))
}
```
