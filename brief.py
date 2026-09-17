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
import html
import json
import os
import re
import shutil
import subprocess
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

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
        rows = re.findall(r"\|\s*\d+\s*\|\s*\[([A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+)\][^\|]*\|\s*(.*?)\s*\|\s*\+([\d,]+)\s*\|\s*([\d,]+)", md)
        if not rows:  # fallback: old plain format without markdown link
            rows = re.findall(r"\|\s*\d+\s*\|\s*([A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+)\s*\|\s*(.*?)\s*\|\s*\+([\d,]+)\s*\|\s*([\d,]+)", md)
        for repo, desc, gained, total in rows[:10]:
            lines_out.append({
                "repo": repo.strip(),
                "gained": "+" + gained.strip(),
                "total": total.strip(),
                "desc": desc.strip()[:160],
                "url": f"https://github.com/{repo.strip()}",
                "source": "ai-repo-tracker"
            })
    except Exception as e:
        lines_out.append({"repo": "fetch-error/ai-tracker", "gained": "-", "total": "-", "desc": f"tracker fetch failed: {e}", "url": "https://github.com/popcafa/ai-repo-tracker", "source": "error"})

    # 2) New hot repos last 14 days via GitHub Search API (no auth, 10 req/min)
    new_hot = []
    try:
        since = (datetime.date.today() - datetime.timedelta(days=14)).isoformat()
        q2 = urllib.parse.quote(f"created:>{since} stars:>200", safe="")
        url = f"https://api.github.com/search/repositories?q={q2}&sort=stars&order=desc&per_page=10"
        data = fetch_json(url)
        for it in data.get("items", [])[:10]:
            new_hot.append({
                "repo": it.get("full_name"),
                "stars": it.get("stargazers_count"),
                "desc": (it.get("description") or "")[:160],
                "url": it.get("html_url"),
            })
    except Exception as e:
        new_hot = [{"repo": "rate-limit-or-offline", "stars": "-", "desc": str(e)[:150], "url": "https://github.com/trending?since=weekly"}]
    return lines_out, new_hot

def clean_html(s, limit=220):
    s = html.unescape(s or "")
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    # drop common feed junk
    s = re.sub(r"^(The post|This article).{0,80}(appeared first on.*?)\.?\s*", "", s)
    if s.lower() in ("comments", "comment", ""):
        return ""
    return s[:limit] + ("..." if len(s) > limit else "")

def takeaway_for(title, summary):
    t = (title + " " + summary).lower()
    if any(k in t for k in ["agent", "claude", "chatgpt", "llm", "ai ", "ai-", "model"]):
        return "Why it matters: agents are moving into real workflows - test on a copy first, don't hand over payments/keys."
    if any(k in t for k in ["nasa", "space", "mars", "moon", "telescope", "orbit", "asteroid", "comet"]):
        return "Why it matters: space ops feed timelines - pretty pictures aside, watch launch/mission dates."
    if any(k in t for k in ["cancer", "drug", "health", "clinical", "vaccine", "brain"]):
        return "Why it matters: health headlines need human trials - mice/cells only means years away, don't act medically on it."
    if any(k in t for k in ["chip", "gpu", "semiconductor", "battery", "quantum", "laser"]):
        return "Why it matters: hardware sets what software can do next - note efficiency/cost claims, not just speed."
    if any(k in t for k in ["climate", "ice", "ocean", "carbon", "fossil", "permafrost"]):
        return "Why it matters: single records aren't trends - look for multi-year data before conclusions."
    return "Why it matters: new tool/idea - try the smallest demo before adopting."

def verdict_for_repo(repo, desc):
    d = (repo + " " + desc).lower()
    if any(k in d for k in ["skill", "browser", "diagram", "science", "template", "prompt"]):
        return "Worth a look - small, reusable, low adoption risk."
    if any(k in d for k in ["harness", "framework", "platform", "gateway"]):
        return "Try carefully - useful but breaks when model APIs change; pin versions."
    if any(k in d for k in ["trading", "finance", "income", "seo"]):
        return "Hype check - interesting code, don't trust money claims; backtest yourself."
    return "Skim first - star spike may be demo-driven; check last commit + issues."

DAILY_BOTTOM = "Bottom line: headlines are hints, not conclusions. For AI: use agents for research, keep payments/keys manual. For science: mice/single papers need replication. For space: dates matter more than photos."
MONDAY_BOTTOM = "Bottom line: weekly gain = interest, not audit. Before install: license, last commit date, open issues, tests. Star spikes on demos fade; painkillers (browser sharing, diagrams, science skills) stick."

