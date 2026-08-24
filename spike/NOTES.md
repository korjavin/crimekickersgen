# Spike notes — comic → video via ElevenLabs (2026-08-24)

Two full episodes produced (S01E1, S01E02): panels + produced narration from the hub,
5 veo-3.1 clips each generated **manually in the ElevenLabs web console** (API is
plan-blocked, see below), assembled with ffmpeg. Results: watchable first-try episodes.
Owner feedback pending.

## The recipe that worked

1. `python3 spike/fetch_comic.py <slug>` — panels + narration.mp3 + segments.json from
   `https://hub.wandergeek.org/api/comics/<slug>`.
2. Fill `segments.json` with the per-panel narration text from the lore vault:
   `~/Projects/crimekickerslor/Stories/<EP>/<EP> — Narration.md`, section
   "Panel-synced breakdown". (Hub text items exist for some episodes but the vault is richer.)
3. Generate clips (console for now): clip i = **start frame panel i, end frame panel i+1**,
   last clip = last panel start-frame only. Settings: Veo 3.1 (standard), 8s, 16:9, 720p,
   audio OFF. Prompts per clip: see `spike/prompts/<slug>/`.
4. `python3 spike/assemble.py episodes/<slug>` → `episode.mp4`.

## Validated

- **Begin→end frame chaining**: clip i ends on the exact image clip i+1 starts from →
  structurally seamless transitions. This is the core design of the future pipeline.
- **Pacing**: segment i = hold clip i's first frame, then play the 8s clip so it lands on
  panel i+1 as narration segment i+1 begins. Segment lengths ∝ word count of segment text,
  normalized to narration duration. Good enough on both episodes.
- Panels are 16:9 (1280×720 or 2048×1152) despite hub metadata saying `1:1` — trust pixels.
- Console clips come back exactly 1280×720, 24fps, 8.000s, no audio track.
- img.cc.wandergeek.org 403s non-browser user agents — send browser UA + referer.
- Prompt craft: repeat one fixed character description in every clip prompt ("blindfolded
  man in the blue W t-shirt") to fight identity drift; write motion beats in narrative
  order; always end with "consistent line art, no new text or captions appear".

## Blockers / decisions

- **API is Pro-gated**: ALL of `/v1/flows/*` (video + image, even GET list) → 402
  `paid_plan_required` on the current **creator** plan. Web console generation works on
  creator. Upgrade to Pro unlocks `spike/api_video_test.py` (written, correct up to the 402).
- **Narration is owner-provided** (produced mp3 per episode on the hub). Per-segment TTS
  was prototyped (voice "Thomas - Calm, Clear and Informative", stability 0.7, style 0.35,
  eleven_multilingual_v2) and then explicitly dropped by the owner — do not re-add.

## Known weaknesses (bead-worthy)

1. Static holds up to ~25s before each transition — needs slow Ken Burns drift on holds.
2. Word-count pacing is approximate — true sync wants forced alignment of narration.mp3
   against per-segment text.
3. Baked-in panel text (SFX like SLOOOSH/KRA-SLURP, speech bubbles, caption boxes) warps
   during veo morphs — would need text-free panel variants from the comic pipeline side.
4. Episode mp4s are 25–36MB at CRF 20-21 720p — fine for local, mind hosting limits.

## Where things are

- Generated episodes (not in git): `out/episode-s01e1.mp4`, `out/episode-s01e02.mp4`.
- Prompts used: `spike/prompts/s01e1/`, `spike/prompts/s01e02/`.
- Backlog: epic `crimekickersgen-c6u` and children track the real CLI.
