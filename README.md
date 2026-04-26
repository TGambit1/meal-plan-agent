# Meal Plan Agent

A Claude-powered household meal planning agent built on the OpenClaw workspace architecture. Give it a request in plain English and it produces a full weekly meal plan and grouped grocery list — priced, categorized, and within your household budget.

## How it works

The agent loads a workspace of markdown files (household profile, pantry staples, family recipes, preferences) and runs a single agentic loop. It reads real household data before generating anything, avoids re-buying pantry staples, respects preferred brands and dietary notes, and writes the output as a clean grocery list.

## Setup

```bash
git clone https://github.com/TGambit1/meal-plan-agent
cd meal-plan-agent
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...
```

For video recipe extraction, also install:

```bash
brew install yt-dlp ffmpeg
pip install openai-whisper
```

## Usage

```bash
# Generate a meal plan
python3 run.py 'Plan meals for the week'
python3 run.py 'Taco night, salmon, something easy Friday'
python3 run.py 'Quick weeknight dinners' --model claude-sonnet-4-6

# Save a recipe from a video
python3 run.py save-recipe https://www.instagram.com/reel/...
python3 run.py save-recipe https://www.tiktok.com/... "Chicken Tacos"
```

Output lands in `output/<timestamp>/grocery-list.md`. The current week's plan is also written back to `resources/meal-plans/this-week.md` and a daily memory log is saved to `memory/`.

## Workspace files

The agent's behavior is driven entirely by markdown files — edit these to tailor it to your household.

| File | What it controls |
|------|-----------------|
| `SOUL.md` | Agent persona and tone |
| `AGENTS.md` | Session rules and workflow |
| `USER.md` | Household preferences |
| `MEMORY.md` | Durable household context |
| `resources/household/profile.md` | Store, budget, brands, dietary notes |
| `resources/pantry/staples.md` | Items always on hand — never re-bought |
| `resources/recipes/book.md` | Family recipe book — authoritative ingredients |
| `resources/meal-plans/favorite-meals.md` | Easy ideas bank |
| `skills/meal-planner/SKILL.md` | Planning workflow and output format |
| `skills/save-recipe/SKILL.md` | Recipe extraction workflow |

## Project structure

```
meal-plan-agent/
├── SOUL.md                          # Persona and safety
├── AGENTS.md                        # Session instructions
├── USER.md                          # Household profile
├── TOOLS.md                         # Tools reference
├── HEARTBEAT.md                     # Periodic check
├── MEMORY.md                        # Long-term memory
├── memory/                          # Daily session logs
├── skills/
│   ├── meal-planner/SKILL.md
│   └── save-recipe/SKILL.md
├── resources/
│   ├── household/profile.md
│   ├── pantry/staples.md
│   ├── recipes/book.md
│   ├── meal-plans/
│   └── shopping/
├── tools/
│   ├── context                      # Read household profile
│   ├── pantry                       # Read pantry staples
│   ├── recipe                       # Look up a family recipe
│   └── save-recipe-video            # Extract recipe from video
├── agent.py                         # Agentic loop
└── run.py                           # Entry point
```

## Plugging into Homebaseuxv12

Add this repo as a git submodule in Homebaseuxv12 and create `grocery-meal-planner.tsx` in the Supabase edge function. The workspace files load into the Claude system prompt at runtime. `web-chat.tsx` already detects grocery intent and routes to `/make-server-8c22500c/meals/chat` — the submodule wires up that endpoint.

```bash
git submodule add https://github.com/TGambit1/meal-plan-agent meal-agent
supabase secrets set ANTHROPIC_API_KEY=sk-ant-...
```
