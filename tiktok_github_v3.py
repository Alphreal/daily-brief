# -*- coding: utf-8 -*-
"""V3: v2 visuals + real VN narration + synced karaoke + muxed audio.
Slices: narration.json (narrate.py) -> frames -> mux. Run: python tiktok_github_v3.py
"""

import json
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw

import tiktok_github_v2 as V

BASE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(BASE, "docs")
TMP = r"C:\Users\ADMIN\AppData\Local\Temp\opencode\ttv3"
FF = r"C:\Users\ADMIN\AppData\Roaming\Python\Python311\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
W, H, FPS = V.W, V.H, V.FPS
CARD_DUR = 2.0
TAIL = 0.7
TOTAL_CH = 12


def load_sched():
    nar = json.load(open(os.path.join(TMP, "narration.json"), encoding="utf-8"))
    items, art = V.load_items()
    by_rank = {it["rank"]: it for it in items}
    segs = []  # (kind, payload, dur, chapter)
    hook = [row for row in nar if row["key"] == "hook"][0]
    segs.append(("hook", hook, hook["dur"] + 1.5, 1))
    for i in range(1, 11):
        it = by_rank[i]
        ln = [row for row in nar if row["key"] == f"repo{i}"][0]
        roll = max(3.2, ln["dur"] + TAIL)
        segs.append(("card", it, CARD_DUR, i + 1))
        segs.append(("roll", (it, ln, roll), roll, i + 1))
    cta = [row for row in nar if row["key"] == "cta"][0]
    segs.append(("cta", (cta, cta["dur"] + 1.5), cta["dur"] + 1.5, TOTAL_CH))
    return segs, art, items


def cap_words(it, text, gain_kw):
    words = []
    for w_ in text.split():
        c = (
            V.RED
            if (
                gain_kw in w_
                or w_ in ("Quán", "quân", "mạnh", "mẽ", "top", "mắt", "chú", "chốt", "Lưu", "lại")
            )
            else V.WHITE
        )
        words.append((w_, c))
    return words


def draw_roll_v3(wide, it, ln, ch, elapsed, dur):
    # B-roll: full banner fit-top with slow horizontal pan (no dead crops)
    p = max(0.0, min(1.0, elapsed / dur if dur else 1.0))
    out = V.GLOW.copy()
    bw, bh = wide.size
    x0 = int((bw - W) * V.smooth(p)) if bw > W else 0
    strip = wide.crop((x0, 0, x0 + min(bw, W), bh))
    if strip.width < W:
        strip = strip.resize((W, bh), Image.BILINEAR)
    out.paste(strip, (0, 210))
    d = ImageDraw.Draw(out, "RGBA")
    d.rectangle([0, 0, W, 7], fill=(V.RED[0], V.RED[1], V.RED[2], 255))
    d.text((36, 30), f"{ch:02d} / {TOTAL_CH:02d}", font=V.F_SMALL, fill=V.MUTED)
    chip = it["repo"][:34]
    cw = d.textlength(chip, font=V.F_SMALL) + 40
    d.rounded_rectangle([(W - cw) / 2, 120, (W + cw) / 2, 168], radius=24, fill=(0, 0, 0, 160))
    V.center(d, W / 2, 128, chip, V.F_SMALL, V.WHITE)
    gain_kw = f"{it['gain']:,}".replace(",", ".")
    words = cap_words(it, ln["text"], gain_kw)
    V.draw_karaoke(
        d,
        [words],
        V.F_CAP,
        W / 2,
        950,
        min(0.99, (elapsed / ln["dur"]) / 2.4) if ln["dur"] else 0.99,
    )
    return out


