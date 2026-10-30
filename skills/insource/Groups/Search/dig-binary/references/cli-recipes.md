# CLI Recipes & One-Liner Cheatsheet

This reference provides production-ready, zero-dependency one-liners for PowerShell (Windows), Bash (Linux/macOS), and standard Python (`python -c`) that allow an agent or engineer to immediately dissect systems, binaries, archives, and network routes without installing external reverse-engineering tools.

---

## 1. System Footprint & Entry Point Tracing

### Finding Binaries & Tracing Shims
- **Windows (PowerShell)**:
  ```powershell
  # Find where an executable or shim is installed
  (Get-Command <app_name>).Source

  # Read shim/batch script to locate actual payload, data dir, and versions
  Get-Content (Get-Command <app_name>).Source | Select-String -Pattern "share|data|version|current|\.jar|\.exe" -Context 1,1
  ```
- **Linux/macOS (Bash)**:
  ```bash
  # Resolve symlinks to target real script/binary
  readlink -f $(which <app_name>)

  # Inspect wrapper script
  grep -Ei "export|dir|share|app|version" $(which <app_name>)
  ```

### Inspecting Running Processes & Arguments
- **Windows (PowerShell)**:
  ```powershell
  # Get exact command-line arguments of a running process (uncovers internal ports/flags)
  Get-CimInstance Win32_Process -Filter "Name like '%<app_name>%'" | Select-Object ProcessId, CommandLine | Format-List
  ```
- **Linux/macOS (Bash)**:
  ```bash
  ps aux | grep -i "<app_name>" | grep -v grep
  ```

---

## 2. In-Memory Archive Inspection (Zero-Disk Footprint)

Inspect multi-hundred megabyte `.jar`, `.zip`, `.apk`, `.tar` packages without extracting files to disk.

### Search Entry Names in ZIP/JAR/APK
- **Python one-liner (Cross-Platform)**:
  ```bash
  python -c "import zipfile, sys; [print(n) for n in zipfile.ZipFile(sys.argv[1]).namelist() if sys.argv[2].lower() in n.lower()]" <archive.jar> <keyword>
  ```
- **Windows (PowerShell - .NET Native)**:
  ```powershell
  Add-Type -AssemblyName System.IO.Compression.FileSystem
  [System.IO.Compression.ZipFile]::OpenRead("<archive.jar>").Entries | Where-Object { $_.FullName -like "*<keyword>*" } | Select-Object FullName, Length
  ```

### Read Specific Text/Config File Directly from Inside an Archive
- **Python one-liner**:
  ```bash
  python -c "import zipfile, sys; print(zipfile.ZipFile(sys.argv[1]).read(sys.argv[2]).decode('utf-8', errors='replace'))" <archive.jar> <internal/path/to/file.json>
  ```

---

## 3. JVM Bytecode & Constant Pool Carving

Extract string constants, enum definitions, error codes, and field descriptors directly from `.class` files.

### Fast Constant-Pool String Dump from Archive
Extract all strings from a specific class inside a `.jar` without extracting it to disk:
```bash
python -c "
import zipfile, sys
z = zipfile.ZipFile(sys.argv[1])
for name in z.namelist():
    if sys.argv[2].lower() in name.lower() and name.endswith('.class'):
        data = z.read(name)
        if data[:4] == b'\xca\xfe\xba\xbe':
            cp_count = int.from_bytes(data[8:10], 'big')
            pos, i, strings = 10, 1, []
            while i < cp_count and pos < len(data):
                tag = data[pos]
                pos += 1
                if tag == 1:
                    l = int.from_bytes(data[pos:pos+2], 'big')
                    pos += 2
                    strings.append(data[pos:pos+l].decode('utf-8', errors='replace'))
                    pos += l
                elif tag in (3, 4): pos += 4
                elif tag in (5, 6): pos += 8; i += 1
                elif tag in (7, 8, 16, 19, 20): pos += 2
                elif tag in (9, 10, 11, 12, 18): pos += 4
                elif tag == 15: pos += 3
                else: break
                i += 1
            print(f'=== {name} ===')
            for s in strings:
                if len(s) > 1 and not s.startswith(('Ljava/', 'java/', '()')):
                    print('  ', s)
" <archive.jar> <ClassPattern>
```

