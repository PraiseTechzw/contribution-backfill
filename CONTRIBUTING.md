# Contributing

This repository contains dated notes used for contribution-history experiments.

## Local fixture data

Use `scripts/generate_fixture.py` when you need a large dataset for parser or streak calculations:

```sh
python3 scripts/generate_fixture.py --count 10000
```

The output is test data only. It is intentionally not a Git history generator and must not be used to misrepresent activity on a hosted service. The generated file goes under `tmp/`, which should remain untracked.

## Building a real streak

A genuine contribution streak comes from useful work completed over time. Good daily-sized contributions include:

- improving an example or explanation
- adding a focused test
- fixing a reproducible issue
- updating documentation when behavior changes
- reviewing or simplifying an existing snippet

Keep each change reviewable, use truthful commit messages, and do not rewrite history to fill missed dates. There is no need to force a daily contribution when there is no meaningful change to make.
