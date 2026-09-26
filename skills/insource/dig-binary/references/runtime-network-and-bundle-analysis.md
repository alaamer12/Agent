# Runtime, Network & Bundle Analysis Reference

This guide provides technical methodologies for reverse engineering modern application targets beyond JVM archives, including JavaScript/Web/Electron bundles, native binaries, network protocols, embedded storage, and dynamic runtime observation.

---

## 1. Web, JavaScript & Electron Bundles

Modern desktop and CLI tools frequently embed or run on Node.js/Chromium/Electron runtimes.

### Electron & ASAR Archives
- **Location**: Electron applications package code into `resources/app.asar` or `resources/app/`.
- **Structure**: ASAR is a simple archive format containing a JSON header describing directory offsets and sizes followed by raw file concatenations.
- **Extraction & Inspection**:
  - Without installing `npx asar`: The header starts with 4-byte size, 4-byte JSON size, followed by directory JSON tree.
  - Python quick extraction:
    ```python
    import json, struct

    def read_asar_header(asar_path):
        with open(asar_path, 'rb') as f:
            data = f.read(16)
            magic, header_size, header_len, json_len = struct.unpack('<IIII', data)
            json_bytes = f.read(json_len)
            return json.loads(json_bytes.decode('utf-8'))
    ```

### Minified JavaScript & Webpack Chunks
- **Source Map Carving**:
  - Look for `//# sourceMappingURL=<filename>.map` or inline `data:application/json;base64,...` at the bottom of `.js` files.
  - If `.map` files are present or hosted, full original source directory trees and unminified TypeScript/ES code can be reconstructed.
- **Module & Route Discovery**:
  - Search for string literals matching API routes (`/api/`, `/v1/`, etc.).
  - Search for client SDK definitions: `axios.create`, `fetch(`, `XMLHttpRequest`, `new WebSocket(`.
  - Search for React/Vue/Angular router definitions: `path:`, `routes: [`.

---

## 2. Native Binaries & Shared Libraries (PE, ELF, Mach-O)

When analyzing compiled native binaries (`.exe`, `.dll`, `.so`, `.dylib`):

### Metadata & Symbol Inspection
- **PE (Windows)**:
  - Inspect Import Address Table (IAT) and Export Table (`dumpbin /imports <file.exe>` or PowerShell script).
  - Uncovers which system APIs are called (e.g., `WinHttpOpen`, `RegOpenKeyExW`, `CreateProcessW`).
- **ELF (Linux)**:
  - Inspect dynamic sections: `readelf -d <file>`, `objdump -p <file>`.
  - Exported/imported symbols: `nm -D <file>` or string extraction from `.dynsym` / `.dynstr`.
- **Mach-O (macOS)**:
  - Load commands, linked dylibs: `otool -L <file>`, `nm -m <file>`.

### String Recovery Techniques
- Plain ASCII (`[\x20-\x7e]{4,}`).
- UTF-16 Little Endian (common for Windows strings: `[\x20-\x7e]\x00`).
- Base64 chunks matching URL/JSON patterns (`eyJ...` for JWTs).

---

## 3. Network Protocol & API Reverse Engineering

### HTTP / REST / GraphQL
1. **Endpoint Reconstruction**:
   - Extract base URLs and URI fragments from configuration files (`config.json`, `.env`, registry, hardcoded strings).
   - Form full URLs: `<base_url> + <route_path>`.
2. **Authentication Flow Detection**:
   - Headers: `Authorization: Bearer <token>`, `X-Api-Key`, `Cookie: session=...`.
   - Token types:
     - JWT: Decode payload (`base64url(payload)`) without signature verification to inspect user IDs, roles, expiration, and issuer claims.
     - Opaque tokens: Look for token exchange or refresh endpoints (`/oauth/token`, `/api/auth/refresh`).
3. **GraphQL Introspection**:
   - Probe endpoint with standard introspection query:
     `{"query": "{ __schema { types { name fields { name } } } }"}`
   - If enabled, yields complete backend schema, queries, mutations, and types.

### Protobuf, gRPC & Binary Formats
- **Protocol Buffers Wire Format**:
  - Protobuf is structured as `(field_number << 3) | wire_type`.
  - Wire types:
    - 0: Varint (int32, int64, bool, enum)
    - 1: 64-bit (fixed64, double)
    - 2: Length-delimited (string, bytes, embedded messages, packed repeated)
    - 5: 32-bit (fixed32, float)
  - `protoc --decode_raw` or Python parsers can parse serialized Protobuf messages without `.proto` definitions.
- **gRPC Framing**:
  - gRPC over HTTP/2 uses a 5-byte frame prefix: 1 byte compressed flag (`0x00`) + 4 bytes big-endian message length, followed by Protobuf payload.
- **WebSockets**:
  - Look for heartbeat/ping frames, opcode types, and JSON-RPC / message dispatch tables.

---

## 4. Local Data Stores & Persistence Layers

Applications frequently store cache, credentials, session states, and schemas locally:

### SQLite Databases
- Standard header starts with string `SQLite format 3\000`.
- Standard inspection via CLI:
  ```bash
  sqlite3 <path_to_db> ".tables"
  sqlite3 <path_to_db> ".schema <table_name>"
  ```
- Uncovers internal data models, offline queues, schema migrations, and persisted tokens.

### Key-Value Stores (LevelDB, RocksDB, IndexedDB)
- Chrome, Electron, and many native apps store local web storage in LevelDB (`.ldb` and `.log` files).
- Text strings and JSON payloads can be carved directly from `.ldb` files using string extraction.

---

## 5. Dynamic Runtime Observation & Interception

When static analysis is inconclusive due to packing, encryption, or heavy obfuscation:

### Process & Environment Snooping
1. **Environment & Arguments**:
   - Inspect command-line invocation and child process spawning (`wmic process get CommandLine`, `ps -ef`, `ProcMon`).
   - Look for config flags passed via hidden CLI switches or env variables.
2. **File & Registry I/O Tracing**:
   - Windows: Process Monitor (ProcMon) / ETW traces file reads, writes, and registry lookups.
   - Linux: `strace -f -e trace=file,network <cmd>`.
   - macOS: `fs_usage`, `dtruss`.

### Local Traffic Interception
1. **Loopback & Proxy Probing**:
   - Check if application respects `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY` environment variables.
   - Configure local intercepting proxy (e.g. mitmproxy, Fiddler, Charles) with trusted root certificate.
2. **Network Probing via PoC**:
   - Once an endpoint, header contract, and auth token are deduced, synthesize a standalone probe (Python / curl) to confirm live server behavior.
