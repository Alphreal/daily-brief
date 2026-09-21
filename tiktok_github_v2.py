# -*- coding: utf-8 -*-
"""TikTok-style short v2: Top 10 GitHub tuan nay — ainius.net vibe.
Cinematic red-glow cards + real repo B-roll (Ken Burns) + karaoke captions.
720x1280 @24fps. Run: python tiktok_github_v2.py
"""
import os
import re
import io
import urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import brief

BASE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(BASE, "docs")
TMP = r"C:\Users\ADMIN\AppData\Local\Temp\opencode\ttv2"
W, H = 720, 1280
FPS = 24
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

BLACK = (10, 10, 12)
PANEL = (20, 22, 28)
BORDER = (48, 54, 61)
RED = (248, 81, 73)
WHITE = (255, 255, 255)
MUTED = (150, 156, 163)
GREEN = (63, 185, 80)

F_DISP = r"C:\Windows\Fonts\tahomabd.ttf"
F_BODY = r"C:\Windows\Fonts\tahoma.ttf"

def font(path, sz):
    return ImageFont.truetype(path, sz)

F_TITLE = font(F_DISP, 64)
F_BIG = font(F_DISP, 96)
F_SUB = font(F_DISP, 34)
F_TXT = font(F_BODY, 30)
F_CAP = font(F_DISP, 34)
F_SMALL = font(F_BODY, 24)
F_EYE = font(F_DISP, 26)

def safe(s):
    out = []
    for ch in (s or ""):
        o = ord(ch)
        if o > 0xFFFF or o < 32:
            continue
        out.append(ch)
    return "".join(out).strip()

def wrap(d, text, fnt, max_w):
    lines, cur = [], ""
    for w_ in text.split():
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

def fit_font(path, text, max_w, start):
    sz = start
    while sz > 20:
        f = ImageFont.truetype(path, sz)
        bb = ImageDraw.Draw(Image.new("RGB", (8, 8))).textbbox((0, 0), text, font=f)
        if bb[2] - bb[0] <= max_w:
            return f
        sz -= 6
    return ImageFont.truetype(path, 20)

def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)

def parse_gain(g):
    m = re.search(r"([\d,]+)", g or "")
    return int(m.group(1).replace(",", "")) if m else 0

# ---------- backdrop ----------
def make_glow():
    import math
    img = Image.new("RGB", (W, H), BLACK)
    px = img.load()
    cx, cy, rmax = W * 0.95, -H * 0.05, 900.0
    for y in range(0, H, 3):
        for x in range(0, W, 3):
            dist = math.hypot(x - cx, y - cy)
            k = max(0.0, 1 - dist / rmax) ** 2
            base = 10 + int(70 * k)
            px[x, y] = (base + 10, 12, 14)
    img = img.resize((W, H))
    # vignette + red edge lines
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 0, W, 7], fill=(RED[0], RED[1], RED[2], 255))
    d.rectangle([0, 0, 7, H], fill=(RED[0], RED[1], RED[2], 255))
    return img.convert("RGB")

GLOW = None

def glass_row(d, x0, y0, x1, y1, label, value, vcol=WHITE):
    d.rounded_rectangle([x0, y0, x1, y1], radius=16, fill=PANEL,
                        outline=BORDER, width=2)
    d.text((x0 + 24, y0 + 18), label, font=F_TXT, fill=MUTED)
    bb = d.textbbox((0, 0), value, font=F_SUB)
    d.text((x1 - 24 - (bb[2] - bb[0]), y0 + 14), value, font=F_SUB, fill=vcol)

def chapter_head(d, cur, total):
    d.text((36, 30), f"{cur:02d} / {total:02d}", font=F_SMALL, fill=MUTED)

