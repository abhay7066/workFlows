#!/usr/bin/env bash
# Makes every workflow (any folder with a SKILL.md) discoverable by every agent tool.
# The real files stay in <workflow>/ — this only creates symlinks, so there is one source of truth.
#
# Usage:
#   ./install.sh            # project level: tools find skills when started inside this repo
#   ./install.sh --global   # user level: tools find skills from any directory
#
# Safe to re-run after adding a new workflow.

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Skill folders each tool scans. .agents/skills is the cross-tool standard; the rest are tool-specific.
SKILL_DIRS=(.agents/skills .claude/skills .gemini/skills .cursor/skills .codex/skills)

# Instruction files each tool reads at startup — all point to AGENTS.md.
INSTRUCTION_LINKS=(CLAUDE.md GEMINI.md)

if [[ "${1:-}" == "--global" ]]; then
	BASE="$HOME"
	echo "Installing globally into $HOME"
else
	BASE="$REPO"
	echo "Installing at project level in $REPO"
	for f in "${INSTRUCTION_LINKS[@]}"; do
		ln -sfn AGENTS.md "$REPO/$f"
	done
fi

for workflow in "$REPO"/*/; do
	workflow="${workflow%/}"
	[[ -f "$workflow/SKILL.md" ]] || continue
	name="$(basename "$workflow")"
	for dir in "${SKILL_DIRS[@]}"; do
		mkdir -p "$BASE/$dir"
		ln -sfn "$workflow" "$BASE/$dir/$name"
	done
	echo "  linked: $name"
done

echo "Done. Restart any running agent session to pick up new skills."
