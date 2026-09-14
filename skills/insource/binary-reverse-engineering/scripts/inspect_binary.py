#!/usr/bin/env python3
"""
inspect_binary.py - Universal Software & Binary Inspector

Dissects archives (ZIP, JAR, APK, TAR, ASAR), bytecode (.class, .dex), native binaries
(PE, ELF, Mach-O), web/JS bundles, SQLite databases, and directory trees for hidden
endpoints, tokens, schema definitions, and constant strings.
"""

import sys
import os
import re
import json
import struct
import base64
import zipfile
import tarfile
import argparse

# Ensure standard output handles Unicode on Windows consoles safely
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

def detect_file_type(data):
    """Detect binary or archive format from magic bytes."""
    if len(data) < 4:
        return "unknown"
    if data[:4] == b'\xca\xfe\xba\xbe':
        return "jvm_class_or_macho_fat"
    if data[:2] == b'PK':
        return "zip_or_jar"
    if data[:2] == b'MZ':
        return "pe_windows"
    if data[:4] == b'\x7fELF':
        return "elf_linux"
    if data[:4] in (b'\xfe\xed\xfa\xce', b'\xfe\xed\xfa\xcf', b'\xce\xfa\xed\xfe', b'\xcf\xfa\xed\xfe'):
        return "macho"
    if data[:8] == b'dex\n035\x00' or data[:4] == b'dex\n':
        return "android_dex"
    if len(data) >= 16 and data[:15] == b'SQLite format 3':
        return "sqlite_db"
    return "raw_or_text"

def parse_class_constant_pool(data):
    """Parse UTF-8 strings from JVM .class constant pool without 3rd party deps."""
    if len(data) < 10 or data[:4] != b'\xca\xfe\xba\xbe':
        return []
    strings = []
    try:
        cp_count = int.from_bytes(data[8:10], 'big')
        pos = 10
        i = 1
        while i < cp_count and pos < len(data):
            tag = data[pos]
            pos += 1
            if tag == 1:  # CONSTANT_Utf8
                length = int.from_bytes(data[pos:pos+2], 'big')
                pos += 2
                val = data[pos:pos+length].decode('utf-8', errors='replace')
                strings.append(val)
                pos += length
            elif tag in (3, 4):  # Integer, Float
                pos += 4
            elif tag in (5, 6):  # Long, Double (takes two CP entries)
                pos += 8
                i += 1
            elif tag in (7, 8, 16, 19, 20):  # Class, String, MethodType, Module, Package
                pos += 2
            elif tag in (9, 10, 11, 12, 18):  # Ref, NameAndType, InvokeDynamic
                pos += 4
            elif tag == 15:  # MethodHandle
                pos += 3
            else:
                break
            i += 1
    except Exception:
        pass
    return strings

def extract_strings(data, min_len=4):
    """Extract ASCII and UTF-16 strings from arbitrary binary buffers."""
    ascii_re = re.compile(rb'[\x20-\x7e]{' + str(min_len).encode() + rb',}')
    ascii_matches = [m.decode('ascii', errors='replace') for m in ascii_re.findall(data)]
    
    utf16_re = re.compile(rb'(?:[\x20-\x7e]\x00){' + str(min_len).encode() + rb',}')
    utf16_matches = [m.decode('utf-16le', errors='replace') for m in utf16_re.findall(data)]
    
    return list(dict.fromkeys(ascii_matches + utf16_matches))

def decode_jwt_payload(token_str):
    """Decode JWT payload unverified for debugging claims."""
    parts = token_str.split('.')
    if len(parts) >= 2:
        try:
            payload_b64 = parts[1]
            rem = len(payload_b64) % 4
            if rem > 0:
                payload_b64 += '=' * (4 - rem)
            decoded = base64.urlsafe_b64decode(payload_b64.encode('ascii'))
            return json.loads(decoded.decode('utf-8', errors='replace'))
        except Exception:
            pass
    return None

