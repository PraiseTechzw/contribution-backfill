import unittest
from datetime import date
from pathlib import Path

from scripts.generate_fixture import ActivityBot


class GenerateCommitsTests(unittest.TestCase):
    def test_generates_requested_count_with_deterministic_seed(self) -> None:
        bot = ActivityBot(Path("."), seed=7, dry_run=True)

        stamps = bot.generate_commits(5, date(2026, 9, 22), weekdays_only=False)
        repeat = ActivityBot(Path("."), seed=7, dry_run=True).generate_commits(
            5, date(2026, 9, 22), weekdays_only=False
        )

        self.assertEqual(len(stamps), 5)
        self.assertEqual(stamps, repeat)

    def test_weekdays_only_skips_weekends(self) -> None:
        bot = ActivityBot(Path("."), seed=7, dry_run=True)

        stamps = bot.generate_commits(10, date(2026, 9, 26), weekdays_only=True)

        self.assertTrue(all(stamp.weekday() < 5 for stamp in stamps))


if __name__ == "__main__":
    unittest.main()
