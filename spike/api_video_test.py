#!/usr/bin/env python3
"""Submit one veo-3.1 clip via the ElevenLabs Flows API (panel1 -> panel2) and poll.

BLOCKED as of 2026-08-24: the whole /v1/flows API (image AND video, even read-only GETs)
returns 402 paid_plan_required on the current 'creator' plan. Needs Pro or above.
Script is otherwise correct — rerun after the plan upgrade:

  export ELEVENLABS_API_KEY=$(~/Projects/stash/kv get secrets/eleven-api-key)
  uv run --with elevenlabs python spike/api_video_test.py episodes/<slug>
"""
import base64, os, sys, time
from elevenlabs.client import ElevenLabs
from elevenlabs.types.video_generation_request import VideoGenerationRequest_Veo31Generate001
from elevenlabs.types.image_reference import ImageReference_InlineBase64

d = sys.argv[1] if len(sys.argv) > 1 else "."
client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])

def img_ref(path):
    return ImageReference_InlineBase64(
        type="inline_base64",
        content_base_64=base64.b64encode(open(path, "rb").read()).decode(),
        mime_type="image/png",
    )

PROMPT = (
    "Animated motion comic in a detailed ink-and-wash comic book illustration style, "
    "matching the start frame exactly. Smooth continuous motion from the start frame "
    "scene to the end frame scene, consistent line art and colors, no new text appears."
)

resp = client.flows.video.create(request=VideoGenerationRequest_Veo31Generate001(
    model_id="veo-3.1-generate-001",
    prompt=PROMPT,
    duration_secs=8,
    aspect_ratio="16:9",
    resolution="720p",
    generate_audio=False,
    start_frame=img_ref(f"{d}/panels/1.png"),
    end_frame=img_ref(f"{d}/panels/2.png"),
))
print("JOB ID:", resp.id, "status:", resp.status, flush=True)

interval, waited = 10, 0  # docs: poll video <= 1 req / 10 s
while waited < 900:
    time.sleep(interval)
    waited += interval
    if waited > 120:
        interval = 20
    g = client.flows.video.get(resp.id)
    print(f"[{waited}s]", g.status, flush=True)
    if g.status == "completed":
        import urllib.request
        urllib.request.urlretrieve(g.content_url, "api_clip1.mp4")  # signed URL expires ~1h
        print("api_clip1.mp4 written")
        sys.exit(0)
    if g.status == "failed":
        print("FAILED:", getattr(g, "failure_reason", None), getattr(g, "error_message", None))
        sys.exit(1)
print("TIMEOUT; job id", resp.id)
sys.exit(2)
