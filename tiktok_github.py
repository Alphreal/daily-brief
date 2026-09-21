#!/usr/bin/env python3
"""TikTok-style 9:16 AI-news short: Top 10 GitHub tuan nay (Vietnamese).
720x1280 @24fps, dark dev-terminal theme, burned-in VN captions.
Run: python tiktok_github.py
Outputs: tiktok-github-tuan-nay.mp4 / cover.png / caption.txt (+ docs/ copies)
"""
import os
import re
from PIL import Image, ImageDraw, ImageFont
import brief

BASE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(BASE, "docs")
W, H = 720, 1280
FPS = 24

BG = (13, 17, 23)
PANEL = (22, 27, 34)
BORDER = (48, 54, 61)
ACCENT = (88, 166, 255)
GREEN = (63, 185, 80)
TEXT = (240, 246, 252)
MUTED = (139, 148, 158)
AMBER = (210, 153, 34)
RED = (248, 81, 73)

FONT_FILES = [
    r"C:\Windows\Fonts\tahoma.ttf",
    r"C:\Windows\Fonts\arial.ttf",
]

def font(sz):
    for p in FONT_FILES:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default(size=sz)

F_HOOK = font(62)
F_TITLE = font(40)
F_BODY = font(29)
F_CAP = font(30)
F_SMALL = font(24)
F_BADGE = font(28)

def safe(s):
    # Tahoma-safe: drop non-BMP (emoji), controls, and risky symbols
    out = []
    for ch in (s or ""):
        o = ord(ch)
        if o > 0xFFFF or o < 32:
            continue
        if ch in "★☆→←↑↓✓✔✗":
            continue
        out.append(ch)
    return "".join(out).strip()

def wrap(d, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines

def center(d, cx, y, s, fnt, fill):
    bb = d.textbbox((0, 0), s, font=fnt)
    d.text((cx - (bb[2] - bb[0]) / 2, y), s, font=fnt, fill=fill)

def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)

def parse_gain(g):
    m = re.search(r"([\d,]+)", g or "")
    return int(m.group(1).replace(",", "")) if m else 0

TIER = {1: "Dan dau tuan nay!", 2: "Tang manh!", 3: "Top 3 goi ten!"}
CAP_EXTRA = ["Dang xem!", "Moi noi!", "Chu y!", "Luu lai de cai sau!"]

def load_items():
    weekly, _ = brief.monday_github_trending()
    items = []
    for i, r in enumerate(weekly[:10], 1):
        items.append({
            "rank": i,
            "repo": safe(r["repo"]),
            "gain": parse_gain(r.get("gained", "")),
            "gain_s": safe(r.get("gained", "")),
            "total": safe(r.get("total", "")),
            "desc": safe(r.get("desc", ""))[:140],
            "tier": TIER.get(i, CAP_EXTRA[(i - 4) % len(CAP_EXTRA)]),
        })
    return items

HOOK_DUR, ITEM_DUR, CTA_DUR = 2.5, 2.2, 2.0

