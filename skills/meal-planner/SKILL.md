# Meal Planner Skill

Use this skill when the user wants to:
- draft a weekly meal plan
- turn a meal plan into a grocery list
- figure out what to cook given current constraints
- simplify dinner on busy days

## Goal

Help the household eat well with less decision fatigue.

## Workflow

1. Write `PLAN.md` — your approach, meals you'll consider, constraints.
2. Write `TODO.md` — a checklist of steps. Check each off as you complete it.
3. Gather real data using tools:
   - `context` — household profile, budget, brands, dietary notes
   - `pantry` — owned staples (do NOT re-buy these)
   - `recipe <name>` — exact ingredients for a named family recipe
4. Check `resources/meal-plans/favorite-meals.md` for easy ideas.
5. Draft a 5–7 day meal plan. Prefer reusing ingredients across days.
6. Build the grocery list from the meal plan, minus pantry staples.
7. Group by category. Add price estimates.
8. Write output to `grocery-list.md`.

## Inputs

Useful context to gather or infer:

- dietary preferences and hard no's
- weekly budget
- busy nights (suggest simpler meals)
- leftovers preference
- pantry staples already on hand
- any family recipes requested

## Rules

- Prefer practical meals over aspirational ones.
- On chaotic days, simple dinners without shame.
- Respect allergies and the never_buy list.
- Keep shopping list grouped and easy to use in-store.
- Family recipe ingredients are authoritative — do not substitute.

## Output format (grocery-list.md)

```
## Meal Plan
Monday — [meal]
Tuesday — [meal]
...

## Grocery List
### Produce
- [ ] Item — quantity (~$price)

### Protein
...

### Dairy
...

### Pantry
...

### Other
...

## Estimated Total
$XX.XX
```
