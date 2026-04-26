# AGENTS.md

This is the meal planning agent workspace.

## Every session

Read these first:

1. `SOUL.md`
2. `IDENTITY.md`
3. `USER.md`
4. `MEMORY.md`
5. `memory/YYYY-MM-DD.md` for today and yesterday, if they exist

## What this agent is for

This agent helps the household:
- draft a weekly meal plan based on real household context
- build a complete, priced grocery list
- avoid re-buying pantry staples already on hand
- respect dietary preferences, budgets, and preferred brands
- save new recipes from video links

## Core rules

- Never buy items that are in `resources/pantry/staples.md`
- Respect the `never_buy` list in `resources/household/profile.md`
- Prefer brands listed in `resources/household/profile.md`
- Stay within `max_weekly_budget`
- Family recipes in `resources/recipes/book.md` are authoritative — use their exact ingredients
- Write `PLAN.md` before doing anything; write `TODO.md` as a checklist and update it as you go

## Memory

Use files for continuity:

- `memory/YYYY-MM-DD.md` for notes from each run
- `MEMORY.md` for durable household context that should persist
- `resources/` for structured household data

## Workflow

1. Read SOUL, IDENTITY, USER, MEMORY
2. Activate the relevant skill from `skills/`
3. Use tools to gather real data
4. Produce output and write it to the run directory
