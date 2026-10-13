---
name: setup-schedule
description: Register the daily 8 AM walmart-cart-fill scheduled task in the Claude desktop app for this clone of the repo. Use on a fresh clone, after moving the repo, or when the user says "set up the schedule".
---

# /setup-schedule

Registers the daily job that runs the `cart-fill` skill. Idempotent: re-running updates the existing task instead of creating a second one.

## Steps

1. Resolve the repo root as an absolute path (the directory containing this repo's `.claude/skills/cart-fill/SKILL.md`). Never `cd`. Confirm `<repo>/.claude/skills/cart-fill/SKILL.md` exists; if not, stop and say so.
2. Load the scheduled-task tools with one ToolSearch call:
   ```
   select:mcp__scheduled-tasks__list_scheduled_tasks,mcp__scheduled-tasks__create_scheduled_task,mcp__scheduled-tasks__update_scheduled_task
   ```
3. Call `list_scheduled_tasks`. If a task with id `walmart-cart-fill` exists, use `update_scheduled_task`; otherwise `create_scheduled_task`. Parameters, identical in both cases:
   - `taskId`: `walmart-cart-fill`
   - `title`: `Daily Walmart cart fill (8am)`
   - `description`: `Daily: run the repo's cart-fill skill to fill the Walmart cart from the Reminders Grocery list; ping only if cart > $45.`
   - `cronExpression`: `0 8 * * *`
   - `notifyOnCompletion`: `false`
   - `prompt`, with `<repo>` replaced by the absolute path from step 1:
     ```
     Read <repo>/.claude/skills/cart-fill/SKILL.md and follow it exactly, start to finish. That file is the full procedure for this job (read the Reminders Grocery list, fill the walmart.com cart via Claude in Chrome, mark items complete, write the run log, ping only if the cart total is over $45). If the file is missing, stop and send a PushNotification saying the cart-fill skill file was not found. Do not improvise steps that are not in the file.
     ```
4. Reply with: the task id, the schedule, the absolute path it points at, and this reminder: click "Run now" once in the Scheduled sidebar section while at the keyboard so browser permissions get approved and saved to the task.

## Notes

- The task runs only while the Claude desktop app is open. A missed 8 AM run fires on next launch.
- The model is set per project in `.claude/settings.json`; the task inherits it.
- The task file itself lives at `~/.claude/scheduled-tasks/walmart-cart-fill/SKILL.md`, outside the repo. The procedure it points at is versioned here.
