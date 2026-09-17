#!/usr/bin/env python3
"""Build guidebook DOC*.md into styled HTML (same shell as brief.py). Stdlib only.

Usage: python guidebook/build.py
Output: guidebook/*.html + OUT_DIR/guidebook/*.html + docs/guidebook/*.html.
Publish with: git add guidebook docs/guidebook && git commit -m ... && git push
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
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<i>\1</i>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    return s


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def md_to_html(text):
    out, toc, lines, i = [], [], text.split("\n"), 0
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip():
            i += 1
            continue
        if ln.startswith("### "):
            out.append(f"<h3>{inline(ln[4:])}</h3>")
        elif ln.startswith("## "):
            sid = slug(ln[3:]) or f"sec-{len(toc)}"
            toc.append((sid, ln[3:].strip()))
            out.append(f'<h2 id="{sid}">{inline(ln[3:])}</h2>')
        elif ln.startswith("# "):
            out.append(f"<h1>{inline(ln[2:])}</h1>")
        elif ln.strip() == "---":
            out.append("<hr>")
        elif ln.startswith("> "):
            quotes = []
            while i < len(lines) and lines[i].strip().startswith("> "):
                quotes.append(inline(lines[i].strip()[2:]))
                i += 1
            out.append('<div class="tldr">' + "<br>".join(quotes) + "</div>")
            continue
        elif ln.startswith("|"):
            tbl, hdr = ["<div class='card'><table>"], True
            while i < len(lines) and lines[i].strip().startswith("|"):
                raw = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if all(c and set(c) <= set("-: ") for c in raw):
                    i += 1
                    continue
                cells = [inline(c) for c in raw]
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
            txt = ln.strip()
            if txt.startswith(("[Graph", "[Picture", "[QR")):
                out.append(f'<div class="placeholder">{inline(txt)}</div>')
            else:
                out.append(f"<p>{inline(txt)}</p>")
        i += 1
    if toc:
        nav = '<div class="toc">' + "".join(
            f'<a href="#{brief.esc(sid)}">{brief.esc(t)}</a>' for sid, t in toc
        ) + "</div>"
        return nav + "\n" + "\n".join(out), toc
    return "\n".join(out), toc


SHELL_TOPBAR = '<div class="topbar"><a href="index.html">&larr; Alph</a><span class="muted">Daily Brief</span></div>'


def swap_topbar(page, nav):
    assert page.count(SHELL_TOPBAR) == 1, "brief.html_shell topbar changed - update SHELL_TOPBAR"
    return page.replace(SHELL_TOPBAR, nav)


def main():
    out_local = os.path.join(brief.OUT_DIR, "guidebook")
    os.makedirs(PAGES_DIR, exist_ok=True)
    os.makedirs(out_local, exist_ok=True)
    built = []
    for fn, label in DOCS:
        with open(os.path.join(GB_DIR, fn), encoding="utf-8") as f:
            body, _toc = md_to_html(f.read())
        nav = '<div class="topbar"><a href="index.html">&larr; Alph</a><span class="muted">Guidebook</span></div>'
        html = swap_topbar(brief.html_shell(label, body), nav)
        name = fn.replace(".md", ".html")
        out = os.path.join(GB_DIR, name)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        shutil.copy(out, os.path.join(PAGES_DIR, name))
        shutil.copy(out, os.path.join(out_local, name))
        built.append(name)
        print(f"Built: {out}")
    idx_body = "<h1>Guidebook</h1>" + "".join(
        f'<div class="card"><a href="{fn.replace(".md", ".html")}"><b>{brief.esc(label)}</b></a></div>'
        for fn, label in DOCS
    )
    idx = swap_topbar(
        brief.html_shell("Guidebook", idx_body),
        '<div class="topbar"><a href="../index.html">&larr; Alph</a><span class="muted">Guidebook</span></div>',
    )
    with open(os.path.join(GB_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(idx)
    shutil.copy(os.path.join(GB_DIR, "index.html"), os.path.join(PAGES_DIR, "index.html"))
    shutil.copy(os.path.join(GB_DIR, "index.html"), os.path.join(out_local, "index.html"))
    print(f"Built index + published to docs/guidebook/: {built + ['index.html']}")


if __name__ == "__main__":
    main()
