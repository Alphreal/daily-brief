#!/usr/bin/env python3
"""
Daily / Monday briefing generator for Windows Task Scheduler.
- Monday 9am VN: Top 10 GitHub TRENDING by weekly star gain (previous week trend, not all-time).
- Tue-Sun 9am VN: 10-min AI / tech / science coffee brief from RSS (no clickbait).

Stdlib only. No pip install required.
Optional Gmail draft: only if google-api-python-client + credentials.json exist, else saves .md file.

Usage:
  python brief.py --mode auto --email tung19628@gmail.com
  python brief.py --mode monday --email tung19628@gmail.com --no-draft
  python brief.py --mode daily --email tung19628@gmail.com
Output: OUT_DIR/brief-YYYY-MM-DD-(daily|monday).md + .html, index.html, docs/ copy for Pages
Flags: --no-draft (skip Gmail), --no-html (skip HTML), --no-push (skip docs/ auto-push)
"""

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from brief_render import (
    clean_html,
    render_daily_html,
    render_daily_md,
    render_index_html,
    render_monday_html,
    render_monday_md,
)
from push_gate import push_gate

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# NOTE: Default Project folder is not creatable via PowerShell here, so write output to Temp (writable).
OUT_DIR = r"C:\Users\ADMIN\AppData\Local\Temp\opencode\brief-out"
DOCS_DIR = os.path.join(BASE_DIR, "docs")
HEADERS = {"User-Agent": "brief-bot/1.0 (+local scheduler)"}


def fetch_text(url, timeout=20):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def fetch_json(url, timeout=20):
    return json.loads(fetch_text(url, timeout))


def monday_github_trending():
    """Return list of dicts: weekly trending, previous-week gain focus."""
    lines_out = []
    # 1) AI-agent weekly growers tracker (popcafa) - exact weekly gain table
    try:
        md = fetch_text("https://raw.githubusercontent.com/popcafa/ai-repo-tracker/main/README.md")
        # rows look like: | 1 | [owner/repo](https://github.com/owner/repo) | desc | +7,463 | 138,511 |
        rows = re.findall(
            r"\|\s*\d+\s*\|\s*\[([A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+)\][^\|]*\|\s*(.*?)\s*\|\s*\+([\d,]+)\s*\|\s*([\d,]+)",
            md,
        )
        if not rows:  # fallback: old plain format without markdown link
            rows = re.findall(
                r"\|\s*\d+\s*\|\s*([A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+)\s*\|\s*(.*?)\s*\|\s*\+([\d,]+)\s*\|\s*([\d,]+)",
                md,
            )
        for repo, desc, gained, total in rows[:10]:
            lines_out.append(
                {
                    "repo": repo.strip(),
                    "gained": "+" + gained.strip(),
                    "total": total.strip(),
                    "desc": desc.strip()[:160],
                    "url": f"https://github.com/{repo.strip()}",
                    "source": "ai-repo-tracker",
                }
            )
    except Exception as e:
        lines_out.append(
            {
                "repo": "fetch-error/ai-tracker",
                "gained": "-",
                "total": "-",
                "desc": f"tracker fetch failed: {e}",
                "url": "https://github.com/popcafa/ai-repo-tracker",
                "source": "error",
            }
        )

    # 2) New hot repos last 14 days via GitHub Search API (no auth, 10 req/min)
    new_hot = []
    try:
        since = (datetime.date.today() - datetime.timedelta(days=14)).isoformat()
        q2 = urllib.parse.quote(f"created:>{since} stars:>200", safe="")
        url = f"https://api.github.com/search/repositories?q={q2}&sort=stars&order=desc&per_page=10"
        data = fetch_json(url)
        for it in data.get("items", [])[:10]:
            new_hot.append(
                {
                    "repo": it.get("full_name"),
                    "stars": it.get("stargazers_count"),
                    "desc": (it.get("description") or "")[:160],
                    "url": it.get("html_url"),
                }
            )
    except Exception as e:
        new_hot = [
            {
                "repo": "rate-limit-or-offline",
                "stars": "-",
                "desc": str(e)[:150],
                "url": "https://github.com/trending?since=weekly",
            }
        ]
    return lines_out, new_hot


