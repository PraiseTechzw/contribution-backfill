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
    "test: extend coverage",
)


def build_entries(count: int, start: date) -> list[str]:
    entries: list[str] = []
    for index in range(count):
        entry_date = start + timedelta(days=index)
        message = MESSAGES[index % len(MESSAGES)]
        entries.append(
            f"{entry_date.isoformat()} 12:00:00 +0000 - TEST FIXTURE ONLY — {message}"
        )
    return entries


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate local test data; this does not create Git commits."
    )
    parser.add_argument("--count", type=int, default=10_000)
    parser.add_argument("--start", type=date.fromisoformat, default=date(2026, 1, 1))
    parser.add_argument("--output", type=Path, default=Path("tmp/contribution-fixture.md"))
    args = parser.parse_args()

    if args.count < 1:
        parser.error("--count must be at least 1")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(build_entries(args.count, args.start)) + "\n")
    print(f"Wrote {args.count:,} test entries to {args.output}")


if __name__ == "__main__":
    main()
