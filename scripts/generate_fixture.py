#!/usr/bin/env python3
"""Generate deterministic contribution-shaped data for local testing only."""

from __future__ import annotations

import argparse
from datetime import date, timedelta
from pathlib import Path

MESSAGES = (
    "docs: add example",
    "feat: add snippet",
    "fix: correct typo",
    "refactor: tidy snippets",
    "test: extend coverage e",
)


def build_entries(count: int, start: date, weekdays_only: bool = False) -> list[str]:
    entries: list[str] = []
    entry_date = start
    while len(entries) < count:
        if weekdays_only and entry_date.weekday() >= 5:
            entry_date += timedelta(days=1)
            continue
        message = MESSAGES[len(entries) % len(MESSAGES)]
        entries.append(f"{entry_date.isoformat()} 12:00:00 +0000 - TEST FIXTURE ONLY — {message}")
        entry_date += timedelta(days=1)
    return entries


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate local test data; this does not create Git commits."
    )
    parser.add_argument("--count", type=int, default=10_000)
    parser.add_argument("--start", type=date.fromisoformat, default=date(2026, 1, 1))
    parser.add_argument("--weekdays-only", action="store_true")
    parser.add_argument("--output", type=Path, default=Path("tmp/contribution-fixture.md"))
    args = parser.parse_args()

    if args.count < 1:
        parser.error("--count must be at least 1")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "\n".join(build_entries(args.count, args.start, args.weekdays_only)) + "\n"
    )
    print(f"Wrote {args.count:,} test entries to {args.output}")


if __name__ == "__main__":
    main()