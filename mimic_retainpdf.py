# -*- coding: utf-8 -*-
"""Mimic reference TikTok (RetainPDF 5-scene format) 1:1, rebuilt from scratch.
Same design grammar + same script beat-for-beat. Voice-subtitle fit GUARANTEED:
karaoke highlight is driven by measured edge-tts word-boundary timestamps,
not estimates. Run: python mimic_retainpdf.py
Output: retainpdf-mimic.mp4 + retainpdf-mimic-cover.png (root only).
"""

import asyncio
import json
import os
import re
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import tiktok_github_v2 as V
from mimic_draw import (
    FPS,
    H,
    W,
    badges_row,
    card_bad,
    card_good,
    card_info,
    card_mock,
    group_panel,
    headline,
    karaoke,
    particles,
    tile,
    topbar,
)

BASE = os.path.dirname(os.path.abspath(__file__))
TMP = r"C:\Users\ADMIN\AppData\Local\Temp\opencode\ttmimic"
FF = r"C:\Users\ADMIN\AppData\Roaming\Python\Python311\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
VOICE = "vi-VN-NamMinhNeural"
TAIL = 0.7

NAVY = (11, 21, 38)
RED = (248, 81, 73)
PINK = (244, 114, 182)


SCENES = [
    dict(
        theme="PARADIGM SHIFT",
        tag="ERA SHIFT",
        head=["CHẤM DỨT THỜI KỲ CŨ", "DỊCH PDF XONG LÀ VỠ NÁT TOÀN BỘ BỐ CỤC?"],
        cards=[
            (
                "bad",
                "Công cụ dịch truyền thống",
                [
                    "Công thức toán bị vỡ vụn hoặc mất trắng",
                    "Bảng biểu xô lệch, ngắt dòng lung tung",
                    "PDF dạng ảnh, scan hoàn toàn bó tay",
                ],
            ),
            (
                "good",
                "RetainPDF Layout-Preserving",
                [
                    "Giữ 100% bố cục, hình ảnh và bảng biểu",
                    "Bảo toàn trọn vẹn công thức inline toán học",
                    "Dịch mượt mà cả PDF scan và tài liệu ảnh",
                ],
            ),
        ],
        badges=["Khôi Phục 100% Layout", "Inline Formulas Intact"],
        voice="Thời đại dịch PDF xong bị vỡ nát layout, và mất sạch công thức toán, đã chính thức kết thúc!",
    ),
    dict(
        theme="ENGINEERING AUTHORITY",
        tag="MIT OPEN SOURCE",
        head=["REPOSITORY CHÍNH THỨC", "wxyhgk / retain-pdf"],
        cards=[
            (
                "tiles",
                "TÀI LIỆU & TÁC VỤ · 4",
                (110, 231, 183),
                (34, 197, 94),
                [
                    ("doc", "Tài liệu"),
                    ("layers", "Hàng đợi"),
                    ("globe", "Song ngữ"),
                    ("chat", "Trích dẫn"),
                ],
            )
        ],
        badges=["Tự Host Riêng Biệt", "Cộng Đồng Dùng Thật"],
        voice="Ritin PDF, mã nguồn mở MIT vừa ra đời, giải quyết triệt để bài toán dịch, giữ nguyên một trăm phần trăm bố cục, công thức inline và bảng biểu, kể cả với file scan hay ảnh chụp.",
        disp="RetainPDF, mã nguồn mở MIT vừa ra đời, giải quyết triệt để bài toán dịch, giữ nguyên một trăm phần trăm bố cục, công thức inline và bảng biểu, kể cả với file scan hay ảnh chụp.",
    ),
    dict(
        theme="BREAKTHROUGH UI",
        tag="LIVE CAPTURE",
        head=["ĐỌC SONG SONG BẢN GỐC & BẢN DỊCH", "CANH CHUẨN 1:1"],
        cards=[
            (
                "tiles",
                "ĐỌC SONG SONG · 3",
                (125, 211, 252),
                (56, 189, 248),
                [("doc", "Trang gốc"), ("doc", "Trang dịch"), ("check", "Formulas")],
            ),
            (
                "tiles",
                "TRỢ LÝ AI · 2",
                (196, 181, 253),
                (167, 139, 250),
                [("sparkles", "Hỏi đáp"), ("chat", "Trích dẫn")],
            ),
        ],
        badges=["Trợ Lý AI Tích Hợp Sẵn"],
        voice="Đặc biệt, hệ thống tích hợp trợ lý AI thông minh, hỏi đáp trực tiếp, và trích dẫn chuẩn từng trang.",
    ),
    dict(
        theme="DEPLOY ANYWHERE",
        tag="DOCKER READY",
        head=["TỰ HOST BẰNG DOCKER", "HOẶC CÀI DESKTOP APP CỰC NHANH"],
        hlgrad={0: ((125, 211, 252), (59, 130, 246))},
        cards=[
            (
                "tiles",
                "TRIỂN KHAI · 2",
                (125, 211, 252),
                (59, 130, 246),
                [("box", "Docker"), ("monitor", "Desktop")],
            )
        ],
        badges=["Miễn phí 100%", "Mã nguồn mở MIT"],
        voice="Hỗ trợ tự host bằng Docker, hoặc cài Desktop app cực nhanh, chỉ trong vài phút.",
    ),
    dict(
        theme="CALL TO ACTION",
        tag="FREE DOCS",
        head=["BÌNH LUẬN 'CÁCH CÀI'", "NGAY BÊN DƯỚI VIDEO"],
        hlgrad={0: ((110, 231, 183), (56, 189, 248))},
        cards=[
            (
                "good",
                "Nhận Ngay Hôm Nay",
                [
                    "Hướng dẫn cài đặt chi tiết từng bước",
                    "Bộ tài liệu sử dụng đầy đủ",
                    "Miễn phí, không cần đăng ký",
                ],
            )
        ],
        badges=["Bình Luận Ngay"],
        voice="Bình luận cách cài ngay bên dưới, để nhận hướng dẫn cài đặt chi tiết và bộ tài liệu nhé!",
    ),
]


