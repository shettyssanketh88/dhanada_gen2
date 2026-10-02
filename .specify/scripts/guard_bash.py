#!/usr/bin/env python3
"""PreToolUse hook (DH2-DEV-002): deny Bash commands that touch secrets, broker endpoints, the VPS or Principal-owned rails.

Secret locations are denied outright. Everything else guarded may be mentioned only in a line
whose every command is read-only, with no output redirection or command substitution.
"""

from __future__ import annotations

import json
import re
import sys

SECRETS = [r"\.env\b(?!\.example\b)", r"/etc/dhanada", r"\bsecrets/"]
GUARDED = [
    r"kite\.trade",
    r"kite\.zerodha",
    r"\bssh\b",
    r"\bscp\b",
    r"\bdocker\b",
    r"\bpsql\b",
    r"rails/ips\.yaml",
    r"rails/RAILS\.md",
    r"rails/broker-confirmation\.md",
    r"constitution\.md",
]
READ_ONLY = re.compile(r"^\s*(cat|sed -n|grep|head|tail|ls|git (diff|log|show|status))\b")
SEPARATORS = re.compile(r"\|\||&&|[|;&\n]")
UNSAFE = re.compile(r"[<>`]|\$\(")


def hits(patterns: list[str], cmd: str) -> list[str]:
    return [p for p in patterns if re.search(p, cmd)]


def is_single_read(cmd: str) -> bool:
    if UNSAFE.search(cmd):
        return False
    return all(READ_ONLY.match(part) for part in SEPARATORS.split(cmd) if part.strip())


def main() -> int:
    data = json.load(sys.stdin)
    cmd = (data.get("tool_input") or {}).get("command", "")
    secret, guarded = hits(SECRETS, cmd), hits(GUARDED, cmd)
    if secret or (guarded and not is_single_read(cmd)):
        print(
            f"blocked by guard_bash (DH2-DEV-002): matches {secret + guarded}. "
            "Principal-owned or production resource; raise it instead.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