def scan_archive(file_path, pattern=None, dump_entry=None, extract_urls=False):
    """Scan ZIP/JAR/APK files for entry patterns or string contents."""
    if not zipfile.is_zipfile(file_path):
        print(f"[-] '{file_path}' is not a valid zip/jar archive.")
        return

    with zipfile.ZipFile(file_path, 'r') as z:
        names = z.namelist()
        print(f"[*] Archive contains {len(names)} entries.")
        
        if dump_entry:
            matching = [n for n in names if dump_entry.lower() in n.lower()]
            for name in matching:
                print(f"\n--- Entry: {name} ({z.getinfo(name).file_size} bytes) ---")
                content = z.read(name)
                if name.endswith('.class'):
                    strings = parse_class_constant_pool(content)
                    print(f"[*] Constant Pool Strings ({len(strings)}):")
                    for s in strings:
                        if not pattern or re.search(pattern, s, re.IGNORECASE):
                            print(f"    {s}")
                else:
                    strings = extract_strings(content)
                    print(f"[*] Extracted Strings ({len(strings)}):")
                    for s in strings:
                        if not pattern or re.search(pattern, s, re.IGNORECASE):
                            print(f"    {s}")
            return

        if pattern:
            print(f"[*] Matching entry names against pattern: '{pattern}'")
            matched_entries = [n for n in names if re.search(pattern, n, re.IGNORECASE)]
            for n in matched_entries:
                print(f"    [MATCH] {n}")
            print(f"[*] Total matching entries: {len(matched_entries)}")

        if extract_urls:
            print(f"[*] Scanning archive contents for URLs and API endpoints...")
            url_re = re.compile(r'https?://[a-zA-Z0-9.-]+(?:/[a-zA-Z0-9_.~!$&\'()*+,;=:@%/-]*)?')
            found_urls = set()
            for name in names:
                if name.endswith(('.class', '.dex', '.json', '.properties', '.xml', '.txt', '.js')):
                    try:
                        content = z.read(name)
                        if name.endswith('.class'):
                            strings = parse_class_constant_pool(content)
                        else:
                            strings = extract_strings(content)
                        for s in strings:
                            for url in url_re.findall(s):
                                found_urls.add((url, name))
                    except Exception:
                        pass
            for url, src in sorted(found_urls):
                print(f"    {url}  (from {src})")

def scan_directory(dir_path, pattern=None, extract_urls=False):
    """Recursively scan directory of installed applications or unpacked modules."""
    print(f"[*] Recursively scanning directory: {dir_path}")
    count = 0
    url_re = re.compile(r'https?://[a-zA-Z0-9.-]+(?:/[a-zA-Z0-9_.~!$&\'()*+,;=:@%/-]*)?')
    found_urls = set()
    for root, _, files in os.walk(dir_path):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, dir_path)
            count += 1
            if pattern and re.search(pattern, rel_path, re.IGNORECASE):
                print(f"    [MATCH FILE] {rel_path}")
            if extract_urls and f.endswith(('.json', '.js', '.ts', '.py', '.properties', '.xml', '.txt', '.yaml', '.yml', '.env', '.class')):
                try:
                    with open(full_path, 'rb') as fp:
                        raw = fp.read(1024 * 512) # Read first 512KB
                    if f.endswith('.class'):
                        strings = parse_class_constant_pool(raw)
                    else:
                        strings = extract_strings(raw)
                    for s in strings:
                        for u in url_re.findall(s):
                            found_urls.add((u, rel_path))
                except Exception:
                    pass
    print(f"[*] Scanned {count} files in directory.")
    if extract_urls and found_urls:
        print("[*] Discovered URLs:")
        for u, src in sorted(found_urls):
            print(f"    {u}  (from {src})")

def main():
    parser = argparse.ArgumentParser(description="Universal Software & Binary Inspector")
    parser.add_argument("path", help="Path to archive, binary, directory, or data file")
    parser.add_argument("-p", "--pattern", help="Regex pattern to search inside entries or strings")
    parser.add_argument("-e", "--entry", help="Target specific entry inside archive to inspect")
    parser.add_argument("-u", "--urls", action="store_true", help="Extract all HTTP/HTTPS endpoints and URLs")
    parser.add_argument("-s", "--strings", action="store_true", help="Extract raw strings from file")
    parser.add_argument("-j", "--jwt", help="Decode and inspect an unverified JWT token payload")

    args = parser.parse_args()

    if args.jwt:
        payload = decode_jwt_payload(args.jwt)
        print("[*] Decoded JWT Payload:")
        print(json.dumps(payload, indent=2) if payload else "[-] Failed to decode JWT payload")
        return

    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' not found.")
        sys.exit(1)

    if os.path.isdir(args.path):
        scan_directory(args.path, pattern=args.pattern, extract_urls=args.urls)
        return

    if os.path.isfile(args.path):
        if zipfile.is_zipfile(args.path):
            scan_archive(args.path, pattern=args.pattern, dump_entry=args.entry, extract_urls=args.urls)
            return

        with open(args.path, 'rb') as f:
            header = f.read(512)
        ftype = detect_file_type(header)
        print(f"[*] Detected file format: {ftype}")

        if ftype == "jvm_class_or_macho_fat" and args.path.endswith('.class'):
            with open(args.path, 'rb') as f:
                data = f.read()
            strings = parse_class_constant_pool(data)
            print(f"[*] Extracted {len(strings)} strings from JVM class constant pool:")
            for s in strings:
                if not args.pattern or re.search(args.pattern, s, re.IGNORECASE):
                    print(f"    {s}")
        else:
            with open(args.path, 'rb') as f:
                data = f.read()
            strings = extract_strings(data)
            print(f"[*] Extracted {len(strings)} strings:")
            for s in strings:
                if not args.pattern or re.search(args.pattern, s, re.IGNORECASE):
                    print(f"    {s}")

if __name__ == "__main__":
    main()
