# Polyglot Walkthrough: Disk-Spill & Sparse Offset Indexing

Holding hundreds of thousands of parsed entities in heap memory (`results: List[Record]`) triggers linear $O(N)$ growth. The **Disk-Spill Pattern** persists records sequentially to an append log while retaining only a compact offset index in RAM.

---

## 1. Python (CPython 3.11+)

### Before: Unbounded In-Memory Collection
```python
# NAIVE: Accumulating 100,000 parsed objects in heap
results: list[dict] = []

def on_entity_parsed(data: dict):
    results.append(data) # 100k records * 15 KB = 1.5 GB RAM!
```

### After: Disk-Spill with Lightweight Offset Index (`ProfileSpill`)
```python
from pathlib import Path
import orjson

class DiskSpillIndex:
    """Appends records to disk and keeps only file offsets in memory."""
    def __init__(self, backing_file: Path):
        self.backing_file = backing_file
        self._offsets: dict[str, int] = {}
        self._writer = open(self.backing_file, "wb")
        self._reader = None

    def add(self, key: str, record: dict) -> bool:
        if key in self._offsets:
            return False
        offset = self._writer.tell()
        # Serialize and write line-delimited payload
        payload = orjson.dumps(record) + b"\n"
        self._writer.write(payload)
        self._offsets[key] = offset
        return True

    def iter_records(self):
        """Streams records sequentially without loading full dataset into RAM."""
        self._writer.flush()
        if self._reader is None:
            self._reader = open(self.backing_file, "rb")
        for offset in self._offsets.values():
            self._reader.seek(offset)
            line = self._reader.readline()
            yield orjson.loads(line)

    def close(self):
        self._writer.close()
        if self._reader:
            self._reader.close()
        if self.backing_file.exists():
            self.backing_file.unlink()
```

---

## 2. Go (1.21+)

### Before: Slice Appends in Heap
```go
// NAIVE: Accumulating parsed structs in a global slice
var parsedRecords []Record

func Process(r Record) {
    parsedRecords = append(parsedRecords, r) // GC pressure & heap bloat
}
```

### After: Append-Only Spiller with Map Index
```go
package spill

import (
	"bufio"
	"encoding/json"
	"os"
	"sync"
)

type DiskSpiller struct {
	file    *os.File
	writer  *bufio.Writer
	offsets map[string]int64
	curPos  int64
	mu      sync.Mutex
}

func NewDiskSpiller(path string) (*DiskSpiller, error) {
	f, err := os.Create(path)
	if err != nil {
		return nil, err
	}
	return &DiskSpiller{
		file:    f,
		writer:  bufio.NewWriterSize(f, 64*1024),
		offsets: make(map[string]int64),
	}, nil
}

func (s *DiskSpiller) Append(id string, data any) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	bytes, err := json.Marshal(data)
	if err != nil {
		return err
	}
	bytes = append(bytes, '\n')

	offset := s.curPos
	n, err := s.writer.Write(bytes)
	if err != nil {
		return err
	}

	s.offsets[id] = offset
	s.curPos += int64(n)
	return nil
}

func (s *DiskSpiller) Close() error {
	s.writer.Flush()
	return s.file.Close()
}
```

---

## 3. Node.js / TypeScript

### Before: Array Accumulation
```typescript
// NAIVE: Array pushing parsed models
const collection: any[] = [];
function save(record: any) {
  collection.push(record);
}
```

### After: File Append with Offset Index
```typescript
import * as fs from 'node:fs';

export class DiskSpillStore {
  private fd: number;
  private currentOffset = 0;
  private index: Map<string, number> = new Map();

  constructor(private path: string) {
    this.fd = fs.openSync(path, 'w+');
  }

  public add(key: string, record: object): void {
    if (this.index.has(key)) return;
    const buffer = Buffer.from(JSON.stringify(record) + '\n', 'utf-8');
    fs.writeSync(this.fd, buffer, 0, buffer.length, this.currentOffset);
    this.index.set(key, this.currentOffset);
    this.currentOffset += buffer.length;
  }

  public *iterate(): Generator<object> {
    for (const offset of this.index.values()) {
      const lineBuf = Buffer.alloc(64 * 1024);
      const bytesRead = fs.readSync(this.fd, lineBuf, 0, lineBuf.length, offset);
      const str = lineBuf.subarray(0, bytesRead).toString('utf-8');
      const line = str.split('\n')[0];
      yield JSON.parse(line);
    }
  }

  public close(): void {
    fs.closeSync(this.fd);
    fs.unlinkSync(this.path);
  }
}
```

---

## 4. Rust (Tokio & BufWriter)

### Before: Monolithic Vector
```rust
// NAIVE: Vector holding thousands of serialized records
static mut RECORDS: Vec<Record> = Vec::new();
```

### After: Sparse Index Spiller
```rust
use std::collections::HashMap;
use std::fs::{File, OpenOptions};
use std::io::{BufWriter, Seek, SeekFrom, Write};
use std::path::PathBuf;

pub struct DiskSpill {
    path: PathBuf,
    writer: BufWriter<File>,
    offsets: HashMap<String, u64>,
    current_offset: u64,
}

impl DiskSpill {
    pub fn new(path: PathBuf) -> std::io::Result<Self> {
        let file = OpenOptions::new().create(true).write(true).read(true).open(&path)?;
        Ok(Self {
            path,
            writer: BufWriter::with_capacity(64 * 1024, file),
            offsets: HashMap::new(),
            current_offset: 0,
        })
    }

    pub fn insert(&mut self, key: String, data: &[u8]) -> std::io::Result<()> {
        if self.offsets.contains_key(&key) {
            return Ok(());
        }
        let offset = self.current_offset;
        self.writer.write_all(data)?;
        self.writer.write_all(b"\n")?;
        
        let written = data.len() as u64 + 1;
        self.offsets.insert(key, offset);
        self.current_offset += written;
        Ok(())
    }

    pub fn flush(&mut self) -> std::io::Result<()> {
        self.writer.flush()
    }
}
```
