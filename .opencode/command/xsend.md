---
description: Send a message to another OpenCode session via the cross-session bus.
---

Send via the bus. $ARGUMENTS should be: `<to-session> <message>`

Steps:
1. Ensure you know your own session name. If unsure, run `python .opencode/cross-session/bus.py sessions --list`.
2. Run: `python .opencode/cross-session/bus.py send --from <my-session> --to <to-session> --msg "<message>" --type text`
3. Confirm with the returned `sent <id>` line.

Example: `/xsend right Hello from left, Part A is done`