def tldr_picks(feeds):
    """First item of each feed = top pick (skip failed feeds). Shared by md + html."""
    return [(n, items[0]) for n, items in feeds.items()
            if items and not items[0][0].startswith("RSS failed")][:3]

def fetch_rss_titles(url, limit=5):
    try:
        xml_text = fetch_text(url)
        root = ET.fromstring(xml_text)
        items = []
        for item in root.iter("item"):
            t = (item.findtext("title") or "").strip()
            l = (item.findtext("link") or "").strip()
            desc_raw = (item.findtext("description") or "")
            pub = (item.findtext("pubDate") or "").strip()
            if t:
                items.append((t, l, clean_html(desc_raw), pub[:16]))
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

def render_monday_md(date_str, weekly, new_hot):
    L = []
    L.append(f"# Monday GitHub Trending - weekly gain (not all-time) - {date_str}")
    L.append("")
    L.append("Top 10 by stars GAINED last week. Read the verdict, not just the stars.")
    L.append("Verify live: https://github.com/trending?since=weekly")
    L.append("")
    L.append("## TL;DR - my take")
    if weekly:
        for i, r in enumerate(weekly[:3], 1):
            L.append(f"- #{i} {r['repo']} ({r['gained']}) - {verdict_for_repo(r['repo'], r['desc'])}")
    else:
        L.append("- Weekly tracker empty today - using new-hot below as fallback.")
        for h in new_hot[:3]:
            L.append(f"- {h['repo']} ({h.get('stars')} stars) - {verdict_for_repo(h['repo'], h['desc'])}")
    L.append("")
    for i, r in enumerate(weekly, 1):
        L.append(f"## {i}. {r['repo']} ({r['gained']} this week, {r['total']} total)")
        L.append(f"- What it is: {r['desc']}")
        L.append(f"- Verdict: {verdict_for_repo(r['repo'], r['desc'])}")
        L.append(f"- {r['url']}")
        L.append("")
    L.append("---")
    L.append("### New hot (created last 14 days) - early bets, higher risk")
    for h in new_hot:
        L.append(f"- {h['repo']} ({h.get('stars')} stars) - {h['desc']}")
        L.append(f"  Verdict: {verdict_for_repo(h['repo'], h['desc'])} - {h['url']}")
    L.append("")
    L.append(MONDAY_BOTTOM)
    return "\n".join(L)

def render_daily_md(date_str, feeds):
    L = []
    L.append(f"# Coffee brief - AI / Tech / Science - {date_str} (10 min)")
    L.append("")
    # TL;DR: first item of each feed = top pick
    L.append("## TL;DR - 3 to read first")
    picks = tldr_picks(feeds)
    if not picks:
        L.append("- All feeds failed today - see sections below, or rerun later.")
    for name, (t, l, s, p) in picks:
        L.append(f"- [{name}] {t}")
        if s:
            L.append(f"  In short: {s}")
        L.append(f"  {l}")
    L.append("")
    for name, items in feeds.items():
        L.append(f"## {name}")
        for t, l, s, p in items:
            L.append(f"- {t}" + (f" ({p})" if p else ""))
            if s:
                L.append(f"  Summary: {s}")
                L.append(f"  {takeaway_for(t, s)}")
            else:
                L.append(f"  Note: discussion thread, no article summary - skim comments for lived experience.")
                L.append(f"  {takeaway_for(t, '')}")
            L.append(f"  Link: {l}")
        L.append("")
    L.append(DAILY_BOTTOM)
    return "\n".join(L)

def esc(s):
    return html.escape(s or "", quote=True)

