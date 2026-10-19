# AI Workflows

This repo holds reusable, LLM-agnostic automation workflows. Any AI agent (Claude Code, Codex, Gemini CLI, Cursor, ...) can run them.

## How this repo is organized

```
workflows/
├── AGENTS.md              # This file — rules for any AI working here
├── CLAUDE.md, GEMINI.md   # Symlinks to AGENTS.md (each tool reads its own file name)
├── install.sh             # Creates the skill symlinks below — re-run after adding a workflow
├── .agents/skills/        # Generated symlinks: cross-tool standard location
├── .claude/ .gemini/ .cursor/ .codex/   # Generated symlinks: tool-specific skill folders
└── <workflow-name>/       # One folder per workflow — the ONLY place real files live
    ├── SKILL.md           # Entry point: what the workflow does and the order of steps
    ├── steps/             # One .md file per step, numbered in execution order
    ├── outputs/           # Each run writes to outputs/<YYYY-MM-DD>-<slug>/
    └── scripts/           # Optional — added only when a step needs deterministic code
```

## Available workflows

| Workflow | What it does | Entry point |
|----------|--------------|-------------|
| `marketing-video` | Turns a product/marketing prompt into a strategy, a reel script, a reviewed final script, and ready-to-use video-generation prompts | `marketing-video/SKILL.md` |

## How to run a workflow

**Routing rule for any AI agent:** when the user's request matches a workflow in the table above, even if your tool has no skill support, open that workflow's `SKILL.md` and follow it.

1. Read the workflow's `SKILL.md`.
2. Execute the step files in `steps/` in numeric order.
3. Each step reads the previous step's output file from the run folder and writes its own output file there.
4. Never skip the output file — the files are the hand-off between steps, so a run can be resumed or re-run from any step.

## Rules for adding or editing workflows

- Workflow folder names are lowercase kebab-case (`daily-jira-brief`, not `DailyJiraBrief`).
- `SKILL.md` must start with YAML frontmatter containing `name` (same as folder name) and `description` (when to use it).
- Each step file states: **Input** (which files it reads), **Task** (what to do), **Output** (exact file name and format).
- Write instructions in plain Markdown. Do not rely on features specific to one AI tool.
- Add a `scripts/` folder only when a step must be deterministic, handles large data, or needs something the AI cannot do itself (rendering, file conversion, API calls on a schedule).
- Never put API keys or secrets in any file. Use a gitignored `.env`.
- After adding a workflow: add it to the table above and run `./install.sh`.
- Never edit files inside `.agents/`, `.claude/`, `.gemini/`, `.cursor/`, or `.codex/` directly — they are symlinks to the workflow folders.
