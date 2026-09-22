import unittest
from datetime import date

from scripts.generate_fixture import build_entries


class BuildEntriesTests(unittest.TestCase):
    def test_generates_requested_count_and_consecutive_dates(self) -> None:
        entries = build_entries(3, date(2026, 1, 1))

        self.assertEqual(len(entries), 3)
        self.assertTrue(all("TEST FIXTURE ONLY" in entry for entry in entries))
        self.assertTrue(entries[0].startswith("2026-01-01"))
        self.assertTrue(entries[1].startswith("2026-01-02"))
        self.assertTrue(entries[2].startswith("2026-01-03"))

    def test_rejecting_zero_count_is_owned_by_cli(self) -> None:
        self.assertEqual(len(build_entries(0, date(2026, 1, 1))), 0)

    def test_weekdays_only_skips_weekends(self) -> None:
        entries = build_entries(3, date(2026, 1, 2), weekdays_only=True)

        self.assertTrue(entries[0].startswith("2026-01-02"))
        self.assertTrue(entries[1].startswith("2026-01-05"))
        self.assertTrue(entries[2].startswith("2026-01-06"))


if __name__ == "__main__":
    unittest.main()
