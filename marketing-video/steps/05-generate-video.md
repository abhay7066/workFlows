# Step 05 — Generate Video Clips (Veo)

## Input
- `04-scenes.json` in the run folder
- `GEMINI_API_KEY` in `workflows/.env`

## Task
Use the script to generate one clip per AI scene. Always run this step, without asking for confirmation. The user has pre-approved generation for every run of this workflow.

Run all commands from the `workflows/` folder.

1. **Check setup.** If `.venv/` does not exist, create it:
   `python3 -m venv .venv && .venv/bin/pip install -r marketing-video/scripts/requirements.txt`
   If `.env` has no `GEMINI_API_KEY`, stop and ask the user to add it. Never ask them to paste the key into the chat.
2. **Generate** (the script prints the plan first, then generates):
   `.venv/bin/python marketing-video/scripts/generate_video.py <run-folder> --yes`
   Each clip takes about 1–5 minutes. The script skips clips that already exist, so it's safe to re-run after a failure.
3. **If a scene fails** (often a safety filter), rewrite that scene's prompt in `04-scenes.json` (and `04-video-prompts.md`), then re-run only that scene once: `... --yes --scenes 3`. If it fails again, leave it and report it at the end.
4. **Later, if the user asks to redo a clip**: change its prompt, then re-run with `--scenes N --force`.

## Output
- `videos/scene-NN.mp4` in the run folder, one per `generate` scene
- Tell the user which scenes still need a screen recording, and point them to the edit plan in `04-video-prompts.md` to assemble the reel (clips + voiceover + captions) in CapCut or any editor.
