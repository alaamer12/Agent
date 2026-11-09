# Result Durability & Salvage

## The Dual-Entry Guarantee
To prevent data loss from interrupted network downloads or expired vendor URLs, the engine implements a dual-entry ledger in `.generate/results.jsonl`.

### 1. `kind: received` (Written immediately upon API response)
The moment an asynchronous polling job returns or a synchronous payload is parsed, the engine appends raw URLs to disk before attempting to download:
```json
{
  "kind": "received",
  "timestamp": 1731150000,
  "job_id": "job_xyz789",
  "provider": "kovapi",
  "media": "video",
  "urls": ["https://img.kovapi.com/v/video-123.mp4"]
}
```

### 2. `kind: done` (Written after atomic download)
Once bytes are downloaded to a temporary file and atomically renamed (`os.replace`) to the final output file, the completion record is appended:
```json
{
  "kind": "done",
  "timestamp": 1731150005,
  "job_id": "job_xyz789",
  "url": "https://img.kovapi.com/v/video-123.mp4",
  "path": "generate-out/intro-01.mp4"
}
```

## Atomic Writes
Downloads are never written directly to their target paths. Bytes stream into `.tmp` files and are swapped into place via atomic filesystem rename operations. If a process crashes mid-stream, partial or corrupted media files never appear in output directories.

## Salvage Mode (`--salvage`)
If a run is terminated or network fails during downloading:
```bash
python scripts/generate.py --salvage
```
The engine inspects `.generate/results.jsonl`, identifies URLs that have a `received` entry without a matching `done` entry on disk, and attempts to re-download them.
- If the URL is still active, it saves the file and records the `done` entry.
- If the vendor link has expired (e.g. past KovAPI 7-day retention or xAI 1-day retention), it marks the entry as unrecoverable with rc 1.
