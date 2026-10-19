# Step 01 — Marketing Strategy

## Input
- `00-brief.md`: the user's prompt
- `../../brand-profile.md`: brand voice and rules, if filled in

## Task
Turn the brief into a clear strategy *before* any script is written.

### 1. Extract the brief
Find these in the prompt, plus any answers the user gave to the up-front questions (see `SKILL.md`). Do not ask the user anything in this step. For anything non-critical, make a sensible assumption and label it `(assumed)`.

| Field | Critical? | Example |
|-------|-----------|---------|
| Product / offer | Yes | AI roleplay coaching for sales reps |
| Target audience | Yes | Sales managers at B2B SaaS companies |
| Goal | Yes | Awareness / demo sign-ups / feature launch / engagement |
| Platform | No (default: Instagram Reels + YouTube Shorts) | LinkedIn, TikTok |
| Length | No (default: 30–40s; aim for 35s) | Only change it if the user asked |
| Tone | No (default: from brand profile, else confident and friendly) | Funny, bold, premium |
| Call to action | No | "Book a demo", "Link in bio" |

### 2. Understand the audience
- Their top 3 **pain points** related to this product, in their own words.
- What they want instead (the desired outcome).
- What would make them stop scrolling, and what would make them scroll past.

### 3. Choose the angle
Pick **one** core message the viewer should remember. A reel with two messages gets neither across.

Pick the best format for the goal and justify it in one line:
- Problem → Solution
- Before / After
- "POV:" relatable scenario
- Myth vs. Fact
- Quick tips / listicle ("3 ways to ...")
- Behind the scenes / demo
- Customer story (only if real details are provided)

### 4. Write hooks
Write **5 hook options**, each one spoken or shown in the first 1–2 seconds. Mix these types:
- Pain call-out ("Your reps are losing deals in the first 30 seconds.")
- Curiosity gap ("Nobody tells new sales hires this.")
- Bold claim, backed by a fact from the brief
- Relatable POV
- Question

Mark the strongest one as **Recommended** and say why. The script uses the Recommended hook. Do not ask the user to choose.

### 5. Platform notes
For each target platform, give: ideal length, caption style, on-screen text rules, and 5–10 relevant hashtags. Note any platform differences (for example, LinkedIn favors a professional tone and text-heavy captions).

## Output
Write `01-strategy.md` in the run folder:

```markdown
# Strategy — <reel title>

## Brief
(table of fields, with assumptions marked)

## Audience
- Pain points:
- Desired outcome:
- Scroll-stoppers / scroll-past triggers:

## Core message
<one sentence>

## Format
<format> — <why>

## Hooks
1. ... ← Recommended (why)
2. ...

## Platform notes
...

## Open questions / placeholders
...
```