# ---------- karaoke ----------
def layout_words(d, words, fnt, max_w, cx, y_top, lh):
    # words: [(text, color)] -> list of (x, y, text, color) + total height
    lines, cur, wsum = [], [], 0.0
    sp = d.textlength(" ", font=fnt)
    for t, c in words:
        ww = d.textlength(t, font=fnt)
        if wsum + ww > max_w and cur:
            lines.append(cur)
            cur, wsum = [], 0.0
        cur.append((t, c, ww))
        wsum += ww + sp
    if cur:
        lines.append(cur)
    out = []
    y = y_top
    for ln in lines:
        total = sum(w[2] for w in ln) + sp * (len(ln) - 1)
        x = cx - total / 2
        for t, c, ww in ln:
            out.append((x, y, t, c))
            x += ww + sp
        y += lh
    return out, y - y_top

def draw_karaoke(d, lines, fnt, cx, y_top, p, dwell=0.55):
    # lines: list of words-lists; reveal word-by-word, keywords red
    flat = []
    for ln in lines:
        flat.extend(ln)
        flat.append(None)
    total_w = sum(1 for w in flat if w)
    shown = int(p * total_w * 2.4) + 1 if p < 0.98 else total_w + 99
    vis, y = [], y_top
    # layout full first for stability
    placed, _ = layout_words(d, [w for w in flat if w], fnt, W - 120, cx, y_top, 52)
    k = 0
    for (x, yy, t, c) in placed:
        if k < shown:
            d.text((x, yy), t, font=fnt, fill=c)
        k += 1

# ---------- assets ----------
def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=25).read()

def repo_art(repo):
    """Return path to B-roll image (og:image, else owner avatar), or None."""
    os.makedirs(TMP, exist_ok=True)
    slug = repo.replace("/", "__")
    for ext in ("jpg", "png"):
        p = os.path.join(TMP, slug + "." + ext)
        if os.path.exists(p):
            return p
    owner = repo.split("/")[0]
    try:
        html = fetch(f"https://github.com/{repo}").decode("utf-8", "replace")
        m = re.search(r'<meta property="og:image" content="([^"]+)"', html)
        if m:
            raw = fetch(m.group(1))
            p = os.path.join(TMP, slug + ".jpg")
            open(p, "wb").write(raw)
            Image.open(p).convert("RGB").save(p)
            return p
    except Exception as e:
        print("  art-meta fail", repo, str(e)[:80])
    try:
        raw = fetch(f"https://github.com/{owner}.png")
        p = os.path.join(TMP, slug + ".png")
        open(p, "wb").write(raw)
        Image.open(p).convert("RGB").save(p)
        return p
    except Exception as e:
        print("  art-avatar fail", repo, str(e)[:80])
    return None

def cover_crop(img, zw=900, zh=1600):
    c = img.convert("RGB")
    s = max(zw / c.width, zh / c.height)
    c = c.resize((int(c.width * s) + 1, int(c.height * s) + 1), Image.BILINEAR)
    x = (c.width - zw) // 2
    y = (c.height - zh) // 2
    return c.crop((x, y, x + zw, y + zh))

# ---------- data ----------
TIER_CAP = [
    ("Quán quân tuần này!", "Quán quân"),
    ("Tăng tốc mạnh mẽ!", "mạnh mẽ"),
    ("Lọt top 3 gọi tên!", "top 3"),
    ("Đáng để mắt tới!", "để mắt"),
    ("Mới nổi đáng chú ý!", "đáng chú ý"),
    ("Cộng đồng chốt đơn!", "chốt đơn"),
]

def load_items():
    weekly, _ = brief.monday_github_trending()
    items, art = [], {}
    for i, r in enumerate(weekly[:10], 1):
        repo = safe(r["repo"])
        short = repo.split("/")[-1][:22]
        gain = parse_gain(r.get("gained", ""))
        cap_kw = TIER_CAP[(i - 1) % len(TIER_CAP)]
        w1 = [(short, WHITE), (f"+{gain:,}".replace(",", ".") + " sao", RED)]
        w2 = [(w_, RED if cap_kw[1] in w_ else WHITE) for w_ in cap_kw[0].split()]
        items.append({
            "rank": i, "repo": repo, "short": short, "gain": gain,
            "gain_s": safe(r.get("gained", "")), "total": safe(r.get("total", "")),
            "desc": safe(r.get("desc", ""))[:120],
            "cap": [w1, w2],
        })
    print("Fetching B-roll art...")
    for it in items:
        art[it["repo"]] = repo_art(it["repo"])
    return items, art

