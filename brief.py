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
Output: ./out/brief-YYYY-MM-DD.md
"""
import argparse
import datetime
import html
import json
import os
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# NOTE: Default Project folder is not creatable via PowerShell here, so write output to Temp (writable).
OUT_DIR = r"C:\Users\ADMIN\AppData\Local\Temp\opencode\brief-out"
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
    L.append("Bottom line: weekly gain = interest, not audit. Before install: license, last commit date, open issues, tests. Star spikes on demos fade; painkillers (browser sharing, diagrams, science skills) stick.")
    return "\n".join(L)

def render_daily_md(date_str, feeds):
    L = []
    L.append(f"# Coffee brief - AI / Tech / Science - {date_str} (10 min)")
    L.append("")
    # TL;DR: first item of each feed = top pick
    L.append("## TL;DR - 3 to read first")
    picks = []
    for name, items in feeds.items():
        if items and not items[0][0].startswith("RSS failed"):
            picks.append((name, items[0]))
    for name, (t, l, s, p) in picks[:3]:
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
    L.append("Bottom line: headlines are hints, not conclusions. For AI: use agents for research, keep payments/keys manual. For science: mice/single papers need replication. For space: dates matter more than photos.")
    return "\n".join(L)

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
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    today = datetime.date.today()
    mode = args.mode
    if mode == "auto":
        mode = "monday" if today.weekday() == 0 else "daily"

    date_str = today.isoformat()
    if mode == "monday":
        weekly, new_hot = monday_github_trending()
        md = render_monday_md(date_str, weekly, new_hot)
        subject = f"[Monday 9am VN] GitHub Trending Top 10 weekly gain - {date_str}"
    else:
        feeds = daily_brief()
        md = render_daily_md(date_str, feeds)
        subject = f"[9am VN] AI/Tech/Science coffee brief - {date_str}"

    path = os.path.join(OUT_DIR, f"brief-{date_str}-{mode}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Saved: {path}")

    if not args.no_draft:
        ok, msg = try_gmail_draft(subject, md, args.email)
        print(msg)
    else:
        print("Draft skipped (--no-draft).")

if __name__ == "__main__":
    main()
