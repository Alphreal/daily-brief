# -*- coding: utf-8 -*-
"""V4: scrolled real-page B-roll + expressive VN narration + synced karaoke.
Run: python tiktok_github_v4.py  (needs ttv4/narration.json + strip_{i}.png)
"""
import json
import os
import re
import subprocess
from PIL import Image, ImageDraw
import numpy as np
import tiktok_github_v2 as V
import tiktok_github_v3 as T3

BASE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(BASE, "docs")
TMP = r"C:\Users\ADMIN\AppData\Local\Temp\opencode\ttv4"
FF = r"C:\Users\ADMIN\AppData\Roaming\Python\Python311\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
W, H, FPS = V.W, V.H, V.FPS
CARD_DUR, TAIL, TOTAL_CH = 2.0, 0.7, 12

def fresh_by_repo():
    items, _ = V.load_items()
    return {it["repo"]: it for it in items}

def load_sched():
    nar = json.load(open(os.path.join(TMP, "narration.json"), encoding="utf-8"))
    fresh = fresh_by_repo()
    repos = []  # dicts: rank, repo, short, gain, gain_s, total, desc, text, mp3, dur
    for ln in nar:
        if not ln["key"].startswith("repo"):
            continue
        fr = fresh.get(ln["repo"], {})
        gm = re.search(r"tăng ([\d.]+) sao", ln["text"])
        gain_txt = gm.group(1) if gm else "?"
        try:
            gain_int = int(gain_txt.replace(".", ""))
        except Exception:
            gain_int = 0
        repos.append({
            "rank": ln["rank"], "repo": ln["repo"],
            "short": ln["repo"].split("/")[-1][:22],
            "gain": gain_txt, "gain_int": gain_int, "total": fr.get("total", "..."),
            "desc": fr.get("desc", ""), "text": ln["text"],
            "mp3": ln.get("mp3"), "dur": ln["dur"],
        })
    hook = [l for l in nar if l["key"] == "hook"][0]
    cta = [l for l in nar if l["key"] == "cta"][0]
    return hook, repos, cta

def draw_scroll(strip, repo, words, ch, elapsed, dur):
    p = max(0.0, min(1.0, elapsed / dur if dur else 1.0))
    max_y = max(0, strip.height - H)
    y0 = int(max_y * V.smooth(p))
    frame = strip.crop((0, y0, W, y0 + H)).convert("RGB")
    d = ImageDraw.Draw(frame, "RGBA")
    d.rectangle([0, 0, W, 200], fill=(0, 0, 0, 110))
    d.rectangle([0, H - 420, W, H], fill=(0, 0, 0, 130))
    d.rectangle([0, 0, W, 7], fill=(V.RED[0], V.RED[1], V.RED[2], 255))
    d.text((36, 30), f"{ch:02d} / {TOTAL_CH:02d}", font=V.F_SMALL, fill=V.MUTED)
    chip = repo[:34]
    cw = d.textlength(chip, font=V.F_SMALL) + 40
    d.rounded_rectangle([(W - cw) / 2, 120, (W + cw) / 2, 168], radius=24, fill=(0, 0, 0, 170))
    V.center(d, W / 2, 128, chip, V.F_SMALL, V.WHITE)
    V.draw_karaoke(d, [words], V.F_CAP, W / 2, 950, min(0.99, p / 2.4))
    return frame

