# Step 04 — Video Generation Prompts

## Input
- `03-review.md`: use only the **FINAL SCRIPT** section
- `../../brand-profile.md`: visual style and colors, if filled in

## Task
Turn the final script into everything needed to produce the video with AI tools and a simple editor.

This step writes two files with the same scene prompts:
- `04-video-prompts.md`: for humans, to read or paste into any video tool manually
- `04-scenes.json`: for `scripts/generate_video.py` (step 05), which generates the clips with Veo automatically

### 1. Tool
Always write the prompts for **Gemini / Veo**. Do not ask. The prompts also work when pasted into other text-to-video tools (Runway, Kling, Sora, and so on).

### 2. Write one video prompt per scene
Each scene must be 8 seconds or less. Give each AI-generated scene a `duration_seconds` of **4, 6, or 8** (Veo clip lengths). Pick the length closest to the script timing and above it, then trim in the editor. Write every prompt so it stands on its own, because the tool does not remember earlier prompts. Repeat the character, setting, and style details in every prompt so the scenes look consistent.

Each prompt covers:
- **Subject**: who or what is on screen (repeat the same description in every scene)
- **Action**: what happens
- **Setting**: where it happens
- **Camera**: shot type and movement (close-up, slow push-in, handheld, and so on)
- **Lighting and mood**
- **Style**: realistic, 3D, motion graphics, and so on (keep it the same across scenes)
- **Format**: vertical 9:16, duration in seconds
- **Audio** (if the tool supports it): ambient sound or dialogue
- **Avoid**: on-screen text inside the generated video, because AI tools render text badly. Captions get added in the editor.

For scenes showing the real product UI, do **not** generate them. Mark them `SCREEN RECORDING` with notes on what to capture.

### 3. Voiceover
Give the full voiceover as one clean block of text, ready for a text-to-speech tool or a human recording. Add the tone direction (for example "energetic, warm, mid-paced").

### 4. Captions
Write the on-screen captions in SRT format, timed to the script.

### 5. Edit plan
Give a short assembly guide for CapCut or any editor: clip order, where the captions and text overlays go, music mood, transitions, and the end card with the CTA.

## Output
Write `04-video-prompts.md` in the run folder:

```markdown
# Video Production Pack — <reel title>

**Tool:** Gemini/Veo | **Format:** 9:16 | **Length:** NNs (30–40)

## Visual consistency sheet
- Character: ...
- Setting: ...
- Style / color palette: ...

## Scene prompts
### Scene 1 (0–2s) — AI GENERATE
```
<prompt>
```
### Scene 3 (6–12s) — SCREEN RECORDING
Capture: ...

## Voiceover
Tone: ...
<full text>

## Captions (SRT)
1
00:00:00,000 --> 00:00:02,000
...

## Edit plan
1. ...

## Before you publish
- [ ] Fill placeholders: ...
- [ ] Check product claims with the marketing/legal owner
```

Also write `04-scenes.json` in the run folder: every scene in order, with exactly these fields:

```json
{
  "scenes": [
    {
      "scene": 1,
      "type": "generate",
      "start": 0,
      "end": 2,
      "duration_seconds": 4,
      "aspect_ratio": "9:16",
      "prompt": "<the full standalone prompt, identical to 04-video-prompts.md>",
      "negative_prompt": "on-screen text, captions, watermarks, logos, distorted hands"
    },
    {
      "scene": 3,
      "type": "screen_recording",
      "start": 6,
      "end": 12,
      "notes": "Capture: ..."
    }
  ]
}
```

- `type` is `generate` (Veo makes it) or `screen_recording` (you record it).
- The JSON must be valid. No comments, no trailing commas.
