#!/usr/bin/env python3
"""Zoom Fatigue - Classroom Edition looping clip (students/teachers).
Outputs: zoom-fatigue-classroom.mp4 / .webm / .gif + docs/zoom-fatigue.html
Stdlib + Pillow + numpy + imageio + imageio-ffmpeg (bundled ffmpeg binary).
Run: python zoom_fatigue.py
"""
import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(BASE, "docs")

W, H = 1280, 720
FPS = 24
DUR = 8.0
N = int(FPS * DUR)  # 192

NAMES = ["Mai", "Leo", "Ava", "Ben", "Ms. An", "Sam", "Nora", "Kai", "Linh"]
IS_TEACHER = [False, False, False, False, True, False, False, False, False]
TILE_BG = ["#DBEAFE", "#FEF3C7", "#DCFCE7", "#FFE4E6", "#FFF7ED",
           "#FFEDD5", "#CCFBF1", "#F3E8FF", "#E0F2FE"]
SKIN = ["#FFDBB4", "#F1C27D", "#E0AC69", "#FFEDD5", "#F1C27D",
        "#C68642", "#FFDBB4", "#8D5524", "#E0AC69"]
HAIR = ["#1F2937", "#4B5563", "#111827", "#6B7280", "#78350F",
        "#1F2937", "#374151", "#111827", "#4B5563"]

def hexcol(s):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))

def lerp(a, b, t):
    return int(a + (b - a) * t)

def lerp_col(c1, c2, t):
    return (lerp(c1[0], c2[0], t), lerp(c1[1], c2[1], t), lerp(c1[2], c2[2], t))

def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)

def fatigue_at(t):
    if t < 0.20:
        return 0.0
    if t < 0.60:
        return smooth((t - 0.20) / 0.40)
    if t < 0.78:
        return 1.0
    return 1.0 - smooth((t - 0.78) / 0.22)

def font(sz):
    try:
        return ImageFont.load_default(size=sz)
    except TypeError:
        return ImageFont.load_default()

F_TITLE = font(34)
F_SUB = font(22)
F_TILE = font(20)
F_SMALL = font(18)
F_BIG = font(30)
F_BANNER = font(28)
F_ZZZ = font(26)

def text_center(d, cx, y, s, fnt, fill):
    bb = d.textbbox((0, 0), s, font=fnt)
    tw = bb[2] - bb[0]
    d.text((cx - tw / 2, y), s, font=fnt, fill=fill)

def draw_battery(d, x, y, w, h, pct):
    # pct 0..100
    d.rounded_rectangle([x, y, x + w, y + h], radius=6, outline=(60, 60, 60), width=2, fill=(255, 255, 255))
    d.rectangle([x + w + 2, y + h * 0.3, x + w + 8, y + h * 0.7], fill=(60, 60, 60))
    inner_w = int((w - 8) * pct / 100)
    if pct > 50:
        col = (34, 197, 94)
    elif pct > 30:
        col = (245, 158, 11)
    else:
        col = (239, 68, 68)
    if inner_w > 0:
        d.rounded_rectangle([x + 4, y + 4, x + 4 + inner_w, y + h - 4], radius=4, fill=col)

def draw_face(d, cx, cy, r, skin, hair_c, f, seed):
    # hair back
    d.ellipse([cx - r - 6, cy - r - 10, cx + r + 6, cy + r + 4], fill=hair_c)
    droop = f * 9
    cy2 = cy + droop
    d.ellipse([cx - r, cy2 - r, cx + r, cy2 + r], fill=skin)
    # hair top arc
    d.arc([cx - r - 6, cy - r - 14, cx + r + 6, cy2 + 10], start=200, end=340, fill=hair_c, width=10)
    # eyes
    eo = 18 * (1 - f * 0.72)  # openness height
    eo = max(4, eo)
    ex = 15
    ey = cy2 - 4
    for sx in (-1, 1):
        exx = cx + sx * ex
        d.ellipse([exx - 11, ey - eo / 2, exx + 11, ey + eo / 2], fill=(255, 255, 255), outline=(30, 30, 30), width=2)
        pr = 5 if f < 0.6 else 4
        # pupils look down more when tired
        py = ey + f * 3
        d.ellipse([exx - pr, py - pr, exx + pr, py + pr], fill=(17, 24, 39))
        if f > 0.45:
            # bags
            alpha_bag = (f - 0.45) / 0.55
            bag_col = (120 + int(30 * (1 - alpha_bag)), 113, 108)
            d.arc([exx - 12, ey + 2, exx + 12, ey + 16], start=10, end=170, fill=bag_col, width=2)
    # mouth: smile -> flat -> frown
    mw, mh = 26, 14
    mx0, my0 = cx - mw // 2, cy2 + 18
    if f < 0.35:
        d.arc([mx0, my0 - 6, mx0 + mw, my0 + mh], start=15, end=165, fill=(30, 30, 30), width=3)
    elif f < 0.7:
        d.line([mx0 + 3, my0 + 6, mx0 + mw - 3, my0 + 6], fill=(30, 30, 30), width=3)
    else:
        d.arc([mx0, my0 - 2, mx0 + mw, my0 + mh + 6], start=195, end=345, fill=(30, 30, 30), width=3)
    # cheeks fade when tired
    if f < 0.5:
        blush = (252, 165, 165)
        d.ellipse([cx - r + 4, cy2 + 8, cx - r + 16, cy2 + 16], fill=blush)
        d.ellipse([cx + r - 16, cy2 + 8, cx + r - 4, cy2 + 16], fill=blush)