# ---------- scenes ----------
CARD_DUR, ROLL_DUR = 2.6, 3.8
HOOK_DUR, CTA_DUR = 2.5, 3.0

def draw_card(d, it, ch, total, p):
    chapter_head(d, ch, total)
    center(d, W / 2, 120, f"HẠNG {it['rank']} • {it['gain_s']} SAO/TUẦN", F_EYE, RED)
    name_lines = wrap(d, it["short"], F_BIG, W - 100)[:2]
    # auto-fit longest line
    fnt = F_BIG
    if name_lines:
        longest = max(name_lines, key=lambda s: d.textlength(s, font=fnt))
        fnt = fit_font(F_DISP, longest, W - 100, 96)
    y = 190
    for ln in name_lines:
        center(d, W / 2, y, ln, fnt, WHITE)
        y += 105
    y0 = y + 30
    glass_row(d, 60, y0, W - 60, y0 + 92, "Tăng trong tuần", f"+{it['gain']:,}".replace(",", "."), GREEN)
    glass_row(d, 60, y0 + 112, W - 60, y0 + 204, "Tổng số sao", it["total"], WHITE)
    dl = wrap(d, it["desc"], F_TXT, W - 170)[:3]
    y = y0 + 240
    for ln in dl:
        center(d, W / 2, y, ln, F_TXT, MUTED)
        y += 44

