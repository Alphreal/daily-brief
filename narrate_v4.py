# -*- coding: utf-8 -*-
"""V4 slice 1: expressive SSML narration (NamMinh), per-line mp3 + durations.
Skips existing files (resume-safe). Writes ttv4/narration.json.
"""
import asyncio
import json
import os
import re
import subprocess

import brief

TMP = r"C:\Users\ADMIN\AppData\Local\Temp\opencode\ttv4"
FF = r"C:\Users\ADMIN\AppData\Roaming\Python\Python311\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
VOICE = "vi-VN-NamMinhNeural"
OUT_JSON = os.path.join(TMP, "narration.json")

TIER = [
    "Quán quân tuần này!",
    "Tăng tốc mạnh mẽ!",
    "Lọt top ba, gọi tên!",
    "Đáng để mắt tới!",
    "Mới nổi, đáng chú ý!",
    "Cộng đồng chốt đơn!",
]

def vn_num(n):
    return f"{n:,}".replace(",", ".")

def spoken(repo):
    return repo.split("/")[-1].replace("-", " ").replace("_", " ")

def ssml_wrap(inner):
    return (f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
            f'xml:lang="vi-VN"><voice name="{VOICE}">{inner}</voice></speak>')

def build_lines():
    weekly, _ = brief.monday_github_trending()
    lines = [{"key": "hook", "rate": "+8%",
              "text": "Top mười GitHub tuần này! Mười repo được thả sao nhiều nhất... số liệu thật!"}]
    for i, r in enumerate(weekly[:10], 1):
        repo = re.sub(r"[^\x20-\uFFFF]", "", r["repo"])
        gain = int(re.search(r"([\d,]+)", r.get("gained", "0")).group(1).replace(",", ""))
        tier = TIER[(i - 1) % len(TIER)]
        lines.append({
            "key": f"repo{i}", "rank": i, "repo": repo, "rate": "-3%",
            "text": f"Hạng {i}, {spoken(repo)}... tăng {vn_num(gain)} sao trong một tuần... {tier}",
        })
    lines.append({"key": "cta", "rate": "+0%",
                  "text": "Repo nào đáng cài nhất? Lưu lại, follow để nhận tin AI mỗi ngày!"})
    return lines

async def synth_one(text, rate, mp3):
    import edge_tts
    await edge_tts.Communicate(text, VOICE, rate=rate).save(mp3)

def duration(mp3):
    p = subprocess.run([FF, "-i", mp3], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", p.stderr)
    if not m:
        return None
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))

async def main():
    os.makedirs(TMP, exist_ok=True)
    lines = build_lines()
    print(f"Lines: {len(lines)}")
    for ln in lines:
        mp3 = os.path.join(TMP, ln["key"] + ".mp3")
        ln["mp3"] = mp3
        try:
            if not (os.path.exists(mp3) and os.path.getsize(mp3) > 1000):
                await synth_one(ln["text"], ln.get("rate", "+0%"), mp3)
            d = duration(mp3)
            ln["dur"] = round(d, 2) if d else 6.0
            print(f"  {ln['key']}: {ln['dur']}s", flush=True)
        except Exception as e:
            print(f"  {ln['key']}: FAIL {str(e)[:100]}")
            ln["mp3"] = None
            ln["dur"] = 6.0
    for ln in lines:
        ln.pop("ssml", None)
    json.dump(lines, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("WROTE", OUT_JSON, "total:", round(sum(l["dur"] for l in lines), 1), "s")

asyncio.run(main())