def phase_info(t):
    if t < 0.20:
        return ("Hour 1 - Fresh & focused", "9 cameras on - eyes bright", "#FFFFFF", "#111827")
    if t < 0.45:
        return ("Hour 3 - Eyes tired, focus slips", "staring - blinking less - fidgeting", "#FEF3C7", "#92400E")
    if t < 0.78:
        return ("Hour 5 - Drained: cameras off", "brain fog - eye strain - quiet class", "#FEE2E2", "#991B1B")
    if t < 0.92:
        return ("Fix: 20-20-20 - stretch - water", "every 20 min look 20 ft away - stand - cameras can rest", "#DCFCE7", "#166534")
    return ("Hour 1 - Fresh & focused", "loop - replay for your class", "#FFFFFF", "#111827")

def render_frame(i):
    t = i / N
    f = fatigue_at(t)
    img = Image.new("RGB", (W, H), (247, 247, 245))
    d = ImageDraw.Draw(img)

    # top bar
    d.rectangle([0, 0, W, 86], fill=(255, 255, 255))
    d.line([0, 86, W, 86], fill=(231, 229, 228), width=2)
    d.text((48, 14), "Zoom Fatigue - Classroom Edition", font=F_TITLE, fill=(17, 24, 39))
    d.text((48, 50), "Why long video classes drain you + what helps", font=F_SUB, fill=(107, 114, 128))
    # clock
    mins = int(9 * 60 + t * 360)
    if t > 0.92:
        clock_s = "Replay 9:00 AM"
    else:
        hh = mins // 60
        mm = mins % 60
        ap = "AM" if hh < 12 else "PM"
        hh12 = hh if 1 <= hh <= 12 else (hh - 12 if hh > 12 else hh)
        clock_s = f"{hh12}:{mm:02d} {ap}"
    bb = d.textbbox((0, 0), clock_s, font=F_BIG)
    d.text((W - 48 - (bb[2] - bb[0]), 12), clock_s, font=F_BIG, fill=(17, 24, 39))
    batt = 100 - f * 75
    draw_battery(d, W - 280, 50, 110, 20, batt)
    d.text((W - 160, 48), f"Energy {int(batt)}%", font=F_SMALL, fill=(107, 114, 128))

    # grid
    mx, gap = 48, 14
    top_y, bot_y = 100, 596
    tw = (W - 2 * mx - 2 * gap) // 3
    th = (bot_y - top_y - 2 * gap) // 3
    for idx in range(9):
        row, col = divmod(idx, 3)
        x0 = mx + col * (tw + gap)
        y0 = top_y + row * (th + gap)
        x1, y1 = x0 + tw, y0 + th
        # staggered camera-off
        thresh = {2: 0.62, 5: 0.74, 7: 0.84}.get(idx, 2.0)
        cam_off = (f > thresh) and (t < 0.88)
        if cam_off:
            d.rounded_rectangle([x0, y0, x1, y1], radius=14, fill=(17, 24, 39))
            init = "".join([p[0] for p in NAMES[idx].split() if p]).upper()[:2]
            text_center(d, (x0 + x1) / 2, y0 + th / 2 - 30, init, F_BIG, (255, 255, 255))
            text_center(d, (x0 + x1) / 2, y0 + th / 2 + 8, "Camera off", F_SMALL, (209, 213, 219))
            # red mic-off dot
            d.ellipse([x1 - 34, y0 + 10, x1 - 14, y0 + 30], fill=(239, 68, 68))
        else:
            base = hexcol(TILE_BG[idx])
            # desaturate toward gray with fatigue
            gray = sum(base) // 3
            bg = lerp_col(base, (226, 232, 240), f * 0.55)
            border = (22, 163, 74) if IS_TEACHER[idx] else (231, 229, 228)
            bw = 3 if IS_TEACHER[idx] else 2
            d.rounded_rectangle([x0, y0, x1, y1], radius=14, fill=bg, outline=border, width=bw)
            cx = (x0 + x1) / 2
            cy = y0 + th / 2 - 6
            # per-student variation: teacher slightly less tired (empathy: teacher holds on)
            fi = f * (0.75 if IS_TEACHER[idx] else 1.0)
            # small deterministic variation
            fi = max(0.0, min(1.0, fi + 0.06 * math.sin(seed_phase(idx) + t * 6.28)))
            draw_face(d, cx, cy, 27, hexcol(SKIN[idx]), hexcol(HAIR[idx]), fi, idx)
            # name + mic
            label = NAMES[idx] + (" · host" if IS_TEACHER[idx] else "")
            text_center(d, cx, y1 - 26, label, F_TILE, (31, 41, 55))
            # mic dot green
            d.ellipse([x0 + 12, y0 + 10, x0 + 28, y0 + 26], fill=(34, 197, 94))
            # ZZZ when tired
            if fi > 0.55 and not cam_off:
                ph = (i * 0.9 + idx * 23) % 46
                zx = cx + 44
                zy = cy - 20 - ph * 0.7
                alpha = 1 - ph / 46
                col = (lerp(200, 100, alpha), lerp(200, 100, alpha), lerp(200, 120, alpha))
                s = "z" if (idx + i) % 2 == 0 else "Z"
                d.text((zx, zy), s, font=F_ZZZ, fill=col)
        # fatigue vignette overlay per tile (subtle)
        if f > 0.05 and not cam_off:
            # draw translucent gray border to suggest drain - simulate with darker outline
            pass

    # full-screen drain tint grows with f (very subtle, keep contrast)
    # banner
    bann_y0, bann_y1 = 610, 690
    title, sub, bg_hex, fg_hex = phase_info(t)
    bg = hexcol(bg_hex)
    fg = hexcol(fg_hex)
    d.rounded_rectangle([mx, bann_y0, W - mx, bann_y1], radius=14, fill=bg, outline=(231, 229, 228), width=2)
    # left accent dot pulses during fix
    if 0.78 <= t < 0.92:
        pulse = 0.6 + 0.4 * math.sin(i * 0.35)
        r = int(8 + 3 * pulse)
        d.ellipse([mx + 22 - r, (bann_y0 + bann_y1) / 2 - r, mx + 22 + r, (bann_y0 + bann_y1) / 2 + r], fill=(22, 163, 74))
        tx = mx + 44
    else:
        tx = mx + 22
    d.text((tx, bann_y0 + 10), title, font=F_BANNER, fill=fg)
    d.text((tx, bann_y0 + 44), sub, font=F_SUB, fill=fg)
    # progress bar (loop)
    d.rectangle([0, H - 6, W, H], fill=(231, 229, 228))
    d.rectangle([0, H - 6, W * (i + 1) / N, H], fill=(15, 98, 254))
    return np.asarray(img)

