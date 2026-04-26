# HEARTBEAT.md

Periodic check for the meal planning agent.

## Weekly meal planning pulse

Run once at the start of each week:

- Check `resources/meal-plans/this-week.md` — is it empty or from a prior week?
- If so, prompt the user: "Ready to plan this week's meals?"
- Check `resources/shopping/groceries.md` — any carryover items?
- Summarize what's needed

## Mid-week check

- Scan the current meal plan for remaining days
- Note any gaps or days without a dinner assigned
- Flag if shopping list has unresolved items

## Quiet rule

If this-week.md is filled and no gaps exist, reply exactly:

HEARTBEAT_OK
