import os
import sys
import unittest


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from task_rollover import (
    RolloverSafetyError,
    fill_daily_slots,
    record_message_outcomes,
    resolve_previous_day,
)


class TaskRolloverTests(unittest.TestCase):
    def test_records_message_outcomes(self):
        entry = {}

        record_message_outcomes(entry, ['q-1'], ['q-2'])

        self.assertEqual(
            entry['question_outcomes'],
            {'q-1': 'completed', 'q-2': 'skipped'},
        )

    def test_completion_overrides_previous_skip(self):
        entry = {'question_outcomes': {'q-1': 'skipped'}}

        record_message_outcomes(entry, ['q-1'], [])

        self.assertEqual(entry['question_outcomes']['q-1'], 'completed')

    def test_mixed_states_keep_only_unfinished(self):
        unfinished, resolved, task_guids = resolve_previous_day(
            ['q-1', 'q-2', 'q-3'],
            ['g-1', 'g-2', 'g-3'],
            {'q-1': 'skipped'},
            lambda guid: {'g-2': 'todo', 'g-3': 'done'}[guid],
        )

        self.assertEqual(unfinished, ['q-2'])
        self.assertEqual(resolved, ['q-1', 'q-3'])
        self.assertEqual(task_guids, ['g-1', 'g-2', 'g-3'])

    def test_no_feedback_continues_all_todo_questions(self):
        unfinished, resolved, _ = resolve_previous_day(
            ['q-1', 'q-2', 'q-3'],
            ['g-1', 'g-2', 'g-3'],
            {},
            lambda _: 'todo',
        )

        self.assertEqual(unfinished, ['q-1', 'q-2', 'q-3'])
        self.assertEqual(resolved, [])

    def test_unknown_or_invalid_state_blocks_cleanup(self):
        with self.assertRaises(RolloverSafetyError):
            resolve_previous_day(['q-1'], ['g-1'], {}, lambda _: 'unknown')
        with self.assertRaises(RolloverSafetyError):
            resolve_previous_day(['q-1'], [], {}, lambda _: 'todo')

    def test_query_exception_blocks_rollover(self):
        def raise_offline(_):
            raise OSError('offline')

        with self.assertRaises(RolloverSafetyError):
            resolve_previous_day(['q-1'], ['g-1'], {}, raise_offline)

    def test_slot_filler_makes_exactly_three_without_duplicates(self):
        selected = fill_daily_slots(['q-1', 'q-3'], ['q-2', 'q-4'], 3)

        self.assertEqual(selected, ['q-1', 'q-3', 'q-2'])

    def test_skip_command_with_chinese_question_word_is_not_completion(self):
        from progress_sync import parse_progress_message

        actions = parse_progress_message('跳过第 2 题', [{"id": "q-1"}, {"id": "q-2"}])

        self.assertEqual(actions['skipped'], [2])
        self.assertEqual(actions['completed'], [])


if __name__ == '__main__':
    unittest.main()
