# Bytecode & Archive Analysis Reference

This guide provides deep technical patterns for dissecting binaries, archives, and bytecode without full decompilation toolchains.

---

## 1. JVM Bytecode & Class Format (`.class`)

### Header and Structure
A Java/Kotlin `.class` file begins with the 4-byte magic signature `0xCAFEBABE`, followed by:
- Minor version (2 bytes), Major version (2 bytes)
  - Java 8: 52 (`0x0034`)
  - Java 11: 55 (`0x0037`)
  - Java 17: 61 (`0x003D`)
  - Java 21: 65 (`0x0041`)
- Constant Pool Count (`u2`) and Constant Pool entries:
  - Strings, class names, method names, descriptor signatures, field names, utf8 literals.
- Access flags, `this_class`, `super_class`, `interfaces_count`, `fields_count`, `methods_count`, `attributes_count`.

### Kotlin Metadata & Intrinsics
Kotlin compiler embeds rich metadata in `.class` files via the `@kotlin.Metadata` annotation:
- `k`: Kind (1 = Class, 2 = File/Facade, 3 = Synthetic, 4 = Multi-file facade, 5 = Multi-file part).
- `mv`: Metadata version.
- `d1`: Protobuf-encoded binary string array containing exact Kotlin declarations, nullability, typealiases, and default parameters.
- `d2`: String array referenced by `d1`.
- Kotlin generated classes often include synthetic inner classes:
  - `<Class>$Companion.class`: Companion objects
  - `<Class>$$serializer.class`: kotlinx.serialization generated serializer
  - `<File>Kt.class`: Top-level functions and extension functions

### Inspecting JVM Bytecode
1. **Using `javap` (if JDK installed)**:
   ```bash
   javap -c -p -constants PathToClass.class
   ```
2. **Pure Python Quick Parser**:
   Extract all UTF-8 constants from the constant pool without needing a JVM or third-party packages:
   ```python
   def read_constant_pool_strings(class_bytes):
       magic = class_bytes[:4]
       if magic != b'\xca\xfe\xba\xbe':
           return []
       # Read major/minor, then constant pool count
       cp_count = int.from_bytes(class_bytes[8:10], 'big')
       pos = 10
       strings = []
       i = 1
       while i < cp_count:
           tag = class_bytes[pos]
           pos += 1
           if tag == 1: # CONSTANT_Utf8
               length = int.from_bytes(class_bytes[pos:pos+2], 'big')
               pos += 2
               val = class_bytes[pos:pos+length].decode('utf-8', errors='replace')
               strings.append(val)
               pos += length
           elif tag in (3, 4): # Integer, Float
               pos += 4
           elif tag in (5, 6): # Long, Double (takes 2 entries)
               pos += 8
               i += 1
           elif tag in (7, 8, 16, 19, 20): # Class, String, MethodType, Module, Package
               pos += 2
           elif tag in (9, 10, 11, 12, 18): # Ref, NameAndType, InvokeDynamic
               pos += 4
           elif tag == 15: # MethodHandle
               pos += 3
           else:
               break
           i += 1
       return strings
   ```

---

## 2. Archive Introspection (ZIP, JAR, AAR, APK, WAR, WHEEL)

### Nested Archives
Modern distributions package dependencies inside fat-jars or nested archives:
- Spring Boot: `BOOT-INF/classes/` and `BOOT-INF/lib/*.jar`
- Android: `classes.dex`, `classes2.dex` (Dalvik Executable)
- JetPack / Compose Desktop / Native Bundles: Executable shim + `app/*.jar` or embedded shared libraries (`.dll`, `.so`, `.dylib`).

### Fast Scanning Without Full Extraction
Streaming index inspection prevents disk bloat and keeps execution fast:
```python
import zipfile

def search_nested_archives(archive_path, keyword):
    with zipfile.ZipFile(archive_path, 'r') as z:
        for name in z.namelist():
            if keyword.lower() in name.lower():
                print(f"[FOUND ENTRY] {name}")
            if name.endswith(('.jar', '.zip')):
                # In-memory inspection of nested zip
                try:
                    nested_bytes = io.BytesIO(z.read(name))
                    with zipfile.ZipFile(nested_bytes) as nested_z:
                        for n_name in nested_z.namelist():
                            if keyword.lower() in n_name.lower():
                                print(f"[NESTED: {name}] {n_name}")
                except Exception:
                    pass
```

---

## 3. String & Literal Extraction from Native Binaries (PE, ELF, Mach-O)

### File Headers
- **PE (Windows .exe / .dll)**: Begins with `MZ` (`0x4D 0x5A`), PE offset at `0x3C` (`PE\0\0`).
- **ELF (Linux)**: Begins with `0x7F 0x45 0x4C 0x46` (`\x7fELF`).
- **Mach-O (macOS)**: `0xFEEDFACE` (32-bit), `0xFEEDFACF` (64-bit), or `0xCAFEBABE` (Universal fat binary).

### Pattern-Based String Extraction
Extract printable ASCII and UTF-16 LE (common in Windows binaries) without external `strings` utility:
```python
import re

def extract_strings(file_bytes, min_len=4):
    # ASCII
    ascii_re = re.compile(rb'[\x20-\x7e]{' + str(min_len).encode() + rb',}')
    ascii_matches = [m.decode('ascii') for m in ascii_re.findall(file_bytes)]
    
    # UTF-16 LE
    utf16_re = re.compile(rb'(?:[\x20-\x7e]\x00){' + str(min_len).encode() + rb',}')
    utf16_matches = [m.decode('utf-16le', errors='replace') for m in utf16_re.findall(file_bytes)]
    
    return ascii_matches + utf16_matches
```

---

## 4. Reverse Engineering Hidden Network Endpoints

1. **Search for URL schemes & paths**:
   - Regex patterns: `https?://[a-zA-Z0-9.-]+(?:/[a-zA-Z0-9_.~!$&'()*+,;=:@%/-]*)?`
   - Common path fragments: `/api/`, `/v1/`, `/v2/`, `/auth/`, `/trial/`, `/activate`, `/token`, `/license`, `/gateway`, `/cloud`.
2. **Correlate Endpoints with Payload Models**:
   - In Kotlin/Java: Search for companion classes or serializers ending in `$$serializer`, `Request`, `Response`, `DTO`.
   - Inspect JSON field names in string constants (e.g. `"code"`, `"token"`, `"user_id"`).
3. **Trace Authentication Headers**:
   - Search for `"Authorization"`, `"Bearer"`, `"X-Api-Key"`, `"User-Agent"`, `"Proxy-Authorization"`.
   - Check how tokens are parsed: JWT (starts with `ey...`), Base64, UUID, or opaque session IDs.
