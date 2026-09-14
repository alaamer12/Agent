#!/usr/bin/env python3
"""
collab_log.py - generic, dependency-free, cross-platform helper for a file-based
shared workspace used by the "contribute-agents" skill.

Provides two operations for subagents that communicate by running shell commands
against a plain-text log file:

    python collab_log.py read  --file <path>
    python collab_log.py send  --file <path> --sender NAME --content "..."
    python collab_log.py init  --file <path>

Guarantees:
    - Concurrent "send" calls from independent processes are safely serialized via an
      OS-level file lock (one lock file per log file), so no message is lost.
    - Each commit is atomic: the new log content is written to a temp file and then
      moved into place with an atomic rename, so no reader ever sees a partial write.
    - Every message gets a monotonically increasing sequence number (authoritative
      ordering) and a high-precision ISO-8601 UTC timestamp generated at commit time
      (not trusted from the caller).
    - New messages are inserted at the top of the file (most-recent-first).

Only use this script if your runtime lets subagents actually execute shell commands
against a shared filesystem. Otherwise, relay messages yourself as described in
references/protocol.md.
"""
import os
import sys
import time
import argparse
from datetime import datetime, timezone

try:
    import msvcrt
    _PLATFORM = "windows"
except ImportError:
    import fcntl
    _PLATFORM = "posix"


def get_paths(target_file):
    conv_file = os.path.abspath(target_file)
    lock_file = conv_file + ".lock"
    return conv_file, lock_file


def acquire_lock(lock_file):
    lock_fd = os.open(lock_file, os.O_CREAT | os.O_RDWR)
    if _PLATFORM == "windows":
        while True:
            try:
                msvcrt.locking(lock_fd, msvcrt.LK_NBLCK, 1)
                return lock_fd
            except OSError:
                time.sleep(0.01)
    else:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        return lock_fd


def release_lock(lock_fd):
    try:
        if _PLATFORM == "windows":
            os.lseek(lock_fd, 0, os.SEEK_SET)
            msvcrt.locking(lock_fd, msvcrt.LK_UNLCK, 1)
        else:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
    finally:
        os.close(lock_fd)


def parse_messages(content):
    if not content.strip():
        return []
    raw_blocks = content.strip().split("\n---\n")
    messages = []
    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.splitlines()
        seq = None
        sent_at = None
        sender = None
        content_lines = []
        is_content = False
        for line in lines:
            if not is_content:
                if line.startswith("sequence:"):
                    seq = int(line.split("sequence:", 1)[1].strip())
                elif line.startswith("sent_at:"):
                    sent_at = line.split("sent_at:", 1)[1].strip()
                elif line.startswith("sender:"):
                    sender = line.split("sender:", 1)[1].strip()
                elif line.strip() == "content:":
                    is_content = True
            else:
                content_lines.append(line)
        if seq is not None:
            messages.append({
                "sequence": seq,
                "sent_at": sent_at,
                "sender": sender,
                "content": "\n".join(content_lines),
            })
    return messages


def format_message(seq, sent_at, sender, content):
    return f"sequence: {seq}\nsent_at: {sent_at}\nsender: {sender}\ncontent:\n{content.strip()}\n---"


def get_max_sequence(messages):
    if not messages:
        return 0
    return max(m["sequence"] for m in messages)


def read_conversation(target_file):
    conv_file, _ = get_paths(target_file)
    if not os.path.exists(conv_file):
        return ""
    with open(conv_file, "r", encoding="utf-8") as f:
        return f.read()


def send_message(sender, content, target_file):
    conv_file, lock_file = get_paths(target_file)
    lock_fd = acquire_lock(lock_file)
    try:
        current_text = ""
        if os.path.exists(conv_file):
            with open(conv_file, "r", encoding="utf-8") as f:
                current_text = f.read()

        messages = parse_messages(current_text)
        new_seq = get_max_sequence(messages) + 1
        sent_at = datetime.now(timezone.utc).isoformat()

        new_msg_str = format_message(new_seq, sent_at, sender, content)

        if current_text.strip():
            updated_text = new_msg_str + "\n\n" + current_text.strip() + "\n"
        else:
            updated_text = new_msg_str + "\n"

        temp_file = conv_file + f".tmp.{os.getpid()}_{time.time_ns()}"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(updated_text)
            f.flush()
            os.fsync(f.fileno())

        os.replace(temp_file, conv_file)
        return new_seq, sent_at
    finally:
        release_lock(lock_fd)


def init_conversation(target_file):
    conv_file, lock_file = get_paths(target_file)
    lock_fd = acquire_lock(lock_file)
    try:
        with open(conv_file, "w", encoding="utf-8") as f:
            f.write("")
    finally:
        release_lock(lock_fd)
    return conv_file


def main():
    parser = argparse.ArgumentParser(
        description="Generic locked shared-log helper for the contribute-agents skill."
    )
    parser.add_argument("--file", required=True, help="Path to the shared conversation/log file")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("read", help="Print the entire current log")

    send_parser = subparsers.add_parser("send", help="Atomically commit a new message")
    send_parser.add_argument("--sender", required=True, help="Persona/agent identifier")
    send_parser.add_argument("--content", required=True, help="Message text")

    subparsers.add_parser("init", help="Create or clear the log file")

    args = parser.parse_args()

    if args.command == "read":
        print(read_conversation(args.file))
    elif args.command == "send":
        seq, sent_at = send_message(args.sender, args.content, args.file)
        print(f"Message committed: sequence={seq}, sent_at={sent_at}")
    elif args.command == "init":
        path = init_conversation(args.file)
        print(f"Log initialized: {path}")


if __name__ == "__main__":
    main()
