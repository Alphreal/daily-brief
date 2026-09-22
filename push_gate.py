#!/usr/bin/env python3
"""push_gate.py — enforced pre-push gate for docs/ publish. Stdlib only.
Checks: allowlist (architecture) + secrets + lengths + lightweight 5-axis.
Usage: from push_gate import push_gate; ok, msg = push_gate(files, base_dir)
"""

import os


def push_gate(docs_files, base_dir):
    """Returns (ok, msg). Never raises."""
    try:
        allowed_ext = (".html", ".css", ".js", ".svg")
        banned = ("credentials.json", "token.json", ".env")
        for f in docs_files:
            bn = os.path.basename(f).lower()
            if bn in banned or not f.startswith("docs/") or not f.lower().endswith(allowed_ext):
                return False, f"gate FAIL architecture/secrets: not shippable: {f}"
            fp = os.path.join(base_dir, f)
            if not os.path.isfile(fp) or os.path.getsize(fp) == 0:
                return False, f"gate FAIL correctness: missing/empty: {f}"
            if os.path.getsize(fp) > 1024 * 1024:
                return False, f"gate FAIL performance: >1MB: {f}"
            n = 0
            with open(fp, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    n += 1
                    ll = line.lower()
                    if "gho_" in ll or "github_pat_" in ll or "credentials.json" in ll:
                        return False, f"gate FAIL security: secret string in {f}"
                    if n > 600:
                        break
            if n > 500:
                return False, f"gate FAIL readability: {f} {n} lines >500, split first"
            if f.lower().endswith(".html"):
                with open(fp, encoding="utf-8", errors="replace") as fh:
                    if "<html" not in fh.read(4000).lower():
                        return False, f"gate FAIL correctness: {f} no <html>"
        return True, "gate PASS"
    except Exception as e:
        return False, f"gate FAIL cannot run: {e}"


if __name__ == "__main__":
    import sys

    base = os.path.dirname(os.path.abspath(__file__))
    print(push_gate(sys.argv[1:] or ["docs/index.html"], base))
