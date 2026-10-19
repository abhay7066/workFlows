#!/usr/bin/env python3
"""Generate one video clip per scene with Google Veo (Gemini API).

Reads <run-dir>/04-scenes.json (written by step 04) and saves clips to <run-dir>/videos/scene-NN.mp4.

By default this is a DRY RUN: it only shows what would be generated. Veo is billed per second of
video, so nothing is sent to the API unless you pass --yes.

Usage:
	generate_video.py <run-dir>                 # dry run: show the plan and the cost driver (total seconds)
	generate_video.py <run-dir> --yes           # generate every AI scene that has no clip yet
	generate_video.py <run-dir> --yes --scenes 1,4   # generate only scenes 1 and 4
	generate_video.py <run-dir> --yes --force   # regenerate even if the clip already exists
	generate_video.py --list-models             # show the Veo models your key can use

Config (environment variables or workflows/.env):
	GEMINI_API_KEY   required
	VEO_MODEL        optional, default: veo-3.1-generate-preview
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path

DEFAULT_MODEL = "veo-3.1-generate-preview"
POLL_SECONDS = 10
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

log = logging.getLogger("generate_video")


def load_env_file(path):
	"""Load KEY=VALUE lines from .env without overriding variables already set in the shell."""
	if not path.exists():
		return
	for line in path.read_text().splitlines():
		line = line.strip()
		if not line or line.startswith("#") or "=" not in line:
			continue
		key, value = line.split("=", 1)
		os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def make_client():
	if not os.environ.get("GEMINI_API_KEY"):
		log.error("GEMINI_API_KEY is not set. Add it to %s (see .env.example).", ENV_FILE)
		sys.exit(1)
	from google import genai
	return genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def load_scenes(run_dir, only):
	scenes_file = run_dir / "04-scenes.json"
	if not scenes_file.exists():
		log.error("%s not found. Run step 04 of the workflow first.", scenes_file)
		sys.exit(1)
	scenes = json.loads(scenes_file.read_text())["scenes"]
	if only:
		scenes = [s for s in scenes if s["scene"] in only]
	return scenes


def generate_scene(client, model, scene, out_path):
	from google.genai import types

	config = types.GenerateVideosConfig(
		aspect_ratio=scene.get("aspect_ratio", "9:16"),
		negative_prompt=scene.get("negative_prompt") or None,
		duration_seconds=scene.get("duration_seconds"),
	)
	operation = client.models.generate_videos(model=model, prompt=scene["prompt"], config=config)
	started = time.time()
	while not operation.done:
		log.info("  scene %d: generating... %ds", scene["scene"], int(time.time() - started))
		time.sleep(POLL_SECONDS)
		operation = client.operations.get(operation)

	if operation.error:
		raise RuntimeError(operation.error)
	videos = operation.response.generated_videos if operation.response else None
	if not videos:
		raise RuntimeError("API returned no video (the prompt may have been blocked by safety filters)")

	client.files.download(file=videos[0].video)
	videos[0].video.save(str(out_path))


def list_models():
	client = make_client()
	for m in client.models.list():
		if "veo" in m.name:
			print(m.name)


def main():
	parser = argparse.ArgumentParser(description="Generate scene clips with Veo.")
	parser.add_argument("run_dir", nargs="?", type=Path, help="workflow run folder, e.g. outputs/2026-10-10-ai-coach-reel")
	parser.add_argument("--yes", action="store_true", help="actually call the API (costs money)")
	parser.add_argument("--scenes", help="comma-separated scene numbers to generate, e.g. 1,4")
	parser.add_argument("--force", action="store_true", help="regenerate clips that already exist")
	parser.add_argument("--list-models", action="store_true", help="list Veo models available to your key")
	args = parser.parse_args()

	logging.basicConfig(level=logging.INFO, format="%(message)s")
	load_env_file(ENV_FILE)

	if args.list_models:
		list_models()
		return
	if not args.run_dir:
		parser.error("run_dir is required")

	run_dir = args.run_dir.resolve()
	only = {int(n) for n in args.scenes.split(",")} if args.scenes else None
	model = os.environ.get("VEO_MODEL", DEFAULT_MODEL)
	out_dir = run_dir / "videos"

	todo = []
	for scene in load_scenes(run_dir, only):
		out_path = out_dir / f"scene-{scene['scene']:02d}.mp4"
		if scene.get("type") != "generate":
			log.info("scene %d: skipped (%s — record this one manually)", scene["scene"], scene.get("type"))
		elif out_path.exists() and not args.force:
			log.info("scene %d: skipped (already exists: %s)", scene["scene"], out_path.name)
		else:
			todo.append((scene, out_path))

	total_seconds = sum(s.get("duration_seconds") or 8 for s, _ in todo)
	log.info("\nModel: %s | clips to generate: %d | ~%ds of video (billed per second)", model, len(todo), total_seconds)

	if not todo:
		return
	if not args.yes:
		for scene, out_path in todo:
			log.info("  would generate scene %d -> %s", scene["scene"], out_path.relative_to(run_dir))
		log.info("\nDry run only. Re-run with --yes to generate.")
		return

	client = make_client()
	out_dir.mkdir(exist_ok=True)
	failed = []
	for scene, out_path in todo:
		log.info("scene %d: starting", scene["scene"])
		try:
			generate_scene(client, model, scene, out_path)
			log.info("scene %d: saved %s", scene["scene"], out_path.relative_to(run_dir))
		except Exception as e:
			log.error("scene %d: FAILED — %s", scene["scene"], e)
			failed.append(scene["scene"])

	if failed:
		log.error("\nFailed scenes: %s. Fix the prompt in 04-scenes.json and re-run with --scenes %s",
			failed, ",".join(map(str, failed)))
		sys.exit(1)
	log.info("\nAll clips saved in %s", out_dir)


if __name__ == "__main__":
	main()