def seed_phase(idx):
    return idx * 1.7

def main():
    import imageio.v2 as iio
    mp4_path = os.path.join(BASE, "zoom-fatigue-classroom.mp4")
    webm_path = os.path.join(BASE, "zoom-fatigue-classroom.webm")
    gif_path = os.path.join(BASE, "zoom-fatigue-classroom.gif")
    print(f"Rendering {N} frames {W}x{H} @ {FPS}fps...")
    frames = []
    for i in range(N):
        frames.append(render_frame(i))
        if (i + 1) % 48 == 0:
            print(f"  {i+1}/{N}")
    frames_np = frames  # list of HxWx3 uint8
    print("Writing mp4...")
    w = iio.get_writer(mp4_path, fps=FPS, codec="libx264", quality=8,
                       ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "faststart"])
    for fr in frames_np:
        w.append_data(fr)
    w.close()
    print("Writing webm...")
    w2 = iio.get_writer(webm_path, fps=FPS, codec="libvpx-vp9", quality=8,
                        ffmpeg_params=["-pix_fmt", "yuv420p", "-b:v", "1M"])
    for fr in frames_np:
        w2.append_data(fr)
    w2.close()
    print("Writing gif (640x360, 12fps)...")
    small = [Image.fromarray(fr[::2]).resize((640, 360), Image.BILINEAR) for fr in frames_np[::2]]
    small[0].save(gif_path, save_all=True, append_images=small[1:], duration=83, loop=0, optimize=True)
    for p in (mp4_path, webm_path, gif_path):
        print(f"Saved: {p} ({os.path.getsize(p)//1024} KB)")
    write_html_preview(mp4_path, webm_path, gif_path)