---

## 4. Binary String Carving (ASCII + UTF-16LE + Regex)

Native binaries (`.exe`, `.dll`, `.so`) and packaged bundles frequently encode strings in UTF-16 LE or ASCII.

### Carve URLs and API Routes Across Any File or Binary
- **Python one-liner**:
  ```bash
  python -c "import re, sys; data = open(sys.argv[1], 'rb').read(); urls = set(re.findall(rb'https?://[a-zA-Z0-9.-]+(?:/[a-zA-Z0-9_.~!$&\'()*+,;=:@%/-]*)?', data)); [print(u.decode('latin1')) for u in urls]" <binary_file>
  ```

### Carve Enum / Constant-Like Identifiers
Extract screaming snake-case constants (e.g., error codes `FORBIDDEN_EMAIL`, `EXPIRED`, `INVALID_TOKEN`):
- **Python one-liner**:
  ```bash
  python -c "import re, sys; data = open(sys.argv[1], 'rb').read(); tokens = set(re.findall(rb'\b[A-Z][A-Z0-9_]{3,30}\b', data)); [print(t.decode('ascii')) for t in sorted(tokens)]" <binary_or_class_file>
  ```

### Carve Strings from Windows Binary via PowerShell
```powershell
$bytes = [System.IO.File]::ReadAllBytes("<file.exe>")
$text = [System.Text.Encoding]::ASCII.GetString($bytes)
[regex]::Matches($text, "https?://[a-zA-Z0-9./_-]+") | ForEach-Object { $_.Value } | Select-Object -Unique
```

---

## 5. Network & Dynamic Port Snooping

Find which internal ports, proxies, or gateways a local service is listening on:

- **Windows (PowerShell)**:
  ```powershell
  # Find listening ports and owning PID
  Get-NetTCPConnection -State Listen | Select-Object LocalAddress, LocalPort, OwningProcess | Sort-Object LocalPort
  ```
- **Linux/macOS (Bash)**:
  ```bash
  ss -tulpn | grep LISTEN
  # or
  lsof -iTCP -sTCP:LISTEN -P -n
  ```

---

## 6. Token & Secret Inspection

### Fast Unverified JWT Payload Inspection
Decode claims, audience, scopes, and expiration without external tools:
- **Python one-liner**:
  ```bash
  python -c "import sys, base64, json; p = sys.argv[1].split('.')[1]; p += '=' * ((4 - len(p) % 4) % 4); print(json.dumps(json.loads(base64.urlsafe_b64decode(p)), indent=2))" "<JWT_TOKEN_STRING>"
  ```
- **PowerShell one-liner**:
  ```powershell
  $token = "<JWT_TOKEN_STRING>"
  $payload = $token.Split('.')[1]
  $payload += "=" * ((4 - $payload.Length % 4) % 4)
  [System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($payload))
  ```

---

## 7. Dynamic Probing & PoC Synthesizers

Once an endpoint, method, and auth token are found, fire test probes directly from the terminal.

### Probe Endpoint with JSON Payload & Auth Header
- **cURL / Bash**:
  ```bash
  curl -s -X POST "https://<host>/api/<endpoint>" \
    -H "Authorization: Bearer <token>" \
    -H "Content-Type: application/json" \
    -d '{"code": "TEST"}' | jq .
  ```
- **PowerShell**:
  ```powershell
  $headers = @{
      "Authorization" = "Bearer <token>"
      "Content-Type"  = "application/json"
  }
  $body = @{ code = "TEST" } | ConvertTo-Json
  Invoke-RestMethod -Uri "https://<host>/api/<endpoint>" -Method Post -Headers $headers -Body $body
  ```
- **Python one-liner (Zero 3rd party deps)**:
  ```bash
  python -c "import urllib.request, json, sys; req = urllib.request.Request(sys.argv[1], data=sys.argv[3].encode('utf-8'), headers={'Authorization': 'Bearer ' + sys.argv[2], 'Content-Type': 'application/json'}); print(urllib.request.urlopen(req).read().decode('utf-8'))" "<url>" "<token>" '{"code":"TEST"}'
  ```
