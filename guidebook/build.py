#!/usr/bin/env python3
"""Build guidebook DOC*.md into styled HTML (same shell as brief.py). Stdlib only.

Usage: python guidebook/build.py [--no-push]
Output: guidebook/*.html + docs/guidebook/*.html (for Pages).
"""
import os
import re
import shutil
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
import brief  # noqa: E402 — reuse esc() + html_shell()

GB_DIR = os.path.join(BASE_DIR, "guidebook")
PAGES_DIR = os.path.join(BASE_DIR, "docs", "guidebook")

DOCS = [
    ("DOC1-practical-short.md", "Practical Short — Student Guide"),
    ("DOC2-detailed-long.md", "Detailed Long — Evidence Report"),
    ("DOC3-mix-textbook.md", "Mix Textbook — Teacher Lessons"),
]


def inline(s):
    s = brief.esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    return s


def md_to_html(text):
    out, lines, i = [], text.split("\n"), 0
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip():
            i += 1
            continue
        if ln.startswith("### "):
            out.append(f"<h3>{inline(ln[4:])}</h3>")
        elif ln.startswith("## "):
            out.append(f"<h2>{inline(ln[3:])}</h2>")
        elif ln.startswith("# "):
            out.append(f"<h1>{inline(ln[2:])}</h1>")
        elif ln.strip() == "---":
            out.append("<hr>")
        elif ln.startswith("> "):
            out.append(f'<div class="tldr">{inline(ln[2:])}</div>')
        elif ln.startswith("|"):
            tbl, hdr = ["<div class='card'><table>"], True
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [inline(c.strip()) for c in lines[i].strip().strip("|").split("|")]
                if all(set(c) <= set("-: ") for c in cells):
                    i += 1
                    continue
                tag = "th" if hdr else "td"
                tbl.append("<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>")
                hdr, i = False, i + 1
            tbl.append("</table></div>")
            out.append("\n".join(tbl))
            continue
        elif ln.startswith("- "):
            items = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append(f"<li>{inline(lines[i].strip()[2:])}</li>")
                i += 1
            out.append("<ul class='card'>" + "\n".join(items) + "</ul>")
            continue
        elif re.match(r"\d+\. ", ln.strip()):
            items = []
            while i < len(lines) and re.match(r"\d+\. ", lines[i].strip()):
                txt = re.sub(r"^\d+\.\s*", "", lines[i].strip())
                items.append(f"<li>{inline(txt)}</li>")
                i += 1
            out.append("<ol class='card'>" + "\n".join(items) + "</ol>")
            continue
        else:
            out.append(f"<p>{inline(ln.strip())}</p>")
        i += 1
    return "\n".join(out)


def main():
    os.makedirs(PAGES_DIR, exist_ok=True)
    built = []
    for fn, label in DOCS:
        with open(os.path.join(GB_DIR, fn), encoding="utf-8") as f:
            body = md_to_html(f.read())
        nav = '<div class="topbar"><a href="index.html">&larr; Alph</a><span class="muted">Guidebook</span></div>'
        page = brief.html_shell(label, body)
        # html_shell has its own topbar; strip ours in favor of page-level one
        html = page.replace(
            '<div class="topbar"><a href="index.html">&larr; Alph</a><span class="muted">Daily Brief</span></div>',
            nav,
        )
        out = os.path.join(GB_DIR, fn.replace(".md", ".html"))
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        shutil.copy(out, os.path.join(PAGES_DIR, os.path.basename(out)))
        built.append(os.path.basename(out))
        print(f"Built: {out}")
    idx_body = "<h1>Guidebook</h1>" + "".join(
        f'<div class="card"><a href="{fn.replace(".md", ".html")}"><b>{label}</b></a></div>'
        for fn, label in DOCS
    )
    idx = brief.html_shell("Guidebook", idx_body).replace(
        '<div class="topbar"><a href="index.html">&larr; Alph</a><span class="muted">Daily Brief</span></div>',
        '<div class="topbar"><a href="../index.html">&larr; Alph</a><span class="muted">Guidebook</span></div>',
    )
    with open(os.path.join(GB_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(idx)
    shutil.copy(os.path.join(GB_DIR, "index.html"), os.path.join(PAGES_DIR, "index.html"))
    print(f"Built index + published to docs/guidebook/: {built + ['index.html']}")


if __name__ == "__main__":
    main()
