"""brief_render.py - pure render helpers for brief.py (md + html). Stdlib only."""

import html
import re


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
    if any(
        k in t for k in ["nasa", "space", "mars", "moon", "telescope", "orbit", "asteroid", "comet"]
    ):
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
    return [
        (n, items[0])
        for n, items in feeds.items()
        if items and not items[0][0].startswith("RSS failed")
    ][:3]


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
            L.append(
                f"- #{i} {r['repo']} ({r['gained']}) - {verdict_for_repo(r['repo'], r['desc'])}"
            )
    else:
        L.append("- Weekly tracker empty today - using new-hot below as fallback.")
        for h in new_hot[:3]:
            L.append(
                f"- {h['repo']} ({h.get('stars')} stars) - {verdict_for_repo(h['repo'], h['desc'])}"
            )
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
    for name, (t, link, s, _p) in picks:
        L.append(f"- [{name}] {t}")
        if s:
            L.append(f"  In short: {s}")
        L.append(f"  {link}")
    L.append("")
    for name, items in feeds.items():
        L.append(f"## {name}")
        for t, link, s, p in items:
            L.append(f"- {t}" + (f" ({p})" if p else ""))
            if s:
                L.append(f"  Summary: {s}")
                L.append(f"  {takeaway_for(t, s)}")
            else:
                L.append(
                    "  Note: discussion thread, no article summary - skim comments for lived experience."
                )
                L.append(f"  {takeaway_for(t, '')}")
            L.append(f"  Link: {link}")
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
<link rel="stylesheet" href="assets/vendor/aos/aos.css">
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
.placeholder{{border:1.5px dashed #a8a29e;border-radius:12px;padding:14px 16px;margin:12px 0;background:#fafaf9;color:#57534e;font-size:14px;list-style:none}}
.toc{{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 4px;position:sticky;top:0;z-index:5;background:#f7f7f5;padding:8px 0}}
.hero{{text-align:center}}
.hero h1{{font-size:30px}}
.hero3d{{position:relative;overflow:hidden;border-radius:14px;border:1px solid #e7e5e4;background:radial-gradient(120% 100% at 50% 0%,#ffffff 0%,#f7f7f5 70%);padding:30px 20px;text-align:center;margin:4px 0 16px}}
.hero3d canvas{{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}}
.hero3d h1{{position:relative;font-size:30px}}
.hero3d .muted{{position:relative}}
@media print{{.hero3d canvas{{display:none}}}}
.chapter{{background:#fff;border:1px solid #e7e5e4;border-radius:14px;padding:4px 20px 16px;margin:20px 0}}
.chapter h2{{margin-top:14px}}
.toc a{{background:#fff;border:1px solid #e7e5e4;border-radius:999px;padding:4px 12px;font-size:13px;color:#1a1a1a;text-decoration:none}}
@media(min-width:1100px){{.wrap{{max-width:1100px}}.grid2{{grid-template-columns:1fr 1fr 1fr}}}}
@media print{{.topbar{{display:none}}.toc{{position:static;background:#fff}}.wrap{{max-width:100%;padding:0}}body{{background:#fff}}.card,.tldr{{break-inside:avoid}}[data-aos]{{opacity:1!important;transform:none!important}}}}
@media (prefers-reduced-motion:reduce){{[data-aos]{{opacity:1!important;transform:none!important;transition:none!important}}}}
</style>
</head>
<body>
<div class="wrap mx-auto px-4">
<div class="topbar"><a href="index.html">&larr; Alph</a><span class="muted">Daily Brief</span></div>
{body_inner}
</div>
<script src="assets/vendor/aos/aos.js" defer></script>
<script type="importmap">{{"imports":{{"three":"./assets/vendor/three/three.module.min.js"}}}}</script>
<script type="module">
import * as THREE from 'three';
(function main() {{
try {{
if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return;
const wrap = document.querySelector('.wrap');
const h1 = wrap && wrap.querySelector('h1');
if (!wrap || !h1) return;
const sub = (h1.nextElementSibling && h1.nextElementSibling.classList.contains('muted')) ? h1.nextElementSibling : null;
const hero = document.createElement('div');
hero.className = 'hero3d';
wrap.insertBefore(hero, h1);
hero.appendChild(h1);
if (sub) hero.appendChild(sub);
const canvas = document.createElement('canvas');
hero.prepend(canvas);
const W = hero.clientWidth || 800, H = hero.clientHeight || 220;
const renderer = new THREE.WebGLRenderer({{canvas: canvas, alpha: true, antialias: false}});
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.setSize(W, H, false);
const scene = new THREE.Scene();
const cam = new THREE.OrthographicCamera(-W/2, W/2, H/2, -H/2, 0.1, 10);
cam.position.z = 5;
const cols = Math.max(24, Math.min(90, Math.floor(W / 12))), rows = 12;
const n = cols * rows;
const pos = new Float32Array(n * 3), col = new Float32Array(n * 3);
const ink = new THREE.Color('#1a1a1a'), blue = new THREE.Color('#0f62fe');
let k = 0;
for (let i = 0; i < cols; i++) {{
  for (let j = 0; j < rows; j++) {{
    pos[k*3] = (i / (cols-1) - 0.5) * (W - 24);
    pos[k*3+1] = (0.5 - j / (rows-1)) * (H - 24);
    pos[k*3+2] = 0;
    const c = (k % 23 === 0) ? blue : ink;
    col[k*3] = c.r; col[k*3+1] = c.g; col[k*3+2] = c.b;
    k++;
  }}
}}
const geo = new THREE.BufferGeometry();
geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
const pts = new THREE.Points(geo, new THREE.PointsMaterial({{size: 2.2, vertexColors: true, transparent: true, opacity: 0.5, sizeAttenuation: false}}));
scene.add(pts);
let run = true, t = 0;
const base = pos.slice();
function frame() {{
  if (!run) return;
  requestAnimationFrame(frame);
  t += 0.012;
  const p = geo.attributes.position.array;
  for (let i = 0; i < n; i++) {{
    p[i*3+1] = base[i*3+1] + Math.sin(base[i*3] * 0.03 + t) * 7 + Math.cos(i * 0.4 + t * 0.7) * 4;
  }}
  geo.attributes.position.needsUpdate = true;
  renderer.render(scene, cam);
}}
if ('IntersectionObserver' in window) {{
  new IntersectionObserver(function(es){{ run = es[0].isIntersecting && !document.hidden; if (run) frame(); }}, {{threshold: 0.05}}).observe(hero);
}}
document.addEventListener('visibilitychange', function(){{ run = !document.hidden; if (run) frame(); }});
let rT;
window.addEventListener('resize', function(){{ clearTimeout(rT); rT = setTimeout(function(){{ location.reload(); }}, 400); }});
frame();
}} catch (e) {{ /* static gradient fallback stays */ }}
}})();
</script>
<script defer>
document.addEventListener('DOMContentLoaded',function(){{try{{if(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches)return;if(!window.AOS)return;document.querySelectorAll('.card').forEach(function(el){{if(!el.hasAttribute('data-aos'))el.setAttribute('data-aos','fade-up')}});AOS.init({{once:true,duration:300,offset:60}});}}catch(e){{}}}});
</script>
</body>
</html>"""


def render_daily_html(date_str, feeds):
    tldr = ['<div class="tldr"><h2>TL;DR &mdash; 3 to read first</h2>']
    picks = tldr_picks(feeds)
    if not picks:
        tldr.append(
            '<div class="card muted">All feeds failed today &mdash; see sections below, or rerun later.</div>'
        )
    for name, (t, link, s, _p) in picks:
        tldr.append(
            f'<div class="card"><span class="badge">{esc(name)}</span>'
            f'<a href="{esc(link)}"><b>{esc(t)}</b></a>'
            + (f'<div class="muted">{esc(s)}</div>' if s else "")
            + "</div>"
        )
    tldr.append("</div>")
    secs = [
        f"<h1>Coffee brief &mdash; AI / Tech / Science &mdash; {esc(date_str)} (10 min)</h1>",
        "<div class='muted'>Same content as .md + Gmail draft.</div>",
    ] + tldr
    for name, items in feeds.items():
        secs.append(f'<div class="sec"><h2>{esc(name)}</h2><div class="grid2">')
        for t, link, s, p in items:
            if s:
                inner = f'<div class="muted">{esc(s)}</div><div class="muted">{esc(takeaway_for(t, s))}</div>'
            else:
                inner = f'<div class="muted">Discussion thread, no summary &mdash; skim comments.</div><div class="muted">{esc(takeaway_for(t, ""))}</div>'
            secs.append(
                f'<div class="card"><a href="{esc(link)}"><b>{esc(t)}</b></a>'
                + (f' <span class="muted">({esc(p)})</span>' if p else "")
                + f'<br>{inner}<br><a href="{esc(link)}">{esc(link)}</a></div>'
            )
        secs.append("</div></div>")
    secs.append(f'<div class="card muted">{esc(DAILY_BOTTOM)}</div>')
    return html_shell(f"Coffee brief - {date_str}", "\n".join(secs))


def render_monday_html(date_str, weekly, new_hot):
    tldr = ['<div class="tldr"><h2>TL;DR &mdash; my take</h2>']
    if weekly:
        for i, r in enumerate(weekly[:3], 1):
            tldr.append(
                f'<div class="card"><span class="badge">#{i} {esc(r["repo"])}</span> '
                f'<span class="badge">{esc(r["gained"])}</span>'
                f'<div class="muted">{esc(verdict_for_repo(r["repo"], r["desc"]))}</div></div>'
            )
    else:
        for h in new_hot[:3]:
            tldr.append(
                f'<div class="card"><b>{esc(h["repo"])}</b><div class="muted">{esc(verdict_for_repo(h["repo"], h["desc"]))}</div></div>'
            )
    tldr.append("</div>")
    secs = [
        f"<h1>Monday GitHub Trending &mdash; weekly gain &mdash; {esc(date_str)}</h1>",
        "<div class='muted'>Top 10 by stars GAINED last week. Read the verdict, not just the stars. "
        "<a href='https://github.com/trending?since=weekly'>Verify live</a></div>",
    ] + tldr
    secs.append('<div class="sec"><h2>Top 10 weekly gain</h2><div class="grid2">')
    for i, r in enumerate(weekly, 1):
        secs.append(
            f'<div class="card"><span class="badge">#{i}</span>'
            f'<a href="{esc(r["url"])}"><b>{esc(r["repo"])}</b></a> '
            f'<span class="badge">{esc(r["gained"])} / {esc(r["total"])} total</span>'
            f'<div class="muted">{esc(r["desc"])}</div>'
            f'<div class="muted">Verdict: {esc(verdict_for_repo(r["repo"], r["desc"]))}</div></div>'
        )
    secs.append("</div></div>")
    secs.append('<div class="sec"><h2>New hot (created last 14 days)</h2>')
    for h in new_hot:
        secs.append(
            f'<div class="card"><a href="{esc(h["url"])}"><b>{esc(h["repo"])}</b></a> '
            f'<span class="badge">{esc(str(h.get("stars")))} stars</span>'
            f'<div class="muted">{esc(h["desc"])}</div>'
            f'<div class="muted">Verdict: {esc(verdict_for_repo(h["repo"], h["desc"]))}</div></div>'
        )
    secs.append("</div>")
    secs.append(f'<div class="card muted">{esc(MONDAY_BOTTOM)}</div>')
    return html_shell(f"Monday Trending - {date_str}", "\n".join(secs))


def render_index_html(entries):
    # entries: list of (filename, label, date_str) sorted desc
    rows = [
        "<h1>NEWS</h1>",
        '<div class="tldr"><b>Latest</b> &mdash; start here, then browse below.</div>',
    ]
    for fn, label, ds in entries:
        rows.append(
            f'<div class="card"><a href="{esc(fn)}"><b>{esc(label)}</b></a> '
            f'<span class="badge">{esc(ds)}</span></div>'
        )
    if not entries:
        rows.append(
            '<div class="card muted">No issues yet &mdash; run: python brief.py --mode daily</div>'
        )
    return html_shell("Daily Brief - index", "\n".join(rows))
