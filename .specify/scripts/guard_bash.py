#!/usr/bin/env python3
"""PreToolUse hook (DH2-DEV-002): deny Bash commands that touch secrets, broker endpoints, the VPS or Principal-owned rails."""
import json, re, sys
data = json.load(sys.stdin)
cmd = (data.get("tool_input") or {}).get("command", "")
patterns = [r"\.env\b", r"/etc/dhanada", r"kite\.trade", r"kite\.zerodha", r"\bssh\b", r"\bscp\b", r"\bdocker\b", r"\bpsql\b",
            r"rails/ips\.yaml", r"rails/RAILS\.md", r"rails/broker-confirmation\.md", r"constitution\.md"]
hit = [p for p in patterns if re.search(p, cmd)]
if hit and not re.match(r"^\s*(cat|sed -n|grep|head|tail|ls|git (diff|log|show|status))\b", cmd):
    print(f"blocked by guard_bash (DH2-DEV-002): matches {hit}. Principal-owned or production resource; raise it instead.", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
