#!/usr/bin/env python3
"""Fetch a comic's panels + narration from the CrimeKickers hub into episodes/<slug>/.

Usage: python3 spike/fetch_comic.py s01e02-feel-the-room
"""
import json, pathlib, subprocess, sys, urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
HUB = "https://hub.wandergeek.org"

def curl(url, out):
    # ponytail: img CDN 403s urllib's default UA; curl with browser headers works
    subprocess.run(["curl", "-sL", "-A", UA, "-e", HUB + "/", url, "-o", str(out)], check=True)

def main(slug):
    d = pathlib.Path("episodes") / slug
    (d / "panels").mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(f"{HUB}/api/comics/{slug}", headers={"User-Agent": UA})
    comic = json.load(urllib.request.urlopen(req))
    (d / "comic.json").write_text(json.dumps(comic, indent=1))
    imgs = [it["url"] for it in comic["items"] if it["type"] == "image"]
    for i, u in enumerate(imgs, 1):
        curl(u, d / "panels" / f"{i}.png")
    if comic.get("audio_url"):
        curl(comic["audio_url"], d / "narration.mp3")
    # segments.json template: hub text items if present, else fill from the lore vault's
    # "Panel-synced breakdown" in crimekickerslor/Stories/<EP>/<EP> — Narration.md
    texts = [it["text_content"] for it in comic["items"] if it["type"] == "text"]
    (d / "segments.json").write_text(json.dumps(texts or ["" for _ in imgs], indent=1, ensure_ascii=False))
    print(f"{comic['title']}: {len(imgs)} panels -> {d}/ (check segments.json)")

if __name__ == "__main__":
    main(sys.argv[1])