def html_shell(title, body_inner):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
body{{background:#f7f7f5;color:#1a1a1a;font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0}}
.wrap{{max-width:880px;margin:0 auto;padding:24px 16px 64px}}
.topbar{{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}}
.topbar a{{color:#555;text-decoration:none;font-size:14px}}
.card{{background:#fff;border:1px solid #e7e5e4;border-radius:12px;padding:16px;margin:12px 0}}
.tldr{{background:#fff;border:1px solid #e7e5e4;border-left:4px solid #1a1a1a;border-radius:12px;padding:16px;margin:16px 0}}
.badge{{display:inline-block;background:#f1f0ee;border-radius:999px;padding:2px 10px;font-size:12px;margin-right:6px}}
.muted{{color:#6b7280;font-size:13px}}
.grid2{{display:grid;grid-template-columns:1fr;gap:0}}
@media(min-width:720px){{.grid2{{grid-template-columns:1fr 1fr;gap:12px}}.grid2 .card{{margin:0}}}}
.sec{{margin-top:28px}}
a{{color:#0f62fe}}
h1{{font-size:26px;margin:8px 0}}h2{{font-size:19px;margin:0 0 8px}}h3{{font-size:16px;margin:14px 0 6px}}
table{{width:100%;border-collapse:collapse;font-size:14px}}
th,td{{text-align:left;padding:8px 10px;border-bottom:1px solid #e7e5e4;vertical-align:top}}
th{{background:#f7f7f5;font-weight:600}}
.placeholder{{border:1.5px dashed #a8a29e;border-radius:12px;padding:14px 16px;margin:12px 0;background:#fafaf9;color:#57534e;font-size:14px}}
.toc{{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 4px;position:sticky;top:0;z-index:5;background:#f7f7f5;padding:8px 0}}
.hero{{text-align:center}}
.hero h1{{font-size:30px}}
.chapter{{background:#fff;border:1px solid #e7e5e4;border-radius:14px;padding:4px 20px 16px;margin:20px 0}}
.chapter h2{{margin-top:14px}}
.toc a{{background:#fff;border:1px solid #e7e5e4;border-radius:999px;padding:4px 12px;font-size:13px;color:#1a1a1a;text-decoration:none}}
@media(min-width:1100px){{.wrap{{max-width:1100px}}.grid2{{grid-template-columns:1fr 1fr 1fr}}}}
@media print{{.topbar{{display:none}}.wrap{{max-width:100%;padding:0}}body{{background:#fff}}.card,.tldr{{break-inside:avoid}}}}
</style>
</head>
<body>
<div class="wrap mx-auto px-4">
<div class="topbar"><a href="index.html">&larr; Alph</a><span class="muted">Daily Brief</span></div>
{body_inner}
</div>
</body>
</html>"""

def render_daily_html(date_str, feeds):
    tldr = ['<div class="tldr"><h2>TL;DR &mdash; 3 to read first</h2>']
    picks = tldr_picks(feeds)
    if not picks:
        tldr.append('<div class="card muted">All feeds failed today &mdash; see sections below, or rerun later.</div>')
    for name, (t, l, s, p) in picks:
        tldr.append(f'<div class="card"><span class="badge">{esc(name)}</span>'
                    f'<a href="{esc(l)}"><b>{esc(t)}</b></a>'
                    + (f'<div class="muted">{esc(s)}</div>' if s else '') + '</div>')
    tldr.append('</div>')
    secs = [f"<h1>Coffee brief &mdash; AI / Tech / Science &mdash; {esc(date_str)} (10 min)</h1>",
            "<div class='muted'>Same content as .md + Gmail draft.</div>"] + tldr
    for name, items in feeds.items():
        secs.append(f'<div class="sec"><h2>{esc(name)}</h2><div class="grid2">')
        for t, l, s, p in items:
            if s:
                inner = f'<div class="muted">{esc(s)}</div><div class="muted">{esc(takeaway_for(t, s))}</div>'
            else:
                inner = f'<div class="muted">Discussion thread, no summary &mdash; skim comments.</div><div class="muted">{esc(takeaway_for(t, ""))}</div>'
            secs.append(f'<div class="card"><a href="{esc(l)}"><b>{esc(t)}</b></a>'
                        + (f' <span class="muted">({esc(p)})</span>' if p else '')
                        + f'<br>{inner}<br><a href="{esc(l)}">{esc(l)}</a></div>')
        secs.append('</div></div>')
    secs.append(f'<div class="card muted">{esc(DAILY_BOTTOM)}</div>')
    return html_shell(f"Coffee brief - {date_str}", "\n".join(secs))

def render_monday_html(date_str, weekly, new_hot):
    tldr = ['<div class="tldr"><h2>TL;DR &mdash; my take</h2>']
    if weekly:
        for i, r in enumerate(weekly[:3], 1):
            tldr.append(f'<div class="card"><span class="badge">#{i} {esc(r["repo"])}</span> '
                        f'<span class="badge">{esc(r["gained"])}</span>'
                        f'<div class="muted">{esc(verdict_for_repo(r["repo"], r["desc"]))}</div></div>')
    else:
        for h in new_hot[:3]:
            tldr.append(f'<div class="card"><b>{esc(h["repo"])}</b><div class="muted">{esc(verdict_for_repo(h["repo"], h["desc"]))}</div></div>')
    tldr.append('</div>')
    secs = [f"<h1>Monday GitHub Trending &mdash; weekly gain &mdash; {esc(date_str)}</h1>",
            "<div class='muted'>Top 10 by stars GAINED last week. Read the verdict, not just the stars. "
            "<a href='https://github.com/trending?since=weekly'>Verify live</a></div>"] + tldr
    secs.append('<div class="sec"><h2>Top 10 weekly gain</h2><div class="grid2">')
    for i, r in enumerate(weekly, 1):
        secs.append(f'<div class="card"><span class="badge">#{i}</span>'
                    f'<a href="{esc(r["url"])}"><b>{esc(r["repo"])}</b></a> '
                    f'<span class="badge">{esc(r["gained"])} / {esc(r["total"])} total</span>'
                    f'<div class="muted">{esc(r["desc"])}</div>'
                    f'<div class="muted">Verdict: {esc(verdict_for_repo(r["repo"], r["desc"]))}</div></div>')
    secs.append('</div></div>')
    secs.append('<div class="sec"><h2>New hot (created last 14 days)</h2>')
    for h in new_hot:
        secs.append(f'<div class="card"><a href="{esc(h["url"])}"><b>{esc(h["repo"])}</b></a> '
                    f'<span class="badge">{esc(str(h.get("stars")))} stars</span>'
                    f'<div class="muted">{esc(h["desc"])}</div>'
                    f'<div class="muted">Verdict: {esc(verdict_for_repo(h["repo"], h["desc"]))}</div></div>')
    secs.append('</div>')
    secs.append(f'<div class="card muted">{esc(MONDAY_BOTTOM)}</div>')
    return html_shell(f"Monday Trending - {date_str}", "\n".join(secs))

def render_index_html(entries, base_dir=None):
    # entries: list of (filename, label, date_str) sorted desc
    rows = ['<h1>NEWS</h1>',
            '<div class="tldr"><b>Latest</b> &mdash; start here, then browse below.</div>']
    for fn, label, ds in entries:
        rows.append(f'<div class="card"><a href="{esc(fn)}"><b>{esc(label)}</b></a> '
                    f'<span class="badge">{esc(ds)}</span></div>')
    if not entries:
        rows.append('<div class="card muted">No issues yet &mdash; run: python brief.py --mode daily</div>')
    if base_dir and os.path.exists(os.path.join(base_dir, "guidebook", "index.html")):
        rows.append('<div class="card"><a href="guidebook/index.html"><b>Guidebook</b></a> '
                    '<span class="badge">study guide</span></div>')
    return html_shell("Daily Brief - index", "\n".join(rows))

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

def auto_push_docs(date_str, mode, docs_files):
    """Best-effort git add/commit/push of the given docs/*.html files so Pages auto-updates.
    Only the listed files are staged (never token/credentials).
    Never raises: scheduler runs must not fail because push failed."""
    try:
        env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
        def run(*a):
            return subprocess.run(a, cwd=BASE_DIR, env=env, capture_output=True,
                                  text=True, timeout=90)
        r = run("git", "rev-parse", "--is-inside-work-tree")
        if r.returncode != 0:
            return False, "not a git repo, push skipped."
        r = run("git", "add", "--", *docs_files)
        if r.returncode != 0:
            return False, f"git add failed: {(r.stderr or r.stdout).strip()[:150]}"
        st = run("git", "status", "--porcelain", "--", *docs_files)
        if not st.stdout.strip():
            return True, "docs/ unchanged, nothing to push."
        c = run("git", "commit", "-m", f"brief {date_str} ({mode}) auto-publish")
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
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        import base64
        from email.message import EmailMessage
    except ImportError:
        return False, "google libs not installed (pip install google-api-python-client google-auth-oauthlib). Saved .md only."
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
                return False, "credentials.json missing. Create OAuth Desktop client in Google Cloud, download as credentials.json next to brief.py, run once manually to login."
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
            f.write(render_index_html(entries, OUT_DIR))
        print(f"Saved: {ipath}")
        # docs/ export for GitHub Pages (html only, never token/credentials):
        # copy every brief-*.html so docs/index never links to a missing file,
        # then rebuild docs/index.html from what is actually in docs/.
        seen = [os.path.join(OUT_DIR, fn) for fn, _, _ in entries] + [ipath]
        export_docs(seen)
        docs_entries = list_html_entries(DOCS_DIR)
        with open(os.path.join(DOCS_DIR, "index.html"), "w", encoding="utf-8") as f:
            f.write(render_index_html(docs_entries, DOCS_DIR))
        print(f"Exported to docs/: {sorted(os.path.basename(p) for p in seen)}")
        if not args.no_push:
            docs_rel = [os.path.join("docs", os.path.basename(p)) for p in seen]
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
