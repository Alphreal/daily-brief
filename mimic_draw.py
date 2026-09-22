"""mimic_draw.py - PIL draw primitives + cards + karaoke for mimic_retainpdf.py."""

from PIL import Image, ImageDraw

import tiktok_github_v2 as V

W, H, FPS = 720, 1280, 24

PANEL = (17, 28, 48)

GREEN = (34, 197, 94)

CYAN = (56, 189, 248)

YELLOW = (250, 204, 21)

WHITE = (255, 255, 255)

MUTED = (150, 156, 163)


def x_mark(d, x, y, s, color, w=5):
    d.line([x, y, x + s, y + s], fill=color, width=w, joint="curve")
    d.line([x + s, y, x, y + s], fill=color, width=w, joint="curve")


def check_mark(d, x, y, s, color, w=5):
    d.line([x, y + s * 0.55, x + s * 0.4, y + s * 0.9], fill=color, width=w, joint="curve")
    d.line([x + s * 0.4, y + s * 0.9, x + s, y + s * 0.1], fill=color, width=w, joint="curve")


F_BVN = r"C:\Users\ADMIN\Projects\Default Project\assets\fonts\BeVietnamPro-ExtraBold.ttf"

F_BVNB = r"C:\Users\ADMIN\Projects\Default Project\assets\fonts\BeVietnamPro-Bold.ttf"

F_BVNR = r"C:\Users\ADMIN\Projects\Default Project\assets\fonts\BeVietnamPro-Regular.ttf"

F_HEAD = V.font(F_BVN, 44)

F_TXT = V.font(F_BVNB, 27)

F_CAP = V.font(F_BVNB, 30)

F_SMALL = V.font(F_BVNR, 23)

F_PILL = V.font(F_BVN, 21)

F_BADGE = V.font(F_BVNR, 20)

F_TILE = V.font(F_BVNR, 18)

F_GHEAD = V.font(F_BVNB, 22)

F_EYE = V.font(F_BVNB, 22)