def main():
    import imageio.v2 as iio
    import shutil
    V.GLOW = V.make_glow()
    hook, repos, cta = load_sched()
    print(f"Repos: {len(repos)}")
    strips = {}
    for r in repos:
        pth = os.path.join(TMP, f"strip_{r['rank']}.png")
        if os.path.exists(pth):
            im = Image.open(pth).convert("RGB")
            s = W / im.width
            strips[r["rank"]] = im.resize((W, int(im.height * s)), Image.BILINEAR)
            print(f"  strip {r['rank']}: {strips[r['rank']].size}")
    # schedule: (kind, payload, dur)
    segs = [("hook", hook, hook["dur"] + 1.5)]
    for r in repos:
        segs.append(("card", r, CARD_DUR))
        segs.append(("roll", r, max(3.2, r["dur"] + TAIL)))
    segs.append(("cta", cta, cta["dur"] + 1.5))
    total_dur = sum(s[2] for s in segs)
    N = int(total_dur * FPS)
    print(f"Video: {round(total_dur, 1)}s, {N} frames")
    ch_of = {}
    ch = 1
    for idx, (kind, pay, dur) in enumerate(segs):
        if kind == "hook":
            ch_of[idx] = 1
        elif kind == "cta":
            ch_of[idx] = TOTAL_CH
        else:
            if kind == "card":
                ch += 1
            ch_of[idx] = ch
    silent = os.path.join(BASE, "tiktok-github-v4-silent.mp4")
    w = iio.get_writer(silent, fps=FPS, codec="libx264", quality=8,
                       ffmpeg_params=["-pix_fmt", "yuv420p"])
    fr = 0
    cover_saved = False
    for idx, (kind, pay, dur) in enumerate(segs):
        n = int(dur * FPS)
        chn = ch_of[idx]
        for k in range(n):
            lt = k / FPS
            if kind == "hook":
                img = V.GLOW.copy()
                d = ImageDraw.Draw(img, "RGBA")
                V.draw_hook(d, min(1.0, lt / dur))
                hw = pay["text"].split()
                out = img
            elif kind == "card":
                img = V.GLOW.copy()
                d = ImageDraw.Draw(img, "RGBA")
                V.draw_card(d, {"rank": pay["rank"], "gain_s": f"+{pay['gain']}",
                                "short": pay["short"], "gain": pay["gain_int"], "total": pay["total"],
                                "desc": pay["desc"]}, chn, TOTAL_CH, min(1.0, lt / dur))
                out = img
            elif kind == "roll":
                words = T3.cap_words(pay, pay["text"], pay["gain"])
                out = draw_scroll(strips[pay["rank"]], pay["repo"], words, chn, lt, pay["dur"])
            else:
                img = V.GLOW.copy()
                d = ImageDraw.Draw(img, "RGBA")
                tops = sorted(repos, key=lambda r: r["rank"])[:3]
                V.draw_cta(d, [{"rank": t["rank"], "short": t["short"],
                                "gain": int(t["gain"].replace(".", "")) if t["gain"] != "?" else 0}
                               for t in tops])
                out = img
            if not cover_saved and fr / FPS > 1.0:
                out.save(os.path.join(BASE, "tiktok-github-v4-cover.png"))
                cover_saved = True
            w.append_data(np.asarray(out.convert("RGB")))
            fr += 1
        print(f"  seg {chn}/{len(segs)} {kind} done")
    w.close()
    # --- audio: hook + [sil2.0 + line + tail] + cta, then loudnorm master
    lst = os.path.join(TMP, "concat4.txt")
    sidx = 0
    def silence(dur, tag):
        pth = os.path.join(TMP, f"s4_{tag}.mp3")
        if not os.path.exists(pth):
            subprocess.run([FF, "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                            "-t", str(round(dur, 2)), "-q:a", "4", pth], capture_output=True)
        return pth
    with open(lst, "w", encoding="utf-8") as f:
        for kind, pay, dur in segs:
            if kind == "hook":
                f.write(f"file '{pay['mp3']}'\n")
                if dur - pay["dur"] > 0.05:
                    f.write(f"file '{silence(dur - pay['dur'], f'h{sidx}')}'\n")
            elif kind == "card":
                f.write(f"file '{silence(dur, f'c{sidx}')}'\n")
            elif kind == "roll":
                f.write(f"file '{pay['mp3']}'\n")
                if dur - pay["dur"] > 0.05:
                    f.write(f"file '{silence(dur - pay['dur'], f'r{sidx}')}'\n")
            else:
                f.write(f"file '{pay['mp3']}'\n")
                if dur - pay["dur"] > 0.05:
                    f.write(f"file '{silence(dur - pay['dur'], f'e{sidx}')}'\n")
            sidx += 1
    raw = os.path.join(TMP, "narration4_raw.mp3")
    subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", raw],
                   capture_output=True)
    master = os.path.join(TMP, "narration4_master.mp3")
    subprocess.run([FF, "-y", "-i", raw, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,acompressor=threshold=-18dB:ratio=3:attack=8:release=120",
                    "-ar", "24000", master], capture_output=True)
    final = os.path.join(BASE, "tiktok-github-v4.mp4")
    subprocess.run([FF, "-y", "-i", silent, "-i", master, "-c:v", "copy", "-c:a", "aac",
                    "-shortest", final], capture_output=True)
    print(f"Saved: {final} ({os.path.getsize(final) // 1024} KB)")
    for f_ in ("tiktok-github-v4.mp4", "tiktok-github-v4-cover.png"):
        shutil.copy(os.path.join(BASE, f_), os.path.join(DOCS, f_))
    print("Copied to docs/")

if __name__ == "__main__":
    main()