def fetch_rss_titles(url, limit=5):
    try:
        xml_text = fetch_text(url)
        root = ET.fromstring(xml_text)
        items = []
        for item in root.iter("item"):
            t = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            desc_raw = item.findtext("description") or ""
            pub = (item.findtext("pubDate") or "").strip()
            if t:
                items.append((t, link, clean_html(desc_raw), pub[:16]))
            if len(items) >= limit:
                break
        return items
    except Exception as e:
        return [(f"RSS failed: {url} ({e})", url, "", "")]


def daily_brief():
    feeds = {
        "HackerNews": "https://news.ycombinator.com/rss",
        "NASA Breaking": "https://www.nasa.gov/rss/dyn/breaking_news.rss",
        "SciTechDaily": "https://scitechdaily.com/feed/",
    }
    out = {}
    for name, url in feeds.items():
        out[name] = fetch_rss_titles(url, limit=6)
    return out


def list_html_entries(scan_dir):
    out = []
    try:
        for fn in sorted(os.listdir(scan_dir), reverse=True):
            if fn.startswith("brief-") and fn.endswith(".html") and fn != "index.html":
                # brief-YYYY-MM-DD-mode.html
                m = re.match(r"brief-(\d{4}-\d{2}-\d{2})-(daily|monday)\.html", fn)
                if m:
                    out.append((fn, f"Brief {m.group(1)} ({m.group(2)})", m.group(1)))
    except FileNotFoundError:
        pass
    return out


def export_docs(html_files):
    """Copy only *.html to docs/ for GitHub Pages. Never token/credentials."""
    os.makedirs(DOCS_DIR, exist_ok=True)
    for src in html_files:
        if src.endswith(".html"):
            shutil.copy(src, os.path.join(DOCS_DIR, os.path.basename(src)))


def sync_vendor_assets():
    """Copy docs/assets (vendored libs) to OUT_DIR so local preview matches Pages.
    Returns repo-relative paths of vendored css/js for git add/push."""
    src = os.path.join(DOCS_DIR, "assets")
    if os.path.isdir(src):
        shutil.copytree(src, os.path.join(OUT_DIR, "assets"), dirs_exist_ok=True)
    out = []
    for root, _, files in os.walk(src):
        for fn in files:
            if fn.endswith((".css", ".js", ".svg")):
                out.append(os.path.relpath(os.path.join(root, fn), BASE_DIR).replace(os.sep, "/"))
    return sorted(out)


def auto_push_docs(date_str, mode, docs_files):
    """Best-effort git add/commit/push of the given docs/*.html files so Pages auto-updates.
    Only the listed files are staged (never token/credentials).
    Never raises: scheduler runs must not fail because push failed."""
    ok, msg = push_gate(docs_files, BASE_DIR)
    print(msg)
    if not ok:
        return False, msg
    try:
        env = dict(os.environ, GIT_TERMINAL_PROMPT="0")

        def run(*a):
            return subprocess.run(
                a, cwd=BASE_DIR, env=env, capture_output=True, text=True, timeout=90
            )

        r = run("git", "rev-parse", "--is-inside-work-tree")
        if r.returncode != 0:
            return False, "not a git repo, push skipped."
        r = run("git", "add", "--", *docs_files)
        if r.returncode != 0:
            return False, f"git add failed: {(r.stderr or r.stdout).strip()[:150]}"
        st = run("git", "status", "--porcelain", "--", *docs_files)
        if not st.stdout.strip():
            return True, "docs/ unchanged, nothing to push."
        c = run("git", "commit", "-m", f"brief {date_str} ({mode}) auto-publish", "--", *docs_files)
        if c.returncode != 0:
            return False, f"commit failed: {(c.stderr or c.stdout).strip()[:200]}"
        p = run("git", "push")
        if p.returncode != 0 and "upstream" in ((p.stderr or "") + (p.stdout or "")).lower():
            p = run("git", "push", "-u", "origin", "HEAD")
        if p.returncode != 0:
            return False, f"push failed: {(p.stderr or p.stdout).strip()[:200]}"
        return True, "Pushed docs/ - Pages rebuilds in ~1 min."
    except Exception as e:
        return False, f"push skipped: {e}"