def draw_icon(d, cx, cy, s, kind, color, w=0):
    """Stroke icon centered at (cx,cy), size s. Hand-drawn PIL primitives."""
    w = w or max(3, s // 10)
    h = s / 2
    if kind == "doc":
        x0, y0, x1, y1 = cx - s * 0.32, cy - s * 0.42, cx + s * 0.32, cy + s * 0.42
        d.rectangle([x0, y0, x1, y1], outline=color, width=w)
        d.line([x1 - s * 0.24, y0, x1, y0 + s * 0.24], fill=color, width=w)
        for i in range(3):
            yy = y0 + s * 0.34 + i * s * 0.17
            d.line([x0 + s * 0.14, yy, x1 - s * 0.14, yy], fill=color, width=max(2, w - 1))
    elif kind == "globe":
        d.ellipse([cx - h, cy - h, cx + h, cy + h], outline=color, width=w)
        d.ellipse(
            [cx - h * 0.45, cy - h, cx + h * 0.45, cy + h], outline=color, width=max(2, w - 1)
        )
        d.line([cx - h, cy, cx + h, cy], fill=color, width=max(2, w - 1))
    elif kind == "download":
        d.line([cx, cy - h, cx, cy + h * 0.5], fill=color, width=w)
        d.line([cx, cy + h * 0.5, cx - h * 0.5, cy], fill=color, width=w)
        d.line([cx, cy + h * 0.5, cx + h * 0.5, cy], fill=color, width=w)
        d.line([cx - h * 0.8, cy + h, cx + h * 0.8, cy + h], fill=color, width=w)
    elif kind == "lock":
        d.rounded_rectangle(
            [cx - h * 0.6, cy - h * 0.1, cx + h * 0.6, cy + h * 0.8],
            radius=8,
            outline=color,
            width=w,
        )
        d.arc(
            [cx - h * 0.4, cy - h * 0.8, cx + h * 0.4, cy + h * 0.1], 180, 360, fill=color, width=w
        )
    elif kind == "users":
        d.ellipse(
            [cx - h * 0.75, cy - h * 0.9, cx - h * 0.15, cy - h * 0.3], outline=color, width=w
        )
        d.arc(
            [cx - h * 0.95, cy - h * 0.2, cx + h * 0.05, cy + h * 0.9],
            200,
            340,
            fill=color,
            width=w,
        )
        d.ellipse(
            [cx + h * 0.15, cy - h * 0.9, cx + h * 0.75, cy - h * 0.3],
            outline=color,
            width=max(2, w - 1),
        )
    elif kind == "box":
        pts = [
            (cx, cy - h),
            (cx + h * 0.9, cy - h * 0.45),
            (cx + h * 0.9, cy + h * 0.45),
            (cx, cy + h),
            (cx - h * 0.9, cy + h * 0.45),
            (cx - h * 0.9, cy - h * 0.45),
        ]
        d.polygon(pts, outline=color, width=w)
        d.line(
            [cx - h * 0.9, cy - h * 0.45, cx, cy, cx + h * 0.9, cy - h * 0.45],
            fill=color,
            width=max(2, w - 1),
        )
        d.line([cx, cy, cx, cy + h], fill=color, width=max(2, w - 1))
    elif kind == "zap":
        d.polygon(
            [
                (cx + h * 0.25, cy - h),
                (cx - h * 0.45, cy + h * 0.15),
                (cx - h * 0.02, cy + h * 0.15),
                (cx - h * 0.25, cy + h),
                (cx + h * 0.45, cy - h * 0.15),
                (cx + h * 0.02, cy - h * 0.15),
            ],
            outline=color,
            width=w,
            fill=None,
        )
    elif kind == "sparkles":
        r1, r2 = h, h * 0.32
        pts = []
        for k in range(8):
            r = r1 if k % 2 == 0 else r2
            a = k * 3.14159 / 4 - 3.14159 / 2
            pts.append(
                (
                    cx + r * 0.9 * (1 if k % 2 == 0 else 1) * __import__("math").cos(a),
                    cy + r * (1 if k % 2 == 0 else 1) * __import__("math").sin(a),
                )
            )
        d.polygon(pts, outline=color, width=w)
        d.line(
            [cx + h * 0.7, cy + h * 0.5, cx + h * 0.9, cy + h * 0.5],
            fill=color,
            width=max(2, w - 1),
        )
        d.line(
            [cx + h * 0.8, cy + h * 0.4, cx + h * 0.8, cy + h * 0.6],
            fill=color,
            width=max(2, w - 1),
        )
    elif kind == "chat":
        d.rounded_rectangle(
            [cx - h * 0.85, cy - h * 0.6, cx + h * 0.85, cy + h * 0.4],
            radius=12,
            outline=color,
            width=w,
        )
        d.polygon(
            [(cx - h * 0.4, cy + h * 0.4), (cx - h * 0.4, cy + h * 0.85), (cx, cy + h * 0.4)],
            outline=color,
            width=w,
        )
        d.line(
            [cx - h * 0.55, cy - h * 0.1, cx + h * 0.55, cy - h * 0.1],
            fill=color,
            width=max(2, w - 1),
        )
    elif kind == "monitor":
        d.rounded_rectangle(
            [cx - h * 0.85, cy - h * 0.7, cx + h * 0.85, cy + h * 0.3],
            radius=8,
            outline=color,
            width=w,
        )
        d.line([cx, cy + h * 0.3, cx, cy + h * 0.7], fill=color, width=w)
        d.line([cx - h * 0.5, cy + h * 0.7, cx + h * 0.5, cy + h * 0.7], fill=color, width=w)
    elif kind == "search":
        d.ellipse([cx - h * 0.6, cy - h * 0.8, cx + h * 0.2, cy], outline=color, width=w)
        d.line([cx + h * 0.1, cy - h * 0.1, cx + h * 0.7, cy + h * 0.5], fill=color, width=w)
    elif kind == "layers":
        for k in range(3):
            yy = cy - h * 0.5 + k * h * 0.42
            d.polygon(
                [(cx - h * 0.8, yy), (cx, yy - h * 0.3), (cx + h * 0.8, yy), (cx, yy + h * 0.3)],
                outline=color,
                width=max(2, w - 1),
            )
    else:  # check fallback
        check_mark(d, cx - h * 0.4, cy - h * 0.4, h * 0.8, color, w)


def gradient_text(d, cx, y, text, fnt, c_top, c_bot):
    bb = d.textbbox((0, 0), text, font=fnt)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    mask = Image.new("L", (tw + 20, th + 20), 0)
    md = ImageDraw.Draw(mask)
    md.text((10 - bb[0], 10 - bb[1]), text, font=fnt, fill=255)
    grad = Image.new("RGB", mask.size)
    px = grad.load()
    for yy in range(grad.size[1]):
        p = yy / grad.size[1]
        cc = tuple(int(c_top[i] + (c_bot[i] - c_top[i]) * p) for i in range(3))
        for xx in range(grad.size[0]):
            px[xx, yy] = cc
    d._image.paste(grad, (int(cx - tw / 2 - 10), y), mask)
    return tw


def tile(d, x, y, tw, th, kind, label, tint, isz=44):
    d.rounded_rectangle(
        [x, y, x + tw, y + th], radius=16, fill=(255, 255, 255, 14), outline=tint, width=2
    )
    draw_icon(d, x + tw / 2, y + th / 2 - 14, isz, kind, (255, 255, 255))
    lw = d.textlength(label, font=F_TILE)
    d.text((x + (tw - lw) / 2, y + th - 34), label, font=F_TILE, fill=(226, 232, 240))


def group_panel(d, x, y, w, h, header, hcolor, accent):
    d.rounded_rectangle(
        [x, y, x + w, y + h], radius=22, fill=(255, 255, 255, 10), outline=accent, width=2
    )
    d.line([x + 24, y + 2, x + w - 24, y + 2], fill=(255, 255, 255, 60), width=2)
    hw = d.textlength(header, font=F_GHEAD)
    d.text((x + (w - hw) / 2, y + 16), header, font=F_GHEAD, fill=hcolor)
    return y + 58


def particles(d, t, seed=7):
    import random

    rnd = random.Random(seed)
    for i in range(38):
        bx = rnd.uniform(20, W - 20)
        by = rnd.uniform(60, H - 60)
        sp = rnd.uniform(0.2, 0.7)
        ph = rnd.uniform(0, 6.28)
        yy = by + 14 * __import__("math").sin(6.28 * sp * t + ph)
        a = int(30 + 40 * abs(__import__("math").sin(6.28 * sp * t * 0.6 + ph)))
        r = 2 + (i % 3)
        tint = [(56, 189, 248), (244, 114, 182), (167, 139, 250)][i % 3]
        d.ellipse([bx - r, yy - r, bx + r, yy + r], fill=tint + (a,))


def pill(d, x, y, text, fnt, fg, bg):
    w = d.textlength(text, font=fnt) + 28
    d.rounded_rectangle([x, y, x + w, y + 36], radius=18, fill=bg)
    d.text((x + 14, y + 5), text, font=fnt, fill=fg)
    return w


def topbar(d, scene, idx):
    y = 84
    tag, cnt = scene["tag"], f"0{idx + 1}/05"
    cntw = d.textlength(cnt, font=F_PILL) + 20
    tagw = d.textlength(tag, font=F_PILL) + 28
    pill(d, W - 40 - tagw - 12 - cntw, y, tag, F_PILL, WHITE, (127, 29, 29))
    gradient_text(
        d, W - 40 - cntw + 10 + (cntw - 20) / 2, y + 5, cnt, F_PILL, (125, 211, 252), (59, 130, 246)
    )
    x = 40
    x += pill(d, x, y, "RETAINPDF", F_PILL, WHITE, GREEN) + 12
    avail = W - 40 - tagw - 12 - cntw - 12 - x
    _sz = 21
    _tmp = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    _th = scene["theme"]
    while _sz > 8 and _tmp.textlength(_th, font=V.font(F_BVNB, _sz)) > avail:
        _sz -= 1
    while _th and _tmp.textlength(_th, font=V.font(F_BVNB, _sz)) > avail:
        _th = _th[:-1]
    if _th != scene["theme"]:
        _th = _th[:-1] + "…"
    d.text((x, y + 5), _th, font=V.font(F_BVNB, _sz), fill=CYAN)


def headline(d, lines, grad=None):
    y = 170
    fonts = [V.fit_font(F_BVN, ln, W - 110, 44) for ln in lines]
    heights = [f.size + 12 for f in fonts]
    h = 44 + sum(heights)
    d.rounded_rectangle(
        [36, y, W - 36, y + h], radius=18, fill=(46, 16, 20), outline=(127, 29, 29), width=2
    )
    yy = y + 22
    for li, (ln, fnt) in enumerate(zip(lines, fonts, strict=True)):
        if grad and li in grad:
            gradient_text(d, W / 2, yy, ln, fnt, grad[li][0], grad[li][1])
        else:
            V.center(d, W / 2, yy, ln, fnt, WHITE)
        yy += fnt.size + 12
    return y + h


def card_bad(d, y, title, items):
    h = 78 + len(items) * 40
    d.rounded_rectangle(
        [36, y, W - 36, y + h], radius=16, fill=(48, 18, 22), outline=(153, 27, 27), width=2
    )
    x_mark(d, 60, y + 20, 22, (252, 165, 165))
    d.text((94, y + 14), title, font=F_TXT, fill=(252, 165, 165))
    yy = y + 58
    for it in items:
        d.text((66, yy), "•  " + it, font=F_SMALL, fill=(253, 164, 175))
        yy += 40
    return y + h


def card_good(d, y, title, items):
    h = 78 + len(items) * 40
    d.rounded_rectangle(
        [36, y, W - 36, y + h], radius=16, fill=(14, 46, 30), outline=(21, 128, 61), width=2
    )
    check_mark(d, 58, y + 18, 24, (110, 231, 183))
    d.text((94, y + 14), title, font=F_TXT, fill=(110, 231, 183))
    yy = y + 58
    for it in items:
        check_mark(d, 64, yy + 6, 20, (110, 231, 183), 4)
        d.text((94, yy), it, font=F_SMALL, fill=(167, 243, 208))
        yy += 40
    return y + h


def card_mock(d, y, title, tag, items):
    h = 120 + len(items) * 44
    d.rounded_rectangle(
        [36, y, W - 36, y + h], radius=16, fill=PANEL, outline=(51, 65, 85), width=2
    )
    for cx in (58, 76, 94):
        d.ellipse([cx, y + 14, cx + 12, y + 26], fill=(100, 116, 139))
    tw = d.textlength(tag, font=F_BADGE) + 20
    tfnt = V.fit_font(V.F_BODY, title, W - 260 - tw, 20)
    d.text((120, y + 12), title, font=tfnt, fill=MUTED)
    tw = d.textlength(tag, font=F_BADGE) + 20
    d.rounded_rectangle(
        [W - 36 - tw - 14, y + 10, W - 36 - 14, y + 38], radius=14, fill=(14, 46, 30)
    )
    d.text((W - 36 - tw - 14 + 10, y + 14), tag, font=F_BADGE, fill=GREEN)
    yy = y + 52
    for it in items:
        d.rounded_rectangle([56, yy, W - 56, yy + 36], radius=10, fill=(255, 255, 255))
        d.text((72, yy + 6), it, font=F_BADGE, fill=(30, 41, 59))
        yy += 44
    return y + h


def card_info(d, y, title, tag, items):
    h = 110 + len(items) * 40
    d.rounded_rectangle(
        [36, y, W - 36, y + h], radius=16, fill=(23, 37, 84), outline=(59, 130, 246), width=2
    )
    d.text((60, y + 14), title, font=F_TXT, fill=(191, 219, 254))
    d.text((60, y + 52), tag, font=F_EYE, fill=CYAN)
    yy = y + 88
    for it in items:
        d.text((66, yy), "•  " + it, font=F_SMALL, fill=(219, 234, 254))
        yy += 40
    return y + h


def badges_row(d, y, badges):
    x = 36
    for b in badges:
        d.rounded_rectangle(
            [x, y, x + d.textlength(b, font=F_BADGE) + 36, y + 44], radius=22, outline=CYAN, width=2
        )
        d.text((x + 18, y + 9), b, font=F_BADGE, fill=CYAN)
        x += d.textlength(b, font=F_BADGE) + 52


F_CAPBIG = V.font(F_BVNB, 35)


def karaoke(d, timed, t):
    lines = V.wrap(d, " ".join(w for w, _, _ in timed), F_CAP, W - 140)
    lh, gap = 46, 6
    h = len(lines) * (lh + gap) + 28
    y0 = 1006
    d.rounded_rectangle([30, y0, W - 30, y0 + h], radius=18, fill=(0, 0, 0, 190))
    # per-word color by measured time
    pos = {}
    for i, (_w, s, e) in enumerate(timed):
        if t >= e:
            pos[i] = (134, 239, 172)  # spoken: green
        elif t >= s:
            pos[i] = YELLOW  # current word
        else:
            pos[i] = WHITE
    # rebuild lines with word indices; active word pops bigger
    idx, yy = 0, y0 + 16
    for ln in lines:
        words = ln.split()
        advs = []
        for j in range(len(words)):
            cur = pos[idx + j] == YELLOW
            advs.append(
                max(
                    d.textlength(words[j] + " ", font=F_CAP),
                    d.textlength(words[j] + " ", font=F_CAPBIG) if cur else 0,
                )
            )
        x = 60
        for j in range(len(words)):
            w = timed[idx + j][0]
            if pos[idx + j] == YELLOW:
                bw = d.textlength(w, font=F_CAPBIG)
                d.text((x + (advs[j] - bw) / 2 - 4, yy - 4), w, font=F_CAPBIG, fill=YELLOW)
            else:
                d.text((x, yy), w, font=F_CAP, fill=pos[idx + j])
            x += advs[j]
        idx += len(words)
        yy += lh + gap
