# Contribution Backfill

A small, deterministic dataset tool for testing contribution-calendar and streak calculations.

## What it does

The generator creates dated, contribution-shaped records for local parser and analytics tests. It does not create Git commits, rewrite history, or claim that test records are real activity.

## Quick start

```sh
python3 scripts/generate_fixture.py --count 10000 --output /tmp/contribution-fixture.md
python3 -m unittest discover -s tests -v
```

The default output is `tmp/contribution-fixture.md`. Keep generated fixtures out of Git unless a test explicitly needs a checked-in sample.

## Data format

Each line contains an ISO date, a UTC timestamp, a test-only marker, and a deterministic message:

```text
2026-01-01 12:00:00 +0000 - TEST FIXTURE ONLY — docs: add example
```

## Responsible use

Use this project to test date-gap handling, streak calculations, parser performance, and calendar visualizations. Real contribution history should come from useful work and truthful commits; this tool is not an activity-inflation mechanism.

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidance.