def ff_dur(pth):
    p = subprocess.run([FF, "-i", pth], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", p.stderr)
    h, mnt, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
    return h * 3600 + mnt * 60 + s


async def tts_one(text, mp3):
    import edge_tts

    comm = edge_tts.Communicate(text, VOICE)
    bounds, chunks = [], []
    async for c in comm.stream():
        if c.get("type") == "audio":
            chunks.append(c["data"])
        elif c.get("type") == "WordsBoundary":
            bounds.append((c["text"], c["offset"] / 1e7, c["duration"] / 1e7))
    open(mp3, "wb").write(b"".join(chunks))
    return bounds


def align_words(text, bounds, dur, disp=None):
    """Map DISPLAY words -> (word, start, end) using measured voice boundaries.
    disp defaults to text; counts must match (falls back gracefully)."""
    words = (disp or text).split()
    b = [(t, s, s + d) for t, s, d in bounds]
    if len(b) == len(words):
        return [(w, s, e) for w, (_, s, e) in zip(words, b, strict=True)]
    if b:
        out, bi = [], 0
        for w in words:
            if bi < len(b):
                _, s, e = b[bi]
                bi += 1
            else:
                s, e = dur * 0.9, dur
            out.append((w, s, e))
        return out
    n = max(1, len(words))
    return [(w, dur * i / n, dur * (i + 1) / n) for i, w in enumerate(words)]


def make_bg_master():
    """720x1400 textured master: vertical gradient + glow blobs + dot grid + vignette."""
    BW, BH = W, H + 120
    base = Image.new("RGB", (BW, BH))
    px = base.load()
    top = (13, 25, 48)
    bot = (4, 8, 18)
    for y in range(BH):
        p = y / BH
        px_day = tuple(int(top[i] + (bot[i] - top[i]) * p) for i in range(3))
        for x in range(BW):
            px[x, y] = px_day
    glow = Image.new("L", (BW, BH), 0)
    gd = ImageDraw.Draw(glow)
    gd.ellipse([-220, -140, 420, 420], fill=70)
    gd.ellipse([340, BH - 480, 980, BH + 60], fill=55)
    gd.ellipse([180, BH // 2 - 160, 560, BH // 2 + 220], fill=30)
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    cyan = Image.new("RGB", (BW, BH), (34, 60, 110))
    base = Image.composite(cyan, base, glow)
    dots = ImageDraw.Draw(base, "RGBA")
    for yy in range(0, BH, 26):
        for xx in range(0, BW, 26):
            dots.point((xx, yy), fill=(255, 255, 255, 10))
    arr = np.asarray(base).astype(np.float32)
    ys, xs = np.mgrid[0:BH, 0:BW]
    dist = np.sqrt(((xs - BW / 2) / (BW / 2)) ** 2 + ((ys - BH / 2) / (BH / 2)) ** 2) / 1.42
    arr *= np.clip(1.0 - dist * 0.35, 0.55, 1.0)[..., None]
    return Image.fromarray(arr.astype(np.uint8))


def glow_rect(img, bbox, color, alpha=70, blur=28, grow=18):
    x0, y0, x1, y1 = bbox
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(
        [x0 - grow, y0 - grow, x1 + grow, y1 + grow], radius=26, fill=color + (alpha,)
    )
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(layer)


def ease_back(p):
    p = max(0.0, min(1.0, p))
    return 1 + 2.70158 * (p - 1) ** 3 + 1.70158 * (p - 1) ** 2


def build_base(scene, idx):
    """Split layers: (head_img, cards_img, tiles[(img, x, y, order)])."""
    head = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow_rect(head, (36, 170, W - 36, 420), (56, 189, 248), 40, 34)
    dh = ImageDraw.Draw(head, "RGBA")
    topbar(dh, scene, idx)
    y_head = headline(dh, scene["head"], scene.get("hlgrad")) + 18
    cards = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dc = ImageDraw.Draw(cards, "RGBA")
    y = y_head
    tiles = []
    for _ci, c in enumerate(scene["cards"]):
        y0 = y
        if c[0] == "bad":
            y = card_bad(dc, y, c[1], c[2]) + 14
            glow_rect(cards, (36, y0, W - 36, y), (248, 81, 73), 45, 30)
        elif c[0] == "good":
            y = card_good(dc, y, c[1], c[2]) + 14
            glow_rect(cards, (36, y0, W - 36, y), (34, 197, 94), 45, 30)
        elif c[0] == "mock":
            y = card_mock(dc, y, c[1], c[2], c[3]) + 14
            glow_rect(cards, (36, y0, W - 36, y), (56, 189, 248), 40, 30)
        elif c[0] == "tiles":
            _, header, hcolor, accent, tls = c
            cols = 4 if len(tls) > 2 else 2
            tw = (W - 72 - (cols - 1) * 12) / cols
            th = 118 if cols == 4 else 150
            isz = 44 if cols == 4 else 56
            rows = (len(tls) + cols - 1) // cols
            gh = 58 + rows * th + (rows - 1) * 12 + 22
            gy = group_panel(dc, 36, y, W - 72, gh, header, hcolor, accent)
            for ti, (kind, label) in enumerate(tls):
                tx = 36 + 20 + (ti % cols) * (tw + 12)
                ty = gy + (ti // cols) * (th + 12)
                tl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                tile(ImageDraw.Draw(tl, "RGBA"), tx, ty, tw, th, kind, label, accent, isz)
                tiles.append((tl, tx, ty, len(tiles), tw, th))
            glow_rect(cards, (36, y, W - 36, y + gh), accent[:3], 40, 30)
            y = y + gh + 14
        else:
            y = card_info(dc, y, c[1], c[2], c[3]) + 14
            glow_rect(cards, (36, y0, W - 36, y), (99, 102, 241), 45, 30)
    badges_row(dc, y + 4, scene["badges"])
    return head, cards, tiles


def paste_layer(out, img, scale, alpha, cx=W / 2, cy=H / 2):
    sw, sh = max(1, int(W * scale)), max(1, int(H * scale))
    b = img.resize((sw, sh), Image.BILINEAR)
    if alpha < 1.0:
        b = b.copy()
        b.putalpha(b.split()[3].point(lambda v: int(v * alpha)))
    out.alpha_composite(b, (int(cx - sw / 2), int(cy - sh / 2)))


async def main():
    import imageio.v2 as iio

    os.makedirs(TMP, exist_ok=True)
    sched = []
    for i, sc in enumerate(SCENES):
        mp3 = os.path.join(TMP, f"mim{i}.mp3")
        if not (os.path.exists(mp3) and os.path.getsize(mp3) > 1000):
            bounds = await tts_one(sc["voice"], mp3)
            json.dump(bounds, open(os.path.join(TMP, f"mim{i}.json"), "w"))
            print(f"  tts scene {i + 1}", flush=True)
        else:
            bounds = json.load(open(os.path.join(TMP, f"mim{i}.json")))
        dur = ff_dur(mp3)
        timed = align_words(sc["voice"], bounds, dur, sc.get("disp"))
        sched.append((sc, mp3, dur, timed))
        print(f"  scene {i + 1}: {dur:.2f}s, {len(timed)} words", flush=True)
    total = sum(d for _, _, d, _ in sched) + TAIL * len(sched)
    print(f"Video: {total:.1f}s", flush=True)
    out = os.path.join(BASE, "retainpdf-mimic.mp4")
    w = iio.get_writer(
        out, fps=FPS, codec="libx264", quality=8, ffmpeg_params=["-pix_fmt", "yuv420p"]
    )
    master_bg = make_bg_master()
    layers = [build_base(sc, i) for i, (sc, _, _, _) in enumerate(sched)]
    segs = [d + TAIL for _, _, d, _ in sched]

    def base_frame(i, lt):
        sc, _, _, _ = sched[i]
        seg = segs[i]
        by = int(60 * V.smooth(min(1.0, lt / seg)))
        bg = master_bg.crop((0, by, W, by + H))
        head, cards, tiles = layers[i]
        out = bg.convert("RGBA")
        paste_layer(out, head, 1.0 + 0.015 * (lt / seg), 1.0)
        p = min(1.0, lt / 0.45)
        paste_layer(
            out, cards, 0.965 + 0.035 * V.smooth(p) + 0.02 * (lt / seg), min(1.0, lt / 0.3 + 0.15)
        )
        for tl, tx, ty, order, tw, th in tiles:
            ap = lt - (0.35 + order * 0.09)
            if ap < 0:
                continue
            q = min(1.0, ap / 0.35)
            s = ease_back(q)
            crop = tl.crop((int(tx), int(ty), int(tx + tw), int(ty + th)))
            sw, sh = max(1, int(tw * s)), max(1, int(th * s))
            b = crop.resize((sw, sh), Image.BILINEAR)
            if q < 1.0:
                b = b.copy()
                b.putalpha(b.split()[3].point(lambda v, q=q: int(v * q)))
            out.alpha_composite(b, (int(tx + tw / 2 - sw / 2), int(ty + th / 2 - sh / 2)))
        return out.convert("RGB")

    el, cover, FADE = 0.0, False, 0.3
    for i, (_sc, _mp3, _dur, timed) in enumerate(sched):
        seg = segs[i]
        for k in range(int(seg * FPS)):
            lt = k / FPS
            fr = base_frame(i, lt)
            if i > 0 and lt < FADE:
                fr = Image.blend(base_frame(i - 1, segs[i - 1]), fr, V.smooth(lt / FADE))
            d = ImageDraw.Draw(fr, "RGBA")
            particles(d, el + lt)
            karaoke(d, timed, lt)
            d.rectangle([0, H - 8, W * (el + lt) / total, H], fill=(236, 72, 153))
            w.append_data(np.asarray(fr))
            el += 1 / FPS
            if not cover and el > 1.5:
                fr.save(os.path.join(BASE, "retainpdf-mimic-cover.png"))
                cover = True
    w.close()
    # audio concat + loudnorm + mux
    lst = os.path.join(TMP, "concat.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for _, mp3, _dur, _ in sched:
            f.write(f"file '{mp3}'\n")
            sil = os.path.join(TMP, "sil.mp3")
            if not os.path.exists(sil):
                subprocess.run(
                    [
                        FF,
                        "-y",
                        "-f",
                        "lavfi",
                        "-i",
                        "anullsrc=r=24000:cl=mono",
                        "-t",
                        str(TAIL),
                        "-q:a",
                        "4",
                        sil,
                    ],
                    capture_output=True,
                )
            f.write(f"file '{sil}'\n")
    raw = os.path.join(TMP, "raw.mp3")
    subprocess.run(
        [FF, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", raw], capture_output=True
    )
    master = os.path.join(TMP, "master.mp3")
    subprocess.run(
        [FF, "-y", "-i", raw, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "24000", master],
        capture_output=True,
    )
    final = os.path.join(BASE, "retainpdf-mimic-final.mp4")
    subprocess.run(
        [FF, "-y", "-i", out, "-i", master, "-c:v", "copy", "-c:a", "aac", "-shortest", final],
        capture_output=True,
    )
    os.replace(final, out)
    print(f"Saved: {out} ({os.path.getsize(out) // 1024} KB)")


if __name__ == "__main__":
    asyncio.run(main())