def write_html_preview(mp4_path, webm_path, gif_path):
    import shutil
    os.makedirs(DOCS, exist_ok=True)
    for p in (mp4_path, webm_path, gif_path):
        try:
            shutil.copy(p, os.path.join(DOCS, os.path.basename(p)))
        except Exception as e:
            print("copy warn:", e)
    html = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Zoom Fatigue classroom looping animation: why long video classes drain students and teachers, plus 20-20-20 fixes.">
<title>Zoom Fatigue — Classroom Loop</title>
<style>
body{background:#f7f7f5;color:#1a1a1a;font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0}
.wrap{max-width:980px;margin:0 auto;padding:24px 16px 64px}
.card{background:#fff;border:1px solid #e7e5e4;border-radius:12px;padding:16px;margin:12px 0}
.tldr{background:#fff;border:1px solid #e7e5e4;border-left:4px solid #1a1a1a;border-radius:12px;padding:16px;margin:16px 0}
video,img{width:100%;height:auto;border-radius:12px;border:1px solid #e7e5e4;background:#000}
.grid{display:grid;grid-template-columns:1fr;gap:12px}
@media(min-width:720px){.grid{grid-template-columns:1fr 1fr 1fr}}
a{color:#0f62fe}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>
</head>
<body>
<header class="wrap" style="padding-bottom:0"><nav><a href="index.html">&larr; Brief index</a></nav>
<h1>Zoom Fatigue — Classroom Edition (8s loop)</h1>
<p>For students &amp; teachers: fresh → drained → recover. Play in class, then try the fix together.</p>
</header>
<main class="wrap" style="padding-top:0">
<div class="tldr"><b>TL;DR</b> — Staring + seeing yourself + no movement = tired eyes &amp; foggy brain. Fix: 20-20-20, stretch, water, camera breaks.</div>
<div class="card">
<video controls loop muted playsinline autoplay poster="" preload="metadata">
<source src="zoom-fatigue-classroom.webm" type="video/webm">
<source src="zoom-fatigue-classroom.mp4" type="video/mp4">
Sorry, your browser cannot play video. See the GIF below.
</video>
<p><a href="zoom-fatigue-classroom.mp4" download>Download MP4</a> · <a href="zoom-fatigue-classroom.webm" download>WebM</a> · <a href="zoom-fatigue-classroom.gif" download>GIF</a></p>
</div>
<div class="card"><h2>GIF fallback (no video needed)</h2><img src="zoom-fatigue-classroom.gif" alt="Looping cartoon of 9-student Zoom grid getting tired then recovering after a break"></div>
<div class="grid">
<div class="card"><h2>👁 Eyes</h2><p>Blink less on screen. Every 20 min, look 20 ft away for 20 sec.</p></div>
<div class="card"><h2>🧍 Body</h2><p>Stand, roll shoulders, unclench jaw. Still images hide fidget needs.</p></div>
<div class="card"><h2>📷 Mind</h2><p>Hide self-view, allow cameras-off breaks. Quiet class ≠ lazy class.</p></div>
</div>
<details class="card"><summary><b>Transcript (for screen readers / reduced motion)</b></summary>
<p>0–2s: 9-tile class grid, 9:00 AM, energy 100%, faces bright. 2–5s: clock advances toward 3 PM, eyelids droop, bags appear, battery drops to ~25%, three tiles switch to “Camera off”. 5–7s: green banner “Fix: 20-20-20 · stretch · water” — faces lift, cameras return. 7–8s: loop back to fresh. Reduced-motion: this text replaces the motion.</p>
</details>
<footer class="card"><p>Built offline with Pillow + imageio-ffmpeg. Free to reuse in class. Tip for teachers: pause at Hour 5 and ask “what do you feel?”</p></footer>
</main>
</body>
</html>"""
    out = os.path.join(DOCS, "zoom-fatigue.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print("Saved:", out)

if __name__ == "__main__":
    main()
