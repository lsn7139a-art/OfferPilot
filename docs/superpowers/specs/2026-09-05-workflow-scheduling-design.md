# Workflow Scheduling and Daily Task Rollover Design

## Goal

Make the scheduled Feishu push run once per intended time window and prevent concurrent runs from creating duplicate messages, tasks, or repository writes.

Keep exactly three current-day Feishu tasks: carry forward unfinished questions, replace yesterday's Feishu tasks, and fill any remaining slots with new questions.

## Scope

- Keep `daily-push.yml` as the only scheduled workflow.
- Schedule one daily push at `00:00 UTC` (08:00 Asia/Shanghai) and one evening reminder at `13:00 UTC` (21:00 Asia/Shanghai).
- Add one workflow-level concurrency group. A new trigger waits for an active run to finish rather than cancelling it.
- Remove `evening-reminder.yml`, which duplicates the 21:00 reminder.
- Retain `data/daily_log.json` only as internal task-rollover state; it is not user-facing history and does not change the question bank.

## Behavior

`daily-push.yml` continues to select `daily` or `evening` mode from `github.event.schedule`. Manual dispatch continues to run the daily push. The existing per-day persistence checks remain the final guard against duplicate Feishu messages.

The concurrency group prevents overlapping workflow runs from concurrently reading and committing `data/daily_log.json` and related progress files. `cancel-in-progress` remains false so an accepted run is allowed to complete its external Feishu side effects.

## Daily Task Rollover

At the morning run, the system reads the prior day's task record and determines the state of each of its three questions. A question is complete when either its Feishu task is marked complete or the user has sent a completion message for that numbered question. A user message such as `跳过第 2 题` marks that numbered question as skipped. A question with neither completion nor skip feedback is unfinished.

All three prior-day Feishu tasks are deleted after their statuses have been read. The system then creates exactly three new current-day tasks:

- unfinished questions are recreated as new tasks with today's deadline;
- completed and skipped questions are not recreated;
- new questions fill the remaining slots until the total is three.

For example, if yesterday's questions 1 and 3 are unfinished while question 2 is complete, today's three tasks are yesterday's questions 1 and 3 plus one new question. An unfinished question continues each day until it is completed or skipped.

The question bank itself is never changed by this process. `daily_log.json` records only enough internal state to match question numbers and Feishu task identifiers across the daily rollover; it can be redesigned separately later.

## Failure Safety

If the prior-day state cannot be read or its Feishu task statuses cannot be queried, the run stops before deleting or creating any task. This prevents an external API failure or corrupted state file from losing tasks or creating a duplicate set.

## Verification

- Parse the updated YAML with a YAML parser.
- Assert that the only scheduled workflow file is `daily-push.yml`.
- Assert exactly two cron expressions and that the conditions map them to daily and evening modes.
- Exercise the rollover rules for all-complete, all-unfinished, mixed, skipped, and unreadable-state cases without calling the Feishu API.
- Confirm the working tree only contains the intended workflow edits plus pre-existing unrelated files.