def main():
    import shutil

    import imageio.v2 as iio

    V.GLOW = V.make_glow()
    segs, art, items = load_sched()
    rolls = {}
    for it in items:
        pth = art.get(it["repo"])
        if pth:
            try:
                b = Image.open(pth).convert("RGB")
                s = 420 / b.height
                rolls[it["repo"]] = b.resize((max(W + 1, int(b.width * s)), 420), Image.BILINEAR)
            except Exception:
                pass
    total_dur = sum(s[2] for s in segs)
    N = int(total_dur * FPS)
    print(f"Video: {round(total_dur, 1)}s, {N} frames")
    silent = os.path.join(BASE, "tiktok-github-v3-silent.mp4")
    w = iio.get_writer(
        silent, fps=FPS, codec="libx264", quality=8, ffmpeg_params=["-pix_fmt", "yuv420p"]
    )
    fr = 0
    cover_saved = False
    for kind, pay, dur, ch in segs:
        n = int(dur * FPS)
        for k in range(n):
            lt = k / FPS
            img = V.GLOW.copy()
            d = ImageDraw.Draw(img, "RGBA")
            if kind == "hook":
                V.draw_hook(d, min(1.0, lt / dur))
                out = img
            elif kind == "card":
                V.draw_card(d, pay, ch, TOTAL_CH, min(1.0, lt / dur))
                out = img
            elif kind == "roll":
                it, ln, _ = pay
                base = rolls.get(it["repo"])
                if base is None:
                    V.draw_card(d, it, ch, TOTAL_CH, 1.0)
                    out = img
                else:
                    audio_t = max(0.0, lt)
                    out = draw_roll_v3(base, it, ln, ch, audio_t, ln["dur"])
            else:
                V.draw_cta(d, items[:3])
                out = img
            if not cover_saved and fr / FPS > 1.0:
                out.save(os.path.join(BASE, "tiktok-github-v3-cover.png"))
                cover_saved = True
            w.append_data(np.asarray(out.convert("RGB")))
            fr += 1
        print(f"  seg {ch}/{len(segs)} {kind} done")
    w.close()
    # --- audio assembly: silence(CARD) + line + tail per repo; hook/cta straight
    lst = os.path.join(TMP, "concat.txt")
    parts = []
    idx = 0

    def silence(dur, tag):
        pth = os.path.join(TMP, f"sil_{tag}.mp3")
        if not os.path.exists(pth):
            subprocess.run(
                [
                    FF,
                    "-y",
                    "-f",
                    "lavfi",
                    "-i",
                    "anullsrc=r=24000:cl=mono",
                    "-t",
                    str(round(dur, 2)),
                    "-q:a",
                    "4",
                    pth,
                ],
                capture_output=True,
            )
        return pth

    with open(lst, "w", encoding="utf-8") as f:
        for kind, pay, dur, _ch in segs:
            if kind == "hook":
                ln = pay
                f.write(f"file '{ln['mp3']}'\n")
                parts.append(ln["mp3"])
                if dur - ln["dur"] > 0.05:
                    s = silence(dur - ln["dur"], f"hook{idx}")
                    f.write(f"file '{s}'\n")
                    parts.append(s)
            elif kind == "card":
                s = silence(dur, f"card{idx}")
                f.write(f"file '{s}'\n")
                parts.append(s)
            elif kind == "roll":
                it, ln, _ = pay
                if ln.get("mp3"):
                    f.write(f"file '{ln['mp3']}'\n")
                    parts.append(ln["mp3"])
                if dur - ln["dur"] > 0.05:
                    s = silence(dur - ln["dur"], f"roll{idx}")
                    f.write(f"file '{s}'\n")
                    parts.append(s)
            else:
                ln, _ = pay
                f.write(f"file '{ln['mp3']}'\n")
                parts.append(ln["mp3"])
                if dur - ln["dur"] > 0.05:
                    s = silence(dur - ln["dur"], f"cta{idx}")
                    f.write(f"file '{s}'\n")
                    parts.append(s)
            idx += 1
    narr = os.path.join(TMP, "narration_full.mp3")
    subprocess.run(
        [FF, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", narr], capture_output=True
    )
    final = os.path.join(BASE, "tiktok-github-v3.mp4")
    subprocess.run(
        [FF, "-y", "-i", silent, "-i", narr, "-c:v", "copy", "-c:a", "aac", "-shortest", final],
        capture_output=True,
    )
    print(f"Saved: {final} ({os.path.getsize(final) // 1024} KB)")
    cap = (
        "Top 10 GitHub tuần này — bản có thuyết minh tiếng Việt! (số liệu thật) "
        "Repo nào đáng cài nhất? #GitHub #LậpTrình #OpenSource #CôngNghệ #AI #TinCôngNghệ"
    )
    open(os.path.join(BASE, "tiktok-github-v2-caption.txt"), "w", encoding="utf-8").write(
        cap + "\n"
    )
    open(os.path.join(BASE, "tiktok-github-v3-caption.txt"), "w", encoding="utf-8").write(
        cap + "\n"
    )
    for f_ in (
        "tiktok-github-v3.mp4",
        "tiktok-github-v3-cover.png",
        "tiktok-github-v3-caption.txt",
    ):
        shutil.copy(os.path.join(BASE, f_), os.path.join(DOCS, f_))
    print("Copied to docs/")


if __name__ == "__main__":
    main()