def draw_hook(d, p):
    glow = int(6 + 4 * smooth(p))
    d.rounded_rectangle([60, 300, W - 60, 980], radius=28, fill=PANEL,
                        outline=ACCENT, width=3 + glow // 4)
    center(d, W / 2, 360, "TOP 10 GITHUB", F_HOOK, ACCENT)
    center(d, W / 2, 445, "TUAN NAY", F_HOOK, TEXT)
    center(d, W / 2, 560, "10 repo duoc sao", F_BODY, MUTED)
    center(d, W / 2, 605, "nhieu nhat tuan qua", F_BODY, MUTED)
    y = 700 + int(14 * (1 - smooth(min(1, p * 3))))
    d.rounded_rectangle([150, y, W - 150, y + 90], radius=45, fill=GREEN)
    center(d, W / 2, y + 22, "BAT DAU!", F_TITLE, (255, 255, 255))
    center(d, W / 2, 860, "AI + agent + open source", F_SMALL, MUTED)

def draw_item(d, it, p):
    n = it["rank"]
    # slide-up entrance
    off = int(40 * (1 - smooth(min(1, p * 4))))
    # counter
    d.text((48, 120), f"{n}/10", font=F_SMALL, fill=MUTED)
    # rank circle
    col = AMBER if n <= 3 else ACCENT
    d.ellipse([48, 170 + off, 128, 250 + off], fill=col)
    center(d, 88, 182 + off, str(n), F_TITLE, (13, 17, 23))
    # repo name
    lines = wrap(d, it["repo"], F_TITLE, W - 220)[:2]
    y = 170 + off
    for ln in lines:
        d.text((150, y), ln, font=F_TITLE, fill=TEXT)
        y += 48
    # gain badge with count-up
    shown = int(it["gain"] * smooth(min(1, p * 1.6)))
    badge = f"+{shown:,} sao/tuan"
    bw = d.textlength(badge, font=F_BADGE) + 44
    d.rounded_rectangle([48, 300 + off, 48 + bw, 356 + off], radius=28, fill=GREEN)
    d.text((70, 310 + off), badge, font=F_BADGE, fill=(255, 255, 255))
    d.text((48, 372 + off), f"Tong: {it['total']} sao", font=F_SMALL, fill=MUTED)
    # desc panel (sized to content) + verdict
    dlines = wrap(d, it["desc"], F_BODY, W - 160)[:4]
    vlines = wrap(d, "Nhan xet: " + safe(brief.verdict_for_repo(it["repo"], it["desc"])), F_BODY, W - 160)[:3]
    panel_b = 460 + off + (len(dlines) + len(vlines)) * 42 + 34
    d.rounded_rectangle([48, 430 + off, W - 48, panel_b], radius=20,
                        fill=PANEL, outline=BORDER, width=2)
    y = 460 + off
    for ln in dlines:
        d.text((78, y), ln, font=F_BODY, fill=TEXT)
        y += 42
    for ln in vlines:
        d.text((78, y), ln, font=F_BODY, fill=AMBER)
        y += 42
    # caption bar (burned-in sub)
    cap = f"Hang {n}: {it['tier']}"
    d.rounded_rectangle([48, 960, W - 48, 1060], radius=16, fill=(0, 0, 0))
    center(d, W / 2, 988, cap, F_CAP, (255, 214, 10) if n <= 3 else TEXT)

def draw_cta(d, p):
    d.rounded_rectangle([60, 340, W - 60, 940], radius=28, fill=PANEL,
                        outline=GREEN, width=3)
    center(d, W / 2, 400, "Luu lai", F_HOOK, GREEN)
    center(d, W / 2, 485, "de cai sau!", F_HOOK, TEXT)
    center(d, W / 2, 620, "Follow de nhan", F_BODY, MUTED)
    center(d, W / 2, 665, "tin AI moi ngay", F_BODY, MUTED)
    center(d, W / 2, 780, "#GitHub #AI #LapTrinh", F_SMALL, ACCENT)
    center(d, W / 2, 820, "#OpenSource #CongNghe", F_SMALL, ACCENT)

def render_frame(items, i, total):
    t = i / FPS
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # top brand bar
    d.rectangle([0, 0, W, 90], fill=(0, 0, 0))
    d.text((36, 24), "AI News - Tin tuc AI", font=F_SMALL, fill=TEXT)
    d.text((W - 200, 24), "Top 10 tuan", font=F_SMALL, fill=MUTED)
    acc = HOOK_DUR
    if t < acc:
        draw_hook(d, t / HOOK_DUR)
        seg = "hook"
    else:
        t2 = t - acc
        idx = int(t2 // ITEM_DUR)
        if idx < len(items):
            draw_item(d, items[idx], (t2 % ITEM_DUR) / ITEM_DUR)
            seg = f"item{idx + 1}"
        else:
            draw_cta(d, min(1.0, (t2 - len(items) * ITEM_DUR) / CTA_DUR))
            seg = "cta"
    # progress bar
    d.rectangle([0, H - 14, W, H], fill=BORDER)
    d.rectangle([0, H - 14, W * (i + 1) / total, H], fill=RED)
    return img, seg

def main():
    import imageio.v2 as iio
    import shutil
    items = load_items()
    print(f"Items: {len(items)}")
    total_dur = HOOK_DUR + len(items) * ITEM_DUR + CTA_DUR
    N = int(total_dur * FPS)
    print(f"Rendering {N} frames {W}x{H}...")
    mp4 = os.path.join(BASE, "tiktok-github-tuan-nay.mp4")
    w = iio.get_writer(mp4, fps=FPS, codec="libx264", quality=8,
                       ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "faststart"])
    cover_saved = False
    for i in range(N):
        img, seg = render_frame(items, i, N)
        if seg == "hook" and not cover_saved and i / FPS > 1.2:
            cover = os.path.join(BASE, "tiktok-github-cover.png")
            img.save(cover)
            cover_saved = True
            print("cover:", cover)
        w.append_data(__import__("numpy").asarray(img))
        if (i + 1) % 120 == 0:
            print(f"  {i + 1}/{N}")
    w.close()
    print(f"Saved: {mp4} ({os.path.getsize(mp4) // 1024} KB)")
    cap = ("Top 10 GitHub tuan nay: 10 repo duoc sao nhieu nhat! "
           "Con so nao khien ban bat ngo nhat? Binh luan so thu tu! "
           "#GitHub #LapTrinh #OpenSource #CongNghe #AI #TinCongNghe #Repo")
    with open(os.path.join(BASE, "tiktok-github-caption.txt"), "w", encoding="utf-8") as f:
        f.write(cap + "\n")
    for p in (mp4, cover, os.path.join(BASE, "tiktok-github-caption.txt")):
        shutil.copy(p, os.path.join(DOCS, os.path.basename(p)))
    print("Copied to docs/")

if __name__ == "__main__":
    main()
