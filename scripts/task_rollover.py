"""Pure rules for safely rolling daily Feishu tasks into a new day."""


class RolloverSafetyError(RuntimeError):
    """Raised when a task rollover cannot be performed safely."""


def record_message_outcomes(entry, completed_ids, skipped_ids):
    """Store user-reported outcomes on one daily-log entry."""
    outcomes = entry.setdefault('question_outcomes', {})

    for question_id in skipped_ids:
        if outcomes.get(question_id) != 'completed':
            outcomes[question_id] = 'skipped'
    for question_id in completed_ids:
        outcomes[question_id] = 'completed'


def resolve_previous_day(question_ids, task_guids, outcomes, get_status):
    """Classify yesterday's questions without making any external changes."""
    if len(question_ids) != len(task_guids):
        raise RolloverSafetyError('昨日题目与飞书任务数量不匹配')

    unfinished = []
    resolved = []

    for question_id, task_guid in zip(question_ids, task_guids):
        if not task_guid:
            raise RolloverSafetyError(f'题目 {question_id} 缺少飞书任务标识')

        if outcomes.get(question_id) in {'completed', 'skipped'}:
            resolved.append(question_id)
            continue

        try:
            status = get_status(task_guid)
        except Exception as error:
            raise RolloverSafetyError(f'无法查询飞书任务 {task_guid}') from error

        if status == 'done':
            resolved.append(question_id)
        elif status == 'todo':
            unfinished.append(question_id)
        else:
            raise RolloverSafetyError(
                f'飞书任务 {task_guid} 返回未知状态: {status}'
            )

    return unfinished, resolved, list(task_guids)


def fill_daily_slots(unfinished_ids, new_ids, daily_count):
    """Preserve unfinished questions and fill the remaining daily slots."""
    selected = list(unfinished_ids)

    for question_id in new_ids:
        if question_id not in selected:
            selected.append(question_id)
        if len(selected) == daily_count:
            break

    if len(selected) != daily_count:
        raise RolloverSafetyError('无法补足每日题目数量')

    return selected
