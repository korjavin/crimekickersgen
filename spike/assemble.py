#!/usr/bin/env python3
"""Assemble veo clips + narration into an episode video.

Usage: python3 spike/assemble.py episodes/<slug>
Expects in that dir:
  console/clip1.mp4 .. clipN.mp4  - 8s veo clips; clip i animates panel i -> panel i+1,
                                    last clip animates the last panel in place
  narration.mp3                   - full produced narration
  segments.json                   - list of N narration texts (one per panel), used only
                                    for word-count-proportional pacing

Pacing: segment i holds clip i's FIRST frame, then plays the 8s clip so it lands on
panel i+1 exactly when segment i+1 starts (last segment: play clip, hold last frame).
Transitions are seamless because clip i's end frame == clip i+1's start frame.
Output: <dir>/episode.mp4
"""
import json, pathlib, subprocess, sys

CLIP = 8.0

def main(d):
    d = pathlib.Path(d)
    texts = json.loads((d / "segments.json").read_text())
    n = len(texts)
    narr = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
         str(d / "narration.mp3")], capture_output=True, text=True).stdout)
    wc = [max(len(t.split()), 1) for t in texts]
    durs = [max(CLIP + 1, narr * w / sum(wc)) for w in wc]
    durs = [x * narr / sum(durs) for x in durs]
    print("segment durations:", [round(x, 1) for x in durs])

    filters = []
    for i in range(1, n + 1):
        pad = durs[i - 1] - CLIP
        mode = "start_mode=clone:start_duration" if i < n else "stop_mode=clone:stop_duration"
        filters.append(f"[{i-1}:v]tpad={mode}={pad:.3f}[v{i}]")
    fc = (";".join(filters) + ";" + "".join(f"[v{i}]" for i in range(1, n + 1))
          + f"concat=n={n}:v=1:a=0[vout]")

    cmd = ["ffmpeg", "-y"]
    for i in range(1, n + 1):
        cmd += ["-i", str(d / "console" / f"clip{i}.mp4")]
    cmd += ["-i", str(d / "narration.mp3"), "-filter_complex", fc,
            "-map", "[vout]", "-map", f"{n}:a", "-c:v", "libx264", "-preset", "medium",
            "-crf", "21", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
            "-shortest", str(d / "episode.mp4")]
    subprocess.run(cmd, check=True)
    print("wrote", d / "episode.mp4")

if __name__ == "__main__":
    main(sys.argv[1])