def try_gmail_draft(subject, body_text, to_email):
    """Best-effort Gmail draft. Requires google-api-python-client + credentials.json. Returns (ok, msg)."""
    try:
        import base64
        from email.message import EmailMessage

        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        return (
            False,
            "google libs not installed (pip install google-api-python-client google-auth-oauthlib). Saved .md only.",
        )
    SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]
    creds = None
    # token must live in writable Temp (Default Project is not writable via Python here)
    tok = os.path.join(OUT_DIR, "token.json")
    sec = os.path.join(BASE_DIR, "credentials.json")
    sec_alt = os.path.join(OUT_DIR, "credentials.json")
    if not os.path.exists(sec) and os.path.exists(sec_alt):
        sec = sec_alt
    os.makedirs(OUT_DIR, exist_ok=True)
    if os.path.exists(tok):
        creds = Credentials.from_authorized_user_file(tok, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(sec):
                return (
                    False,
                    "credentials.json missing. Create OAuth Desktop client in Google Cloud, download as credentials.json next to brief.py, run once manually to login.",
                )
            flow = InstalledAppFlow.from_client_secrets_file(sec, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(tok, "w") as f:
            f.write(creds.to_json())
    try:
        svc = build("gmail", "v1", credentials=creds)
        msg = EmailMessage()
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body_text)
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        d = svc.users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()
        return True, f"Draft created: {d.get('id')}"
    except Exception as e:
        return False, f"Gmail API error: {e}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["auto", "monday", "daily"], default="auto")
    ap.add_argument("--email", default="tung19628@gmail.com")
    ap.add_argument("--no-draft", action="store_true", help="skip Gmail, just save file")
    ap.add_argument("--no-html", action="store_true", help="skip HTML, md only")
    ap.add_argument("--no-push", action="store_true", help="skip auto-push of docs/ to GitHub")
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    today = datetime.date.today()
    mode = args.mode
    if mode == "auto":
        mode = "monday" if today.weekday() == 0 else "daily"

    if mode == "monday":
        # Monday brief is weekly: always date it to the most recent Monday,
        # even when generated on another day (e.g. Wed 09-16 -> Mon 09-14).
        date_str = (today - datetime.timedelta(days=today.weekday())).isoformat()
    else:
        date_str = today.isoformat()
    if mode == "monday":
        weekly, new_hot = monday_github_trending()
        md = render_monday_md(date_str, weekly, new_hot)
        html_doc = None if args.no_html else render_monday_html(date_str, weekly, new_hot)
        subject = f"[Monday 9am VN] GitHub Trending Top 10 weekly gain - {date_str}"
    else:
        feeds = daily_brief()
        md = render_daily_md(date_str, feeds)
        html_doc = None if args.no_html else render_daily_html(date_str, feeds)
        subject = f"[9am VN] AI/Tech/Science coffee brief - {date_str}"

    path = os.path.join(OUT_DIR, f"brief-{date_str}-{mode}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Saved: {path}")

    if html_doc:
        hpath = os.path.join(OUT_DIR, f"brief-{date_str}-{mode}.html")
        with open(hpath, "w", encoding="utf-8") as f:
            f.write(html_doc)
        print(f"Saved: {hpath}")
        # rebuild index in OUT_DIR (entries already includes hpath)
        entries = list_html_entries(OUT_DIR)
        ipath = os.path.join(OUT_DIR, "index.html")
        with open(ipath, "w", encoding="utf-8") as f:
            f.write(render_index_html(entries))
        print(f"Saved: {ipath}")
        # docs/ export for GitHub Pages (html only, never token/credentials):
        # copy every brief-*.html so docs/index never links to a missing file,
        # then rebuild docs/index.html from what is actually in docs/.
        seen = [os.path.join(OUT_DIR, fn) for fn, _, _ in entries] + [ipath]
        export_docs(seen)
        vendor_rel = sync_vendor_assets()
        docs_entries = list_html_entries(DOCS_DIR)
        with open(os.path.join(DOCS_DIR, "index.html"), "w", encoding="utf-8") as f:
            f.write(render_index_html(docs_entries))
        print(f"Exported to docs/: {sorted(os.path.basename(p) for p in seen)}")
        if not args.no_push:
            docs_rel = [os.path.join("docs", os.path.basename(p)) for p in seen] + vendor_rel
            _, msg = auto_push_docs(date_str, mode, docs_rel)
            print(msg)
        else:
            print("Push skipped (--no-push).")
    else:
        print("HTML skipped (--no-html).")

    if not args.no_draft:
        ok, msg = try_gmail_draft(subject, md, args.email)
        print(msg)
    else:
        print("Draft skipped (--no-draft).")


if __name__ == "__main__":
    main()