def draw_roll(base_img, d, it, ch, total, p, cap_lines):
    # Ken Burns zoom 1.00 -> 1.09
    z = 1.0 + 0.09 * smooth(p)
    zw, zh = W, H
    cw, chh = int(zw * z), int(zh * z)
    crop = base_img.crop(((base_img.width - cw) // 2, (base_img.height - chh) // 2 - int(30 * p),
                          (base_img.width + cw) // 2, (base_img.height + chh) // 2 - int(30 * p)))
    frame = crop.resize((W, H), Image.BILINEAR)
    # bottom scrim
    ov = Image.new("L", (1, H), 0)
    for y in range(H):
        k = max(0, (y - H * 0.45) / (H * 0.55))
        ov.putpixel((0, y), int(190 * k * k))
    black = Image.new("RGB", (W, H), (0, 0, 0))
    frame = Image.composite(black, frame, ov.resize((W, H)))
    out = Image.fromarray(__import__("numpy").asarray(frame))
    d2 = ImageDraw.Draw(out, "RGBA")
    d2.rectangle([0, 0, W, 7], fill=(RED[0], RED[1], RED[2], 255))
    d2.text((36, 30), f"{ch:02d} / {total:02d}", font=F_SMALL, fill=MUTED)
    # repo chip
    chip = it["repo"][:34]
    bw = d2.textlength(chip, font=F_SMALL) + 40
    d2.rounded_rectangle([(W - bw) / 2, 120, (W + bw) / 2, 168], radius=24, fill=(0, 0, 0, 160))
    center(d2, W / 2, 128, chip, F_SMALL, WHITE)
    draw_karaoke(d2, cap_lines, F_CAP, W / 2, 950, p)
    return out

def draw_hook(d, p):
    chapter_head(d, 1, 12)
    center(d, W / 2, 150, "SỐ LIỆU THẬT • 10 REPO", F_EYE, RED)
    center(d, W / 2, 330, "TOP 10", F_BIG, WHITE)
    center(d, W / 2, 440, "GITHUB", F_BIG, RED)
    center(d, W / 2, 550, "TUẦN NÀY", F_BIG, WHITE)
    y = 730 + int(16 * (1 - smooth(min(1, p * 3))))
    d.rounded_rectangle([170, y, W - 170, y + 96], radius=48, fill=GREEN)
    center(d, W / 2, y + 24, "BẮT ĐẦU!", F_SUB, WHITE)
    draw_karaoke(d, [[("Top", WHITE), ("10", RED), ("GitHub", WHITE), ("tuần", WHITE), ("này", WHITE)]], F_CAP, W / 2, 950, p)

def draw_cta(d, top3):
    chapter_head(d, 12, 12)
    center(d, W / 2, 150, "REPO NÀO ĐÁNG CÀI NHẤT?", F_SUB, WHITE)
    y = 260
    for it in top3:
        glass_row(d, 60, y, W - 60, y + 92, f"#{it['rank']} {it['short'][:18]}", f"+{it['gain']:,}".replace(",", "."), GREEN)
        y += 112
    center(d, W / 2, y + 60, "Lưu lại • Follow để nhận", F_TXT, MUTED)
    center(d, W / 2, y + 108, "tin AI mỗi ngày", F_TXT, WHITE)
    center(d, W / 2, y + 180, "#GitHub #AI #LậpTrình", F_SMALL, (88, 166, 255))

def main():
    import imageio.v2 as iio
    import numpy as np
    import shutil
    global GLOW
    GLOW = make_glow()
    items, art = load_items()
    print(f"Items: {len(items)}")
    # pre-crop B-roll
    rolls = {}
    for it in items:
        p = art.get(it["repo"])
        if p:
            try:
                rolls[it["repo"]] = cover_crop(Image.open(p))
                print("  roll ok:", it["repo"])
            except Exception as e:
                print("  roll bad:", it["repo"], str(e)[:60])
    total_ch = 12
    per_item = CARD_DUR + ROLL_DUR
    total_dur = HOOK_DUR + len(items) * per_item + CTA_DUR
    N = int(total_dur * FPS)
    mp4 = os.path.join(BASE, "tiktok-github-v2.mp4")
    w = iio.get_writer(mp4, fps=FPS, codec="libx264", quality=8,
                       ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "faststart"])
    cover_saved = False
    for i in range(N):
        t = i / FPS
        img = GLOW.copy()
        d = ImageDraw.Draw(img, "RGBA")
        if t < HOOK_DUR:
            draw_hook(d, t / HOOK_DUR)
            out = img
        else:
            t2 = t - HOOK_DUR
            idx = int(t2 // per_item)
            if idx < len(items):
                it = items[idx]
                lt = t2 % per_item
                if lt < CARD_DUR:
                    draw_card(d, it, idx + 2, total_ch, lt / CARD_DUR)
                    out = img
                else:
                    base = rolls.get(it["repo"])
                    if base is None:
                        draw_card(d, it, idx + 2, total_ch, 1.0)
                        out = img
                    else:
                        out = draw_roll(base, d, it, idx + 2, total_ch,
                                        (lt - CARD_DUR) / ROLL_DUR, it["cap"])
            else:
                draw_cta(d, items[:3])
                out = img
        if not cover_saved and i / FPS > 1.0:
            out.save(os.path.join(BASE, "tiktok-github-v2-cover.png"))
            cover_saved = True
        w.append_data(np.asarray(out.convert("RGB")))
        if (i + 1) % 240 == 0:
            print(f"  {i + 1}/{N}")
    w.close()
    print(f"Saved: {mp4} ({os.path.getsize(mp4) // 1024} KB)")
    cap = ("Top 10 GitHub tuần này (số liệu thật, Phần 1): quán quân tăng hơn "
           "8.000 sao chỉ trong 1 tuần! Repo nào đáng cài nhất? "
           "#GitHub #LậpTrình #OpenSource #CôngNghệ #AI #TinCôngNghệ")
    open(os.path.join(BASE, "tiktok-github-v2-caption.txt"), "w", encoding="utf-8").write(cap + "\n")
    for f_ in ("tiktok-github-v2.mp4", "tiktok-github-v2-cover.png", "tiktok-github-v2-caption.txt"):
        shutil.copy(os.path.join(BASE, f_), os.path.join(DOCS, f_))
    print("Copied to docs/")

if __name__ == "__main__":
    main()
