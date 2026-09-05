from pathlib import Path
import unittest


class WorkflowScheduleTests(unittest.TestCase):
    def test_single_workflow_has_two_schedules_and_concurrency(self):
        content = Path('.github/workflows/daily-push.yml').read_text(encoding='utf-8')

        self.assertEqual(content.count('- cron:'), 2)
        self.assertIn("- cron: '0 0 * * *'", content)
        self.assertIn("- cron: '0 13 * * *'", content)
        self.assertIn('group: feishu-daily-push', content)
        self.assertIn('cancel-in-progress: false', content)

    def test_duplicate_evening_workflow_is_removed(self):
        self.assertFalse(Path('.github/workflows/evening-reminder.yml').exists())


if __name__ == '__main__':
    unittest.main()
