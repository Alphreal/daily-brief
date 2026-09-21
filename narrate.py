# -*- coding: utf-8 -*-
"""Slice 1: synthesize per-line VN narration, measure durations.
Writes narration.json: [{key, text, mp3, dur}]. Falls back to estimate on failure.
"""
import asyncio
import json
import os
import re
import subprocess
import urllib.request
import xml.etree.ElementTree as ET

import brief

TMP = r"C:\Users\ADMIN\AppData\Local\Temp\opencode\ttv3"
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

def build_lines():
    weekly, _ = brief.monday_github_trending()
    lines = [{"key": "hook",
              "text": "Top mười GitHub tuần này! Mười repo được thả sao nhiều nhất, số liệu thật!"}]
    for i, r in enumerate(weekly[:10], 1):
        repo = re.sub(r"[^\x20-\uFFFF]", "", r["repo"])
        gain = int(re.search(r"([\d,]+)", r.get("gained", "0")).group(1).replace(",", ""))
        lines.append({
            "key": f"repo{i}",
            "rank": i, "repo": repo,
            "text": f"Hạng {i}, {spoken(repo)}, tăng {vn_num(gain)} sao trong một tuần. {TIER[(i - 1) % len(TIER)]}",
        })
    lines.append({"key": "cta",
                  "text": "Repo nào đáng cài nhất? Lưu lại, follow để nhận tin AI mỗi ngày!"})
    return lines

async def synth_one(text, mp3):
    import edge_tts
    await edge_tts.Communicate(text, VOICE).save(mp3)

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
            if not os.path.exists(mp3):
                await synth_one(ln["text"], mp3)
            d = duration(mp3)
            ln["dur"] = round(d, 2) if d else round(0.55 * len(ln["text"].split()) + 0.4, 2)
            print(f"  {ln['key']}: {ln['dur']}s")
        except Exception as e:
            print(f"  {ln['key']}: SYNTH FAIL {str(e)[:100]} — estimate used")
            ln["mp3"] = None
            ln["dur"] = round(0.55 * len(ln["text"].split()) + 0.4, 2)
    json.dump(lines, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("WROTE", OUT_JSON, "total audio:", round(sum(l["dur"] for l in lines), 1), "s")

asyncio.run(main())
