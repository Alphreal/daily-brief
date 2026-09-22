#!/usr/bin/env python3
"""check_lengths.py — file-length clean-code gate. Stdlib only.
Usage: python check_lengths.py [paths...]  (default: repo root)
Exit: 0 clean, 1 FAIL (>500), 2 cannot run. WARN (>300) never fails.
"""

import os
import sys

WARN = 300
BLOCK = 500
EXTS = (".py", ".html", ".js", ".css")
SKIP_DIRS = {".git", "__pycache__", ".opencode", "node_modules", "vendor"}
SKIP_PATH = ("docs/assets/vendor",)

BASE = os.path.dirname(os.path.abspath(__file__))


def iter_files(paths):
    for p in paths:
        if os.path.isfile(p):
            if p.endswith(EXTS):
                yield p
            continue
        for root, dirs, files in os.walk(p):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for f in files:
                fp = os.path.join(root, f)
                if any(s in fp.replace("\\", "/") for s in SKIP_PATH):
                    continue
                if f.endswith(EXTS):
                    yield fp


def count_lines(fp):
    with open(fp, encoding="utf-8", errors="replace") as fh:
        return sum(1 for _ in fh)


def main(paths):
    roots = paths or [BASE]
    warns, blocks = [], []
    checked = 0
    for fp in iter_files(roots):
        try:
            n = count_lines(fp)
        except OSError as e:
            print(f"SKIP {fp}: {e}")
            continue
        checked += 1
        rel = os.path.relpath(fp, BASE)
        if n > BLOCK:
            blocks.append((n, rel))
        elif n > WARN:
            warns.append((n, rel))
    for n, rel in sorted(warns, reverse=True):
        print(f"WARN {n:5d}  {rel}  (>300, split soon)")
    for n, rel in sorted(blocks, reverse=True):
        print(f"FAIL {n:5d}  {rel}  (>500, must split)")
    print(f"checked {checked} files, {len(warns)} warn, {len(blocks)} fail")
    return 1 if blocks else 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Exception as e:  # gate must never read as clean on crash
        print(f"check_lengths: cannot run: {e}")
        sys.exit(2)
