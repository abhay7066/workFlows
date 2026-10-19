---
name: marketing-video
description: Use when the user wants a marketing reel or short-form video (Instagram Reels, YouTube Shorts, TikTok, LinkedIn video) created from a product, offer, or idea prompt. Runs end to end from one prompt: strategy, script, review, prompts, and generated video clips (Veo), 30–40s by default.
---

# Marketing Video (Reel) Workflow

Turns a short prompt (for example "a reel for our new AI coaching feature, aimed at sales managers") into generated video clips for a 30–40 second reel, in one run without stopping.

## Flow

```
User prompt
   │
   ▼
01-strategy.md ──► 01-strategy.md      (audience, platform, angle, hooks)
   │
   ▼
02-script.md ────► 02-script.md        (scene-by-scene reel script)
   │
   ▼
03-review.md ────► 03-review.md        (scorecard + improved FINAL script)
   │
   ▼
04-video-generation.md ──► 04-video-prompts.md + 04-scenes.json   (prompts per scene, voiceover, captions, edit plan)
   │
   ▼
05-generate-video.md ──► videos/scene-NN.mp4   (runs scripts/generate_video.py — Veo, always runs)
```

## How to run

1. **Create the run folder**: `outputs/<YYYY-MM-DD>-<short-slug>/` (for example `outputs/2026-10-10-ai-coach-reel/`). All step outputs go here.
2. **Save the user's prompt** exactly as given to `00-brief.md` in the run folder.
3. **Ask questions once, up front.** Check the prompt for the critical fields: product/offer, target audience, and goal (see the table in `steps/01-strategy.md`). If any are missing or unclear, ask for all of them in **one message**, at most 3 questions. This is the only time you ask the user anything. If nothing critical is missing, ask nothing and start. Everything non-critical (platform, tone, CTA, hook choice) is decided by you, with assumptions marked `(assumed)` in the outputs.
4. **Load brand context**: if `brand-profile.md` exists in this folder and has been filled in, read it and apply it in every step.
5. **Run every step file in `steps/` in order without stopping**: `01` → `02` → `03` → `04` → `05`. Read each step file fully before doing it. Do not pause for approval between steps. Always finish with step 05 (video generation).
6. **Only stop early** if something blocks the run, such as a missing `GEMINI_API_KEY` or a setup error. Then tell the user exactly what to fix.
7. **Finish** by telling the user where the run folder is, which clips were generated in `videos/`, and which scenes still need a screen recording, with a 3–4 line summary of the strategy (core message, chosen hook) and the review score. The user can then ask to redo any part.

## Re-running part of the flow

The steps communicate only through files, so you can restart from any step. For example, "redo the script with a funnier tone" means re-running step 02 and then steps 03 and 04, while keeping `01-strategy.md`.

## Rules

- Do not invent product facts, numbers, customer names, or claims. If something is needed and unknown, use a clearly marked placeholder like `[STAT: % time saved]` and list it at the end of the output.
- Write for short-form video: short spoken lines, one idea per scene, captions on screen.
