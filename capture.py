# -*- coding: utf-8 -*-
"""V4 slice 2: scrolled GitHub captures via bsk (resume-safe).
Shots -> TMP/shots/{i}_{k}.png, strips -> TMP/strip_{i}.png (stacked, 650px step).
Falls back to banner art in render if a strip is missing.
"""

import json
import os
import subprocess
import time

from PIL import Image

BSK = r"C:\Users\ADMIN\.local\bin\bsk.exe"
TMP = r"C:\Users\ADMIN\AppData\Local\Temp\opencode\ttv4"
SHOTS = 6
STEP = 650


def run(*args):
    p = subprocess.run([BSK] + list(args), capture_output=True, text=True, timeout=120)
    return p.returncode, (p.stdout or "").strip()


def main():
    nar = json.load(open(os.path.join(TMP, "narration.json"), encoding="utf-8"))
    repos = [(r["rank"], r["repo"]) for r in nar if r["key"].startswith("repo")]
    os.makedirs(os.path.join(TMP, "shots"), exist_ok=True)
    rc, out = run("session", "start", "--json", "--no-focus", "--width", "500", "--height", "1200")
    if rc != 0:
        print("session start failed:", out[:200])
        return
    sid = json.loads(out)["session_id"]
    print("session:", sid)
    try:
        for rank, repo in repos:
            paths = [os.path.join(TMP, "shots", f"{rank}_{k}.png") for k in range(SHOTS)]
            if all(os.path.exists(p) and os.path.getsize(p) > 10000 for p in paths):
                print(f"  repo{rank} {repo}: cached")
            else:
                rc, _ = run("navigate", f"https://github.com/{repo}", "--session", sid)
                time.sleep(2.5)
                for k in range(SHOTS):
                    if not (os.path.exists(paths[k]) and os.path.getsize(paths[k]) > 10000):
                        if k > 0:
                            run("wheel", "--delta-y", str(STEP), "--session", sid)
                            time.sleep(1.2)
                        run("screenshot", "--session", sid, "--out", paths[k])
                        time.sleep(0.6)
                print(f"  repo{rank} {repo}: shot")
            # stitch strip
            strip = os.path.join(TMP, f"strip_{rank}.png")
            try:
                imgs = [Image.open(p).convert("RGB") for p in paths]
                w_, h_ = imgs[0].size
                canvas = Image.new("RGB", (w_, h_ + STEP * (SHOTS - 1)), (10, 10, 12))
                for k, im in enumerate(imgs):
                    canvas.paste(im, (0, k * STEP))
                canvas.save(strip)
                print(f"  repo{rank}: strip {canvas.size}")
            except Exception as e:
                print(f"  repo{rank}: stitch fail {str(e)[:80]}")
    finally:
        run("session", "stop", sid)
        print("session stopped")


main()
